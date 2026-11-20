from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class CompraDetalleCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)
    costo_unitario: Decimal = Field(..., ge=0)

class CompraDetalleResponse(CompraDetalleCreate):
    id: int
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)

class CompraCreate(BaseModel):
    proveedor_id: int
    numero_comprobante: Optional[str] = Field(None, max_length=50)
    observaciones: Optional[str] = None
    detalles: List[CompraDetalleCreate] = Field(..., min_length=1)

class CompraUpdate(BaseModel):
    proveedor_id: Optional[int] = None
    numero_comprobante: Optional[str] = Field(None, max_length=50)
    observaciones: Optional[str] = None

class CompraResponse(BaseModel):
    id: int
    proveedor_id: int
    usuario_id: int
    numero_comprobante: Optional[str]
    fecha: datetime
    monto_total: Decimal
    observaciones: Optional[str]
    detalles: List[CompraDetalleResponse]

    model_config = ConfigDict(from_attributes=True)
