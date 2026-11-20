from collections import defaultdict
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ReglaNegocioError
from app.core.money import redondear
from app.crud.base import CRUDBase
from app.crud.movimiento_stock import movimiento_stock as crud_movimiento
from app.enums import TipoMovimientoEnum
from app.models.compra import Compra
from app.models.compra_detalle import CompraDetalle
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.schemas.compra import CompraCreate, CompraUpdate


class CRUDCompra(CRUDBase[Compra, CompraCreate, CompraUpdate]):
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Compra]:
        # selectinload trae todos los detalles en UNA consulta extra (evita el problema N+1).
        stmt = (
            select(Compra)
            .options(selectinload(Compra.detalles))
            .order_by(Compra.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt))

    def create_with_detalles(self, db: Session, *, obj_in: CompraCreate, usuario_id: int) -> Compra:
        try:
            proveedor = db.get(Proveedor, obj_in.proveedor_id)
            if proveedor is None or not proveedor.activo:
                raise ReglaNegocioError("Proveedor no encontrado o inactivo.", status_code=404)

            productos: dict[int, Producto] = {}
            for producto_id in sorted({d.producto_id for d in obj_in.detalles}):
                producto = db.scalar(
                    select(Producto).where(Producto.id == producto_id).with_for_update()
                )
                if producto is None or not producto.activo:
                    raise ReglaNegocioError(
                        f"El producto con ID {producto_id} no existe o está inactivo.", status_code=404
                    )
                productos[producto_id] = producto

            subtotales = [redondear(d.cantidad * d.costo_unitario) for d in obj_in.detalles]

            db_compra = Compra(
                proveedor_id=obj_in.proveedor_id,
                usuario_id=usuario_id,
                numero_comprobante=obj_in.numero_comprobante,
                monto_total=sum(subtotales, Decimal("0.00")),
                observaciones=obj_in.observaciones,
            )
            db.add(db_compra)
            db.flush()  # obtiene el id SIN confirmar: si algo falla más abajo, no queda una compra a medias

            cantidades: dict[int, int] = defaultdict(int)
            for detalle, subtotal in zip(obj_in.detalles, subtotales):
                db.add(
                    CompraDetalle(
                        compra_id=db_compra.id,
                        producto_id=detalle.producto_id,
                        cantidad=detalle.cantidad,
                        costo_unitario=detalle.costo_unitario,
                        subtotal=subtotal,
                    )
                )
                # Decisión de negocio: el costo actual pasa a ser el de la última compra.
                # (Alternativa más precisa: costo promedio ponderado.)
                productos[detalle.producto_id].costo_actual = detalle.costo_unitario
                cantidades[detalle.producto_id] += detalle.cantidad

            # El stock NO se suma acá: lo hace el movimiento (una sola fuente de verdad).
            crud_movimiento.registrar_movimiento(
                db,
                tipo=TipoMovimientoEnum.COMPRA,
                usuario_id=usuario_id,
                items=[{"producto_id": pid, "cantidad": c} for pid, c in cantidades.items()],
                compra_id=db_compra.id,
                commit=False,
            )
            db.commit()  # único commit: compra + detalles + costos + stock + movimiento
        except Exception:
            db.rollback()
            raise

        db.refresh(db_compra)
        return db_compra


compra = CRUDCompra(Compra)
