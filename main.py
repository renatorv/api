from fastapi import FastAPI

from database import lifespan

app = FastAPI(lifespan=lifespan)

from routes.auth_routes import auth_router
from routes.visits_routes import visit_router

app.include_router(auth_router)
app.include_router(visit_router)