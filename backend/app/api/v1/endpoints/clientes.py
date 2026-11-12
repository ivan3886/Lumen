from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.cliente import cliente as crud_cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse

router = APIRouter()

@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_cliente.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=ClienteResponse, status_code=201)
def crear_cliente(cliente_in: ClienteCreate, db: Session = Depends(get_db_session)):
    return crud_cliente.create(db, obj_in=cliente_in)