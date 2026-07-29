from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def autenticar():
    """Essa é rota padrão de autenticação"""
    return {"mensagem":"Você acessou a rota de autenticacoa", "autenticado": False}