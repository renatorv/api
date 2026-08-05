from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class Visita(BaseModel):
    id_usuario: int
    nome_visitado: str
    data_visita: datetime
    descricao: str
    visitar_novamente: bool = False
    proxima_visita: Optional[datetime] = None
    motivo_proxima_visita: Optional[str] = None
    mostrar_app: bool
    telefone: str
    endereco: str
    status: str = "A"
    data_cadastro: datetime = Field(default_factory=datetime.now)
