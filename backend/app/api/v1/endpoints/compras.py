from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_db_session, require_roles
from app.crud.compra import compra as crud_compra
from app.enums import RolEnum
from app.models.usuario import Usuario
from app.schemas.compra import CompraCreate, CompraResponse

router = APIRouter()


@router.get("/", response_model=List[CompraResponse])
def listar_compras(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_compra.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.post("/", response_model=CompraResponse, status_code=201)
def crear_compra(
    compra_in: CompraCreate,
    db: Session = Depends(get_db_session),
    actual: Usuario = Depends(require_roles(RolEnum.ADMIN)),
):
    # El usuario sale del token, ya no se puede "elegir" desde el request.
    return crud_compra.create_with_detalles(db, obj_in=compra_in, usuario_id=actual.id)
