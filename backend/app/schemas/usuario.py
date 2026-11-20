from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import MAX_PASSWORD_BYTES
from app.enums import RolEnum


class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=50)
    usuario: str = Field(..., min_length=3, max_length=50)
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=10)
    rol: RolEnum = RolEnum.EMPLEADO

    @field_validator("password")
    @classmethod
    def password_no_supera_limite_bcrypt(cls, v: str) -> str:
        if len(v.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError("La contraseña no puede superar los 72 bytes")
        return v


class UsuarioResponse(UsuarioBase):
    id: int
    rol: RolEnum
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
