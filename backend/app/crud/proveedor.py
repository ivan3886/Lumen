from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.proveedor import Proveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate

class CRUDProveedor(CRUDBase[Proveedor, ProveedorCreate, ProveedorUpdate]):
    def get_by_nombre(self, db: Session, nombre: str) -> Optional[Proveedor]:
        return db.query(Proveedor).filter(Proveedor.nombre == nombre).first()

proveedor = CRUDProveedor(Proveedor)