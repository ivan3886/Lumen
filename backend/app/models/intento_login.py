from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.clock import ahora_utc
from app.db.base import Base


class IntentoLogin(Base):
    """Un intento de iniciar sesión (exitoso o no), exista o no el usuario."""

    __tablename__ = "intento_login"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usuario: Mapped[str] = mapped_column(String(50), nullable=False)
    direccion_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    exitoso: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=ahora_utc)
