from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.usuario import usuario as crud_usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

router = APIRouter()

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_usuario.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db_session)):
    existing = crud_usuario.get_by_usuario(db, usuario=usuario_in.usuario)
    if existing:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
    return crud_usuario.create(db, obj_in=usuario_in)