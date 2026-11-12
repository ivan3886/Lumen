from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class VentaDetalle(Base):
    __tablename__ = "venta_detalle"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("venta.id", ondelete="CASCADE"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    costo_historico: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Relaciones
    venta: Mapped["Venta"] = relationship("Venta", back_populates="detalles")
    producto: Mapped["Producto"] = relationship("Producto", back_populates="ventas_detalle")