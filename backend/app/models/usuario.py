from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rol: Mapped[str] = mapped_column(String(50), default="empleado", nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relaciones
    compras: Mapped[List["Compra"]] = relationship("Compra", back_populates="usuario")
    ventas: Mapped[List["Venta"]] = relationship("Venta", back_populates="usuario")
    movimientos_stock: Mapped[List["MovimientoStock"]] = relationship("MovimientoStock", back_populates="usuario")
    auditorias: Mapped[List["Auditoria"]] = relationship("Auditoria", back_populates="usuario")