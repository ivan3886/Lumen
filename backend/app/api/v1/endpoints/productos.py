from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_db_session, require_roles
from app.core.exceptions import ReglaNegocioError
from app.crud.producto import producto as crud_prod
from app.enums import RolEnum
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter()
solo_admin = [Depends(require_roles(RolEnum.ADMIN))]


@router.get("/", response_model=List[ProductoResponse])
def listar_productos(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_prod.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.post("/", response_model=ProductoResponse, status_code=201, dependencies=solo_admin)
def crear_producto(prod_in: ProductoCreate, db: Session = Depends(get_db_session)):
    if crud_prod.get_by_codigo_interno(db, codigo_interno=prod_in.codigo_interno):
        raise ReglaNegocioError("Ya existe un producto con ese código interno.", status_code=409)
    if prod_in.codigo_barras and crud_prod.get_by_codigo_barras(db, codigo_barras=prod_in.codigo_barras):
        raise ReglaNegocioError("Ya existe un producto con ese código de barras / ISBN.", status_code=409)
    return crud_prod.create(db, obj_in=prod_in)


@router.get("/{id}", response_model=ProductoResponse)
def obtener_producto(id: int, db: Session = Depends(get_db_session)):
    return crud_prod.get_or_404(db, id)


@router.patch("/{id}", response_model=ProductoResponse, dependencies=solo_admin)
def actualizar_producto(id: int, prod_in: ProductoUpdate, db: Session = Depends(get_db_session)):
    # El stock NO se edita acá (no está en ProductoUpdate): solo cambia con compras, ventas o ajustes.
    return crud_prod.update(db, db_obj=crud_prod.get_or_404(db, id), obj_in=prod_in)
