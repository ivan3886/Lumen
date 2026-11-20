from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_db_session, require_roles
from app.crud.proveedor import proveedor as crud_prov
from app.enums import RolEnum
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse

router = APIRouter()
solo_admin = [Depends(require_roles(RolEnum.ADMIN))]


@router.get("/", response_model=List[ProveedorResponse])
def listar_proveedores(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_prov.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.post("/", response_model=ProveedorResponse, status_code=201, dependencies=solo_admin)
def crear_proveedor(prov_in: ProveedorCreate, db: Session = Depends(get_db_session)):
    return crud_prov.create(db, obj_in=prov_in)


@router.patch("/{id}", response_model=ProveedorResponse, dependencies=solo_admin)
def actualizar_proveedor(id: int, prov_in: ProveedorUpdate, db: Session = Depends(get_db_session)):
    return crud_prov.update(db, db_obj=crud_prov.get_or_404(db, id), obj_in=prov_in)
