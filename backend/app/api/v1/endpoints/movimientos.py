from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_roles
from app.crud.movimiento_stock import movimiento_stock as crud_mov
from app.enums import RolEnum
from app.models.usuario import Usuario
from app.schemas.movimiento_stock import MovimientoManualCreate, MovimientoStockResponse

router = APIRouter()


@router.post("/", response_model=MovimientoStockResponse, status_code=201)
def registrar_ajuste_stock(
    mov_in: MovimientoManualCreate,
    db: Session = Depends(get_db_session),
    actual: Usuario = Depends(require_roles(RolEnum.ADMIN)),
):
    return crud_mov.registrar_movimiento(
        db,
        tipo=mov_in.tipo,
        usuario_id=actual.id,
        items=[i.model_dump() for i in mov_in.items],
        observaciones=mov_in.observaciones,
    )
