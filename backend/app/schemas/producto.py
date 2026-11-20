from typing import Optional
from decimal import Decimal
from pydantic import ConfigDict, BaseModel, Field

class ProductoBase(BaseModel):
    codigo_interno: str = Field(..., max_length=30)
    codigo_barras: Optional[str] = Field(None, max_length=50)
    titulo: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    autor: Optional[str] = Field(None, max_length=100)
    editorial: Optional[str] = Field(None, max_length=100)
    categoria_id: int
    subcategoria_id: Optional[int] = None
    costo_actual: Decimal = Field(..., ge=0)
    precio_venta: Decimal = Field(..., ge=0)
    stock_minimo: int = Field(0, ge=0)
    activo: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    codigo_interno: Optional[str] = Field(None, max_length=30)
    codigo_barras: Optional[str] = Field(None, max_length=50)
    titulo: Optional[str] = Field(None, max_length=150)
    descripcion: Optional[str] = None
    autor: Optional[str] = Field(None, max_length=100)
    editorial: Optional[str] = Field(None, max_length=100)
    categoria_id: Optional[int] = None
    subcategoria_id: Optional[int] = None
    costo_actual: Optional[Decimal] = Field(None, ge=0)
    precio_venta: Optional[Decimal] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

class ProductoResponse(ProductoBase):
    id: int
    stock_actual: int

    model_config = ConfigDict(from_attributes=True)
