from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from app.enums import MedioPagoEnum, EstadoVentaEnum

class VentaDetalleCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)

class VentaDetalleResponse(VentaDetalleCreate):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    costo_historico: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True

class RemitoResponse(BaseModel):
    id: int
    numero_remito: str
    fecha_emision: datetime

    class Config:
        from_attributes = True

class VentaCreate(BaseModel):
    cliente_id: int = 1  # Por defecto Consumidor Final (ID 1)
    medio_pago: MedioPagoEnum = MedioPagoEnum.EFECTIVO
    observaciones: Optional[str] = None
    detalles: List[VentaDetalleCreate]

class VentaUpdate(BaseModel):
    cliente_id: Optional[int] = None
    medio_pago: Optional[MedioPagoEnum] = None
    estado: Optional[EstadoVentaEnum] = None
    observaciones: Optional[str] = None

class VentaResponse(BaseModel):
    id: int
    cliente_id: int
    usuario_id: int
    fecha: datetime
    monto_total: Decimal
    medio_pago: MedioPagoEnum
    estado: EstadoVentaEnum
    observaciones: Optional[str]
    detalles: List[VentaDetalleResponse]
    remito: Optional[RemitoResponse] = None

    class Config:
        from_attributes = True