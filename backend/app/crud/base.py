from typing import Generic, Type, TypeVar, List, Optional, Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ReglaNegocioError
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_or_404(self, db: Session, id: Any) -> ModelType:
        obj = db.get(self.model, id)
        if obj is None:
            raise ReglaNegocioError(f"{self.model.__name__} no encontrado", status_code=404)
        return obj

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        # order_by es necesario: sin orden, la paginación puede repetir o saltear filas.
        stmt = select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        return list(db.scalars(stmt))

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)  # solo los campos que el cliente envió

        columnas = self.model.__table__.columns
        for campo, valor in update_data.items():
            if campo in columnas:
                setattr(db_obj, campo, valor)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    # No hay remove(): no se borran registros de un sistema comercial, se desactivan
    # (activo = False) para no perder el historial de ventas y compras.
