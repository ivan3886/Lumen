from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Paginacion, get_db_session
from app.core.exceptions import ReglaNegocioError
from app.crud.cliente import cliente as crud_cliente
from app.crud.venta import CONSUMIDOR_FINAL
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse

router = APIRouter()


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(pag: Paginacion = Depends(), db: Session = Depends(get_db_session)):
    return crud_cliente.get_multi(db, skip=pag.skip, limit=pag.limit)


@router.post("/", response_model=ClienteResponse, status_code=201)
def crear_cliente(cliente_in: ClienteCreate, db: Session = Depends(get_db_session)):
    return crud_cliente.create(db, obj_in=cliente_in)


@router.patch("/{id}", response_model=ClienteResponse)
def actualizar_cliente(id: int, cliente_in: ClienteUpdate, db: Session = Depends(get_db_session)):
    db_obj = crud_cliente.get_or_404(db, id)
    if db_obj.nombre == CONSUMIDOR_FINAL:
        # Si se desactivara o renombrara, las ventas sin cliente dejarían de funcionar.
        raise ReglaNegocioError("El cliente 'CONSUMIDOR FINAL' no se puede modificar.", status_code=409)
    return crud_cliente.update(db, db_obj=db_obj, obj_in=cliente_in)
