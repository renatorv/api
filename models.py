from datetime import datetime

from pydantic import BaseModel, Field


class Usuario(BaseModel):
    id: int
    login: str
    status: str = "A"
    senha: str = Field(..., max_length=12)
    data_cadastro: datetime = Field(default_factory=datetime.now)
