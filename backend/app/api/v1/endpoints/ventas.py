from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_current_user, get_db_session, require_roles
from app.crud.venta import venta as crud_venta
from app.enums import RolEnum
from app.models.usuario import Usuario
from app.schemas.venta import VentaCreate, VentaResponse

router = APIRouter()


@router.get("/", response_model=List[VentaResponse])
def listar_ventas(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_venta.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.get("/{id}", response_model=VentaResponse)
def obtener_venta(id: int, db: Session = Depends(get_db_session)):
    return crud_venta.get_or_404(db, id)


@router.post("/", response_model=VentaResponse, status_code=201)
def crear_venta(
    venta_in: VentaCreate,
    db: Session = Depends(get_db_session),
    actual: Usuario = Depends(get_current_user),
):
    return crud_venta.create_venta_completa(db, obj_in=venta_in, usuario_id=actual.id)


@router.post("/{id}/anular", response_model=VentaResponse)
def anular_venta(
    id: int,
    db: Session = Depends(get_db_session),
    actual: Usuario = Depends(require_roles(RolEnum.ADMIN)),
):
    return crud_venta.anular(db, venta_id=id, usuario_id=actual.id)
