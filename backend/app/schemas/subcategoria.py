from typing import Optional
from pydantic import ConfigDict, BaseModel, Field

class SubcategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=50)
    descripcion: Optional[str] = None
    activo: bool = True

class SubcategoriaCreate(SubcategoriaBase):
    categoria_id: int

class SubcategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class SubcategoriaResponse(SubcategoriaBase):
    id: int
    categoria_id: int

    model_config = ConfigDict(from_attributes=True)
