from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate

class CRUDProducto(CRUDBase[Producto, ProductoCreate, ProductoUpdate]):
    def get_by_codigo_interno(self, db: Session, codigo_interno: str) -> Optional[Producto]:
        return db.query(Producto).filter(Producto.codigo_interno == codigo_interno).first()

    def get_by_codigo_barras(self, db: Session, codigo_barras: str) -> Optional[Producto]:
        return db.query(Producto).filter(Producto.codigo_barras == codigo_barras).first()

producto = CRUDProducto(Producto)