from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db_session
from app.crud.subcategoria import subcategoria as crud_subcat
from app.schemas.subcategoria import SubcategoriaCreate, SubcategoriaUpdate, SubcategoriaResponse

router = APIRouter()

@router.get("/", response_model=List[SubcategoriaResponse])
def listar_subcategorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return crud_subcat.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=SubcategoriaResponse, status_code=201)
def crear_subcategoria(subcat_in: SubcategoriaCreate, db: Session = Depends(get_db_session)):
    return crud_subcat.create(db, obj_in=subcat_in)

@router.get("/categoria/{categoria_id}", response_model=List[SubcategoriaResponse])
def listar_por_categoria(categoria_id: int, db: Session = Depends(get_db_session)):
    return crud_subcat.get_by_categoria(db, categoria_id=categoria_id)