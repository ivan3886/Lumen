from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class CompraDetalle(Base):
    __tablename__ = "compra_detalle"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    compra_id: Mapped[int] = mapped_column(ForeignKey("compra.id", ondelete="CASCADE"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    costo_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Relaciones
    compra: Mapped["Compra"] = relationship("Compra", back_populates="detalles")
    producto: Mapped["Producto"] = relationship("Producto", back_populates="compras_detalle")