from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Remito(Base):
    __tablename__ = "remito"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    numero_remito: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    venta_id: Mapped[int] = mapped_column(ForeignKey("venta.id"), unique=True, nullable=False)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relaciones
    venta: Mapped["Venta"] = relationship("Venta", back_populates="remito")