from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import TipoMovimientoEnum

# Solo estos tipos se pueden cargar a mano. COMPRA y VENTA los genera el sistema
# al registrar una compra o una venta.
TIPOS_MANUALES = {
    TipoMovimientoEnum.MERMA,
    TipoMovimientoEnum.PERDIDA,
    TipoMovimientoEnum.AJUSTE_POSITIVO,
    TipoMovimientoEnum.AJUSTE_NEGATIVO,
}


class ItemMovimientoManual(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0, description="Siempre positiva: el signo lo define el tipo de movimiento")


class MovimientoManualCreate(BaseModel):
    tipo: TipoMovimientoEnum
    observaciones: str = Field(..., min_length=3, description="Motivo del movimiento (queda en el historial)")
    items: List[ItemMovimientoManual] = Field(..., min_length=1)

    @field_validator("tipo")
    @classmethod
    def tipo_debe_ser_manual(cls, v: TipoMovimientoEnum) -> TipoMovimientoEnum:
        if v not in TIPOS_MANUALES:
            validos = ", ".join(t.value for t in TIPOS_MANUALES)
            raise ValueError(f"Tipo no permitido para carga manual. Válidos: {validos}")
        return v


class MovimientoStockDetalleResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    stock_resultante: int

    model_config = ConfigDict(from_attributes=True)


class MovimientoStockResponse(BaseModel):
    id: int
    tipo: TipoMovimientoEnum
    usuario_id: int
    fecha: datetime
    observaciones: Optional[str]
    compra_id: Optional[int]
    venta_id: Optional[int]
    detalles: List[MovimientoStockDetalleResponse]

    model_config = ConfigDict(from_attributes=True)
