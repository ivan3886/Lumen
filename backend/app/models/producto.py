from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Text, Boolean, Numeric, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

# Tabla de asociación
producto_proveedor = Table(
    "producto_proveedor",
    Base.metadata,
    Column("producto_id", ForeignKey("producto.id", ondelete="CASCADE"), primary_key=True),
    Column("proveedor_id", ForeignKey("proveedor.id", ondelete="CASCADE"), primary_key=True),
)

class Producto(Base):
    __tablename__ = "producto"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_interno: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    codigo_barras: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    autor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    editorial: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categoria.id"), nullable=False)
    subcategoria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subcategoria.id"), nullable=True)

    costo_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    stock_actual: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relaciones
    categoria: Mapped["Categoria"] = relationship("Categoria", back_populates="productos")
    subcategoria: Mapped[Optional["Subcategoria"]] = relationship("Subcategoria", back_populates="productos")
    proveedores: Mapped[List["Proveedor"]] = relationship(
        "Proveedor", secondary=producto_proveedor, back_populates="productos"
    )
    compras_detalle: Mapped[List["CompraDetalle"]] = relationship("CompraDetalle", back_populates="producto")
    ventas_detalle: Mapped[List["VentaDetalle"]] = relationship("VentaDetalle", back_populates="producto")
    movimientos_detalle: Mapped[List["MovimientoStockDetalle"]] = relationship(
        "MovimientoStockDetalle", back_populates="producto"
    )