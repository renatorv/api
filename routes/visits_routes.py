from fastapi import APIRouter

visit_router = APIRouter(prefix="/visit", tags=["Visitas"])

@visit_router.get("/")
async def visitas():
    return {"mensagem":"Você acessou a rota de visitas..."}
