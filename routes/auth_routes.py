from schemas import UserSchema
from fastapi import APIRouter, Depends, HTTPException

from database import get_session

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register_user(user: UserSchema, session = Depends(get_session)):
    """Cadastra um novo usuário para acesso ao sistema."""

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
        return {"mensagem": f"Usuário cadastrado com sucesso: {user.login}"}
