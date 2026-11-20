from typing import Generator

import jwt
from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.enums import RolEnum
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


class Paginacion:
    """Parámetros skip/limit con tope, para que nadie pida toda la tabla de una vez."""

    def __init__(self, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
        self.skip = skip
        self.limit = limit


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
) -> Usuario:
    credenciales_invalidas = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise credenciales_invalidas

    # Se consulta la base en cada request: si desactivás a un empleado o le cambiás
    # el rol, el cambio rige al instante (un token firmado no se puede "revocar").
    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise credenciales_invalidas
    return usuario


def require_roles(*roles: RolEnum):
    permitidos = {r.value for r in roles}

    def verificar(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in permitidos:
            raise HTTPException(status_code=403, detail="No tenés permisos para esta operación")
        return usuario

    return verificar
