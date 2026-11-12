from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.producto import producto as crud_prod
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter()

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_prod.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=ProductoResponse, status_code=201)
def crear_producto(prod_in: ProductoCreate, db: Session = Depends(get_db_session)):
    existing = crud_prod.get_by_codigo_interno(db, codigo_interno=prod_in.codigo_interno)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código interno.")
    return crud_prod.create(db, obj_in=prod_in)

@router.get("/{id}", response_model=ProductoResponse)
def obtener_producto(id: int, db: Session = Depends(get_db_session)):
    db_obj = crud_prod.get(db, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_obj