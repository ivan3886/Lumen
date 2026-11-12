from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Subcategoria(Base):
    __tablename__ = "subcategoria"
    __table_args__ = (
        UniqueConstraint("categoria_id", "nombre", name="uq_subcategoria_categoria"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categoria.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relaciones
    categoria: Mapped["Categoria"] = relationship("Categoria", back_populates="subcategorias")
    productos: Mapped[List["Producto"]] = relationship("Producto", back_populates="subcategoria")