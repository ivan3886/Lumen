from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Compra(Base):
    __tablename__ = "compra"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedor.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    numero_comprobante: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    proveedor: Mapped["Proveedor"] = relationship("Proveedor", back_populates="compras")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="compras")
    detalles: Mapped[List["CompraDetalle"]] = relationship("CompraDetalle", back_populates="compra", cascade="all, delete-orphan")