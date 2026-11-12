from datetime import datetime
from typing import Optional, List
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.enums import TipoMovimientoEnum

class MovimientoStock(Base):
    __tablename__ = "movimiento_stock"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[TipoMovimientoEnum] = mapped_column(
        SQLEnum(TipoMovimientoEnum, name="tipo_movimiento"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    compra_id: Mapped[Optional[int]] = mapped_column(ForeignKey("compra.id"), nullable=True)
    venta_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venta.id"), nullable=True)

    # Relaciones
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="movimientos_stock")
    compra: Mapped[Optional["Compra"]] = relationship("Compra")
    venta: Mapped[Optional["Venta"]] = relationship("Venta")
    detalles: Mapped[List["MovimientoStockDetalle"]] = relationship(
        "MovimientoStockDetalle", back_populates="movimiento", cascade="all, delete-orphan"
    )