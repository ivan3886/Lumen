from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=50)
    usuario: str = Field(..., max_length=50)
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)

class UsuarioResponse(UsuarioBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True