import logging

from exceptions import handle_db_errors
from models import Visita
from schemas import VisitSchema
from database import get_session
from fastapi import Depends, HTTPException
from fastapi import APIRouter
from dependencies import verify_token

logger = logging.getLogger(__name__)

visit_router = APIRouter(prefix="/visit", tags=["Visitas"], dependencies=[Depends(verify_token)])


@visit_router.post("/register")
async def new_visit(visit: VisitSchema,  session = Depends(get_session)):
    """Cria uma nova visita."""
    new_visit = Visita(**visit.model_dump())

    async with handle_db_errors(
        "cadastrar a visita",
        foreign_key_detail=f"Usuário {new_visit.id_usuario} não encontrado.",
    ):
        async with session.transaction():
            visita_id = await session.fetchval(
                "INSERT INTO visitas (id_usuario, nome_visitado, data_visita, descricao, visitar_novamente, proxima_visita, motivo_proxima_visita, mostrar_app, telefone, endereco, status) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING id",
                new_visit.id_usuario, new_visit.nome_visitado, new_visit.data_visita,
                new_visit.descricao, new_visit.visitar_novamente, new_visit.proxima_visita,
                new_visit.motivo_proxima_visita, new_visit.mostrar_app, new_visit.telefone,
                new_visit.endereco, new_visit.status
            )

    logger.info("Visita %s cadastrada pelo usuário %s", visita_id, new_visit.id_usuario)
    return {"mensagem": "Visita cadastrada com sucesso!!", "id": visita_id}


@visit_router.post("/visit/cancel/{id_visita}")
async def cancel_visit(id_visita: int, session = Depends(get_session), usuario = Depends(verify_token)):
    """Cancela uma visita existente. Realiza um update e altera o status da visita para 'C'"""
    visit = await session.fetchrow("SELECT * FROM visitas WHERE id = $1", id_visita)
    if not visit:
        raise HTTPException(
            status_code=404,
            detail=f"Visita {id_visita} não encontrada.",
        )

    if visit["id_usuario"] != usuario["id"]:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para cancelar esta visita.",
        )

    async with handle_db_errors("cancelar a visita", catch_unexpected=True):
        async with session.transaction():
            await session.execute(
                "UPDATE visitas SET status = 'C' WHERE id = $1",
                id_visita,
            )
        return {"mensagem": "Visita cancelada com sucesso!!", "id": id_visita}