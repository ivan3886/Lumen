from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.enums import AccionAuditoriaEnum

class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    tabla: Mapped[str] = mapped_column(String(70), nullable=False)
    registro_id: Mapped[int] = mapped_column(nullable=False)
    accion: Mapped[AccionAuditoriaEnum] = mapped_column(
        SQLEnum(AccionAuditoriaEnum, name="accion_auditoria"), nullable=False
    )
    datos_anteriores: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    datos_nuevos: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    direccion_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    # Relaciones
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="auditorias")