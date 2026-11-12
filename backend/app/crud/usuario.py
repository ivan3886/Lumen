from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import get_password_hash

class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioCreate]):
    def get_by_usuario(self, db: Session, usuario: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.usuario == usuario).first()

    def create(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        db_obj = Usuario(
            nombre=obj_in.nombre,
            usuario=obj_in.usuario,
            password_hash=get_password_hash(obj_in.password),
            activo=obj_in.activo
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

usuario = CRUDUsuario(Usuario)