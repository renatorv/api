import logging
import os

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from database import lifespan

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-form")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

from routes.auth_routes import auth_router
from routes.visits_routes import visit_router

app.include_router(auth_router)
app.include_router(visit_router)
