from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.subcategoria import Subcategoria
from app.schemas.subcategoria import SubcategoriaCreate, SubcategoriaUpdate

class CRUDSubcategoria(CRUDBase[Subcategoria, SubcategoriaCreate, SubcategoriaUpdate]):
    def get_by_categoria(self, db: Session, categoria_id: int) -> List[Subcategoria]:
        return db.query(Subcategoria).filter(Subcategoria.categoria_id == categoria_id).all()

subcategoria = CRUDSubcategoria(Subcategoria)