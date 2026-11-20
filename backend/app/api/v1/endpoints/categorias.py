from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_db_session, require_roles
from app.crud.categoria import categoria as crud_cat
from app.enums import RolEnum
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter()
solo_admin = [Depends(require_roles(RolEnum.ADMIN))]


@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_cat.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.post("/", response_model=CategoriaResponse, status_code=201, dependencies=solo_admin)
def crear_categoria(cat_in: CategoriaCreate, db: Session = Depends(get_db_session)):
    return crud_cat.create(db, obj_in=cat_in)


@router.get("/{id}", response_model=CategoriaResponse)
def obtener_categoria(id: int, db: Session = Depends(get_db_session)):
    return crud_cat.get_or_404(db, id)


@router.patch("/{id}", response_model=CategoriaResponse, dependencies=solo_admin)
def actualizar_categoria(id: int, cat_in: CategoriaUpdate, db: Session = Depends(get_db_session)):
    # Para "borrar" una categoría se envía {"activo": false}
    return crud_cat.update(db, db_obj=crud_cat.get_or_404(db, id), obj_in=cat_in)
