from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserSchema(BaseModel):
    login: str
    senha: str


class VisitSchema(BaseModel):
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

    @field_validator("proxima_visita", "motivo_proxima_visita", mode="before")
    @classmethod
    def vazio_para_nulo(cls, valor):
        """Trata string vazia enviada pelo formulario como ausencia de valor."""
        if isinstance(valor, str) and not valor.strip():
            return None
        return valor

    @field_validator("data_visita", "proxima_visita")
    @classmethod
    def remover_timezone(cls, valor: Optional[datetime]) -> Optional[datetime]:
        """Converte datas com timezone para o horario local, pois as colunas sao TIMESTAMP."""
        if valor is not None and valor.tzinfo is not None:
            return valor.astimezone().replace(tzinfo=None)
        return valor

