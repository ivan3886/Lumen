from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.categoria import categoria as crud_cat
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter()

@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_cat.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=CategoriaResponse, status_code=201)
def crear_categoria(cat_in: CategoriaCreate, db: Session = Depends(get_db_session)):
    return crud_cat.create(db, obj_in=cat_in)

@router.get("/{id}", response_model=CategoriaResponse)
def obtener_categoria(id: int, db: Session = Depends(get_db_session)):
    db_obj = crud_cat.get(db, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_obj