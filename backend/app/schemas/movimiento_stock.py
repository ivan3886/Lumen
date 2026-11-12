from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.enums import TipoMovimientoEnum

class MovimientoStockDetalleResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    stock_resultante: int

    class Config:
        from_attributes = True

class MovimientoStockResponse(BaseModel):
    id: int
    tipo: TipoMovimientoEnum
    usuario_id: int
    fecha: datetime
    observaciones: Optional[str]
    compra_id: Optional[int]
    venta_id: Optional[int]
    detalles: List[MovimientoStockDetalleResponse]

    class Config:
        from_attributes = True