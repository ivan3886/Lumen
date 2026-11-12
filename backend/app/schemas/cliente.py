from typing import Optional
from pydantic import BaseModel, Field

class ClienteBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    cuit: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    activo: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    cuit: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None

class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True