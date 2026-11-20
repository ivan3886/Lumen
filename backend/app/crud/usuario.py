from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import DUMMY_HASH, get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioCreate]):
    def get_by_usuario(self, db: Session, usuario: str) -> Optional[Usuario]:
        return db.scalar(select(Usuario).where(Usuario.usuario == usuario))

    def create(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        db_obj = Usuario(
            nombre=obj_in.nombre,
            usuario=obj_in.usuario,
            password_hash=get_password_hash(obj_in.password),
            rol=obj_in.rol.value,
            activo=obj_in.activo,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, usuario: str, password: str) -> Optional[Usuario]:
        user = self.get_by_usuario(db, usuario)
        # Siempre se verifica un hash (el real o uno falso) para que el tiempo de
        # respuesta no revele si el usuario existe.
        password_ok = verify_password(password, user.password_hash if user else DUMMY_HASH)
        if user is None or not password_ok or not user.activo:
            return None
        return user


usuario = CRUDUsuario(Usuario)
