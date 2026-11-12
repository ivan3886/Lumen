from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.enums import MedioPagoEnum, EstadoVentaEnum

class Venta(Base):
    __tablename__ = "venta"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    medio_pago: Mapped[MedioPagoEnum] = mapped_column(
        SQLEnum(MedioPagoEnum, name="medio_pago"), default=MedioPagoEnum.EFECTIVO, nullable=False
    )
    estado: Mapped[EstadoVentaEnum] = mapped_column(
        SQLEnum(EstadoVentaEnum, name="estado_venta"), default=EstadoVentaEnum.COMPLETADA, nullable=False
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="ventas")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="ventas")
    detalles: Mapped[List["VentaDetalle"]] = relationship("VentaDetalle", back_populates="venta", cascade="all, delete-orphan")
    remito: Mapped[Optional["Remito"]] = relationship("Remito", back_populates="venta", uselist=False)