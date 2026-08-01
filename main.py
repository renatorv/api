import logging

from fastapi import FastAPI

from database import lifespan

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(lifespan=lifespan)

from routes.auth_routes import auth_router
from routes.visits_routes import visit_router

app.include_router(auth_router)
app.include_router(visit_router)