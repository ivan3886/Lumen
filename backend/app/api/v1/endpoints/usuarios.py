from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_current_user, get_db_session, require_roles
from app.core.exceptions import ReglaNegocioError
from app.crud.usuario import usuario as crud_usuario
from app.enums import RolEnum
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

router = APIRouter()
solo_admin = [Depends(require_roles(RolEnum.ADMIN))]


@router.get("/me", response_model=UsuarioResponse)
def mi_usuario(actual: Usuario = Depends(get_current_user)):
    return actual


@router.get("/", response_model=List[UsuarioResponse], dependencies=solo_admin)
def listar_usuarios(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_usuario.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.post("/", response_model=UsuarioResponse, status_code=201, dependencies=solo_admin)
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db_session)):
    if crud_usuario.get_by_usuario(db, usuario=usuario_in.usuario):
        raise ReglaNegocioError("El nombre de usuario ya está registrado.", status_code=409)
    return crud_usuario.create(db, obj_in=usuario_in)
