from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.proveedor import proveedor as crud_prov
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse

router = APIRouter()

@router.get("/", response_model=List[ProveedorResponse])
def listar_proveedores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_prov.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=ProveedorResponse, status_code=201)
def crear_proveedor(prov_in: ProveedorCreate, db: Session = Depends(get_db_session)):
    return crud_prov.create(db, obj_in=prov_in)