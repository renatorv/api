from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class Visita(BaseModel):
    id_usuario: int
    nome_visitado: str
    data_visita: datetime
    descricao: str
    visitar_novamente: Optional[bool] = None
    proxima_visita: Optional[datetime] = None
    motivo_proxima_visita: Optional[str] = None
    mostrar_app: bool
    telefone: str
    endereco: str
    data_cadastro: datetime = Field(default_factory=datetime.now)
