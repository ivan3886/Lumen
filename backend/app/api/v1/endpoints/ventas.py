from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.venta import venta as crud_venta
from app.schemas.venta import VentaCreate, VentaResponse

router = APIRouter()

@router.get("/", response_model=List[VentaResponse])
def listar_ventas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_venta.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=VentaResponse, status_code=201)
def crear_venta(venta_in: VentaCreate, usuario_id: int = 1, db: Session = Depends(get_db_session)):
    try:
        return crud_venta.create_venta_completa(db, obj_in=venta_in, usuario_id=usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))