from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.compra import compra as crud_compra
from app.schemas.compra import CompraCreate, CompraResponse

router = APIRouter()

@router.get("/", response_model=List[CompraResponse])
def listar_compras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_compra.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=CompraResponse, status_code=201)
def crear_compra(compra_in: CompraCreate, usuario_id: int = 1, db: Session = Depends(get_db_session)):
    try:
        return crud_compra.create_with_detalles(db, obj_in=compra_in, usuario_id=usuario_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))