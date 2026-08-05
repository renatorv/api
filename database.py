import logging
import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

logger = logging.getLogger(__name__)


def _conexao_config():
    """Parâmetros de conexão lidos das variáveis de ambiente."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "capelania"),
        "user": os.getenv("DB_USER", "capelania"),
        "password": os.environ["DB_PASSWORD"],
    }


async def conectar():
    """Abre uma conexão avulsa com o banco (para scripts fora da API)."""
    return await asyncpg.connect(**_conexao_config())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria o pool de conexões ao subir a API e fecha no desligamento."""
    app.state.pool = await asyncpg.create_pool(
        **_conexao_config(),
        min_size=1,
        max_size=10,
    )
    try:
        yield
    finally:
        await app.state.pool.close()


async def get_session(request: Request):
    """Dependência do FastAPI: pega uma sessão do pool e devolve ao final."""
    pool = request.app.state.pool
    try:
        conn = await pool.acquire()
    except (asyncpg.PostgresError, OSError):
        logger.exception("Banco indisponível ao obter conexão do pool")
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível. Tente novamente em instantes.",
        )
    try:
        yield conn
    finally:
        await pool.release(conn)
