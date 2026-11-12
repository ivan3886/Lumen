from typing import Optional, List
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Proveedor(Base):
    __tablename__ = "proveedor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cuit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relaciones
    productos: Mapped[List["Producto"]] = relationship(
        "Producto", secondary="producto_proveedor", back_populates="proveedores"
    )
    compras: Mapped[List["Compra"]] = relationship("Compra", back_populates="proveedor")