import logging

import asyncpg
import bcrypt
from dependencies import verify_token
from main import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from schemas import LoginSchema, UserSchema
from fastapi import APIRouter, Depends, HTTPException

from database import get_session
from security import gerar_hash_senha

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def generate_token(id_usuario, token_duration=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """Gera um token de acesso para o usuário autenticado."""
    """JWT => vai conter id_usuario, data de expiração"""
    data_expiracao = datetime.now(timezone.utc) + token_duration
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}

    try:
        encoded_jwt = jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError:
        logger.exception("Erro ao gerar token de acesso")
        raise HTTPException(status_code=500, detail="Erro ao gerar token de acesso.")

    return encoded_jwt


async def auth_user(login, senha, session):
    """Autentica um usuário e retorna seu ID se válido, caso contrário retorna False."""
    try:
        async with session.transaction():
            usuario = await session.fetchrow(
                "SELECT * from usuarios WHERE login = $1",
                login,
            )

            if not usuario:
                return False
            try:
                if not bcrypt.checkpw(senha.encode("utf-8"), usuario["senha"].encode("utf-8")):
                    return False
            except ValueError:
                logger.exception("Hash de senha inválido para o usuário %s", login)
                return False
            return usuario
    except (asyncpg.PostgresConnectionError, OSError):
        logger.exception("Banco indisponível ao autenticar usuário")
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível. Tente novamente em instantes.",
        )
    except asyncpg.PostgresError:
        logger.exception("Erro do banco ao autenticar usuário")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível autenticar o usuário.",
        )


@auth_router.post("/login")
async def login_user(login_schema: LoginSchema, session = Depends(get_session)):
    """Autentica um usuário e retorna um token de acesso."""

    existe = await auth_user(login_schema.login, login_schema.senha, session)

    async with session.transaction():
        if not existe:
            raise HTTPException(status_code=401, detail="Usuário não encontrado ou credenciais inválidas.")
        else:
            
            access_token = generate_token(existe["id"])
            refresh_token = generate_token(existe["id"], token_duration=timedelta(days=7))  # Token de atualização válido por 7 dias
            
            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}


@auth_router.post("/register")
async def register_user(user: UserSchema, session = Depends(get_session)):
    """Cadastra um novo usuário para acesso ao sistema."""

    try:
        senha_criptografada = gerar_hash_senha(user.senha)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))

    try:
        async with session.transaction():
            existe = await session.fetchval(
                "SELECT id FROM usuarios WHERE login = $1",
                user.login,
            )
            if existe:
                raise HTTPException(status_code=400, detail="Usuário já cadastrado.")

            await session.execute(
                "INSERT INTO usuarios (login, senha) VALUES ($1, $2)",
                user.login,
                senha_criptografada,
            )
    except HTTPException:
        raise
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")
    except asyncpg.StringDataRightTruncationError:
        raise HTTPException(
            status_code=400,
            detail="Login deve ter no máximo 20 caracteres.",
        )
    except asyncpg.NotNullViolationError as erro:
        raise HTTPException(
            status_code=400,
            detail=f"Campo obrigatório não informado: {erro.column_name}.",
        )
    except (asyncpg.PostgresConnectionError, OSError):
        logger.exception("Banco indisponível ao cadastrar usuário")
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível. Tente novamente em instantes.",
        )
    except asyncpg.PostgresError:
        logger.exception("Erro do banco ao cadastrar usuário")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível cadastrar o usuário.",
        )

    logger.info("Usuário %s cadastrado", user.login)
    return {"mensagem": f"Usuário cadastrado com sucesso: {user.login}"}


@auth_router.get("/refresh")
async def use_refresh_token(usuario = Depends(verify_token)):
    """Gera um novo token de acesso ao sistema usando um token de atualização válido."""
    access_token = generate_token(usuario["id"])

    return {"access_token": access_token, "token_type": "Bearer"}
