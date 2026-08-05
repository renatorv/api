import logging
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg
from fastapi import HTTPException

logger = logging.getLogger(__name__)


@asynccontextmanager
async def handle_db_errors(
    action: str,
    *,
    unique_detail: Optional[str] = None,
    foreign_key_detail: Optional[str] = None,
    truncation_detail: str = "Algum campo excede o tamanho permitido.",
    catch_unexpected: bool = False,
):
    """Traduz exceções comuns de banco de dados em HTTPException.

    `action` descreve a operação no infinitivo (ex.: "cadastrar usuário") e é
    usado tanto nas mensagens de log quanto nas mensagens de erro padrão.
    """
    try:
        yield
    except HTTPException:
        raise
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail=unique_detail or "Registro já cadastrado.")
    except asyncpg.ForeignKeyViolationError:
        raise HTTPException(status_code=400, detail=foreign_key_detail or "Referência inválida.")
    except asyncpg.StringDataRightTruncationError:
        raise HTTPException(status_code=400, detail=truncation_detail)
    except asyncpg.NotNullViolationError as erro:
        raise HTTPException(
            status_code=400,
            detail=f"Campo obrigatório não informado: {erro.column_name}.",
        )
    except (asyncpg.PostgresConnectionError, OSError):
        logger.exception("Banco indisponível ao %s", action)
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível. Tente novamente em instantes.",
        )
    except asyncpg.PostgresError:
        logger.exception("Erro do banco ao %s", action)
        raise HTTPException(status_code=500, detail=f"Não foi possível {action}.")
    except Exception:
        if not catch_unexpected:
            raise
        logger.exception("Erro inesperado ao %s", action)
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado ao {action}.")
