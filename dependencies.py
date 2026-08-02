from fastapi import Depends, HTTPException
from jose import JWTError, jwt

from database import get_session
from main import ALGORITHM, SECRET_KEY, oauth2_scheme


async def verify_token(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    """Dependência do FastAPI: valida o token de acesso e retorna o usuário autenticado."""

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = payload.get("sub")
    except JWTError as erro:
        print("Erro ao decodificar o token:", erro)
        raise HTTPException(status_code=401, detail="Token inválido ou expirado..")

    if id_usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado...")

    id_usuario = int(id_usuario)

    async with session.transaction():
        usuario = await session.fetchrow(
            "SELECT * from usuarios WHERE id = $1",
            id_usuario,
        )

    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    return usuario