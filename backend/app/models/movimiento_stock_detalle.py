from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class MovimientoStockDetalle(Base):
    __tablename__ = "movimiento_stock_detalle"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movimiento_id: Mapped[int] = mapped_column(ForeignKey("movimiento_stock.id", ondelete="CASCADE"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)  # Positivo = entrada, Negativo = salida
    stock_resultante: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relaciones
    movimiento: Mapped["MovimientoStock"] = relationship("MovimientoStock", back_populates="detalles")
    producto: Mapped["Producto"] = relationship("Producto", back_populates="movimientos_detalle")