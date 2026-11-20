from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_db_session, require_roles
from app.crud.subcategoria import subcategoria as crud_subcat
from app.enums import RolEnum
from app.schemas.subcategoria import SubcategoriaCreate, SubcategoriaUpdate, SubcategoriaResponse

router = APIRouter()
solo_admin = [Depends(require_roles(RolEnum.ADMIN))]


@router.get("/", response_model=List[SubcategoriaResponse])
def listar_subcategorias(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_subcat.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.post("/", response_model=SubcategoriaResponse, status_code=201, dependencies=solo_admin)
def crear_subcategoria(subcat_in: SubcategoriaCreate, db: Session = Depends(get_db_session)):
    return crud_subcat.create(db, obj_in=subcat_in)


@router.get("/categoria/{categoria_id}", response_model=List[SubcategoriaResponse])
def listar_por_categoria(categoria_id: int, db: Session = Depends(get_db_session)):
    return crud_subcat.get_by_categoria(db, categoria_id=categoria_id)


@router.patch("/{id}", response_model=SubcategoriaResponse, dependencies=solo_admin)
def actualizar_subcategoria(id: int, subcat_in: SubcategoriaUpdate, db: Session = Depends(get_db_session)):
    return crud_subcat.update(db, db_obj=crud_subcat.get_or_404(db, id), obj_in=subcat_in)
