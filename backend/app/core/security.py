from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

MAX_PASSWORD_BYTES = 72  # límite propio del algoritmo bcrypt


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_PASSWORD_BYTES:
        # Antes se truncaba en silencio; ahora se rechaza de forma explícita.
        raise ValueError("La contraseña no puede superar los 72 bytes")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except ValueError:  # hash con formato inválido
        return False


# Hash "de mentira" para que el login tarde lo mismo exista o no el usuario
# (evita que un atacante descubra usuarios válidos midiendo tiempos de respuesta).
DUMMY_HASH = get_password_hash("contraseña-falsa-para-igualar-tiempos")


def create_access_token(subject: int | str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    # Lanza jwt.PyJWTError si el token es inválido, está alterado o expiró.
    return jwt.decode(
        token,
        settings.SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],  # lista fija: nunca aceptar el algoritmo que dice el token
        options={"require": ["exp", "sub"]},
    )
