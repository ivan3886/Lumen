from datetime import datetime
from typing import Optional, Any
from pydantic import ConfigDict, BaseModel
from app.enums import AccionAuditoriaEnum

class AuditoriaResponse(BaseModel):
    id: int
    fecha: datetime
    usuario_id: int
    tabla: str
    registro_id: int
    accion: AccionAuditoriaEnum
    datos_anteriores: Optional[Any]
    datos_nuevos: Optional[Any]
    direccion_ip: Optional[str]

    model_config = ConfigDict(from_attributes=True)
