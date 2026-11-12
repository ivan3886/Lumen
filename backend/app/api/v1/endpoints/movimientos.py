from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from app.api.deps import get_db_session
from app.crud.movimiento_stock import movimiento_stock as crud_mov
from app.enums import TipoMovimientoEnum

router = APIRouter()

class ItemMovimientoManual(BaseModel):
    producto_id: int
    cantidad: int = Field(..., description="Positivo para entradas, negativo para mermas/salidas")

class MovimientoManualCreate(BaseModel):
    tipo: TipoMovimientoEnum  # MERMA, PERDIDA, AJUSTE_POSITIVO, AJUSTE_NEGATIVO
    usuario_id: int
    observaciones: str = None
    items: List[ItemMovimientoManual]

@router.post("/", status_code=201)
def registrar_ajuste_stock(mov_in: MovimientoManualCreate, db: Session = Depends(get_db_session)):
    try:
        items_dict = [{"producto_id": i.producto_id, "cantidad": i.cantidad} for i in mov_in.items]
        movimiento = crud_mov.registrar_movimiento(
            db,
            tipo=mov_in.tipo,
            usuario_id=mov_in.usuario_id,
            items=items_dict,
            observaciones=mov_in.observaciones
        )
        return {"message": "Movimiento de stock registrado con éxito", "movimiento_id": movimiento.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))