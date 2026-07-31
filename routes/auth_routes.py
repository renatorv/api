import logging

import asyncpg
from schemas import UserSchema
from fastapi import APIRouter, Depends, HTTPException

from database import get_session

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register_user(user: UserSchema, session = Depends(get_session)):
    """Cadastra um novo usuário para acesso ao sistema."""

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
                user.senha,
            )
    except HTTPException:
        raise
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")
    except asyncpg.StringDataRightTruncationError:
        raise HTTPException(
            status_code=400,
            detail="Login e senha devem ter no máximo 20 caracteres.",
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
