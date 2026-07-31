import logging

import asyncpg
from models import Visita
from schemas import VisitSchema
from database import get_session
from fastapi import Depends, HTTPException
from fastapi import APIRouter

logger = logging.getLogger(__name__)

visit_router = APIRouter(prefix="/visit", tags=["Visitas"])


@visit_router.post("/register")
async def new_visit(visit: VisitSchema,  session = Depends(get_session)):
    """Cria uma nova visita."""
    new_visit = Visita(**visit.model_dump())

    try:
        async with session.transaction():
            visita_id = await session.fetchval(
                "INSERT INTO visitas (id_usuario, nome_visitado, data_visita, descricao, visitar_novamente, proxima_visita, motivo_proxima_visita, mostrar_app, telefone, endereco) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id",
                new_visit.id_usuario, new_visit.nome_visitado, new_visit.data_visita,
                new_visit.descricao, new_visit.visitar_novamente, new_visit.proxima_visita,
                new_visit.motivo_proxima_visita, new_visit.mostrar_app, new_visit.telefone,
                new_visit.endereco
            )
    except asyncpg.ForeignKeyViolationError:
        raise HTTPException(
            status_code=400,
            detail=f"Usuário {new_visit.id_usuario} não encontrado.",
        )
    except asyncpg.StringDataRightTruncationError:
        raise HTTPException(
            status_code=400,
            detail="Algum campo excede o tamanho permitido.",
        )
    except asyncpg.NotNullViolationError as erro:
        raise HTTPException(
            status_code=400,
            detail=f"Campo obrigatório não informado: {erro.column_name}.",
        )
    except (asyncpg.PostgresConnectionError, OSError):
        logger.exception("Banco indisponível ao cadastrar visita")
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível. Tente novamente em instantes.",
        )
    except asyncpg.PostgresError:
        logger.exception("Erro do banco ao cadastrar visita")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível cadastrar a visita.",
        )

    logger.info("Visita %s cadastrada pelo usuário %s", visita_id, new_visit.id_usuario)
    return {"mensagem": "Visita cadastrada com sucesso!!", "id": visita_id}
