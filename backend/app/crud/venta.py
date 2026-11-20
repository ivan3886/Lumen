from collections import defaultdict
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ReglaNegocioError
from app.core.money import redondear
from app.crud.base import CRUDBase
from app.crud.movimiento_stock import movimiento_stock as crud_movimiento
from app.enums import EstadoVentaEnum, TipoMovimientoEnum
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.remito import Remito
from app.models.venta import Venta
from app.models.venta_detalle import VentaDetalle
from app.schemas.venta import VentaCreate, VentaUpdate

CONSUMIDOR_FINAL = "CONSUMIDOR FINAL"


class CRUDVenta(CRUDBase[Venta, VentaCreate, VentaUpdate]):
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Venta]:
        stmt = (
            select(Venta)
            .options(selectinload(Venta.detalles), selectinload(Venta.remito))
            .order_by(Venta.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt))

    def _resolver_cliente(self, db: Session, cliente_id: Optional[int]) -> Cliente:
        if cliente_id is None:
            cliente = db.scalar(select(Cliente).where(Cliente.nombre == CONSUMIDOR_FINAL))
            if cliente is None:
                raise ReglaNegocioError(
                    "Falta el cliente 'CONSUMIDOR FINAL'. Ejecutá database/seed.sql.", status_code=500
                )
            return cliente
        cliente = db.get(Cliente, cliente_id)
        if cliente is None or not cliente.activo:
            raise ReglaNegocioError("Cliente no encontrado o inactivo.", status_code=404)
        return cliente

    def create_venta_completa(self, db: Session, *, obj_in: VentaCreate, usuario_id: int) -> Venta:
        try:
            cliente = self._resolver_cliente(db, obj_in.cliente_id)

            # Si el mismo libro viene en dos líneas, se suman las cantidades.
            cantidades: dict[int, int] = defaultdict(int)
            for item in obj_in.detalles:
                cantidades[item.producto_id] += item.cantidad

            # Se bloquean las filas de los productos (en orden de id) antes de leer precios.
            productos: dict[int, Producto] = {}
            for producto_id in sorted(cantidades):
                producto = db.scalar(
                    select(Producto).where(Producto.id == producto_id).with_for_update()
                )
                if producto is None or not producto.activo:
                    raise ReglaNegocioError(
                        f"El producto con ID {producto_id} no existe o está inactivo.", status_code=404
                    )
                productos[producto_id] = producto

            # El precio y el costo salen SIEMPRE de la base, nunca del cliente.
            monto_total = Decimal("0.00")
            lineas = []
            for producto_id, cantidad in cantidades.items():
                producto = productos[producto_id]
                subtotal = redondear(producto.precio_venta * cantidad)
                monto_total += subtotal
                lineas.append((producto, cantidad, subtotal))

            db_venta = Venta(
                cliente_id=cliente.id,
                usuario_id=usuario_id,
                monto_total=monto_total,
                medio_pago=obj_in.medio_pago,
                observaciones=obj_in.observaciones,
            )
            db.add(db_venta)
            db.flush()

            db.add(Remito(numero_remito=f"REM-{db_venta.id:07d}", venta_id=db_venta.id))
            for producto, cantidad, subtotal in lineas:
                db.add(
                    VentaDetalle(
                        venta_id=db_venta.id,
                        producto_id=producto.id,
                        cantidad=cantidad,
                        precio_unitario=producto.precio_venta,
                        costo_historico=producto.costo_actual,
                        subtotal=subtotal,
                    )
                )

            # El movimiento valida que haya stock y lo descuenta, dentro de ESTA transacción.
            crud_movimiento.registrar_movimiento(
                db,
                tipo=TipoMovimientoEnum.VENTA,
                usuario_id=usuario_id,
                items=[{"producto_id": pid, "cantidad": c} for pid, c in cantidades.items()],
                venta_id=db_venta.id,
                commit=False,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(db_venta)
        return db_venta

    def anular(self, db: Session, *, venta_id: int, usuario_id: int) -> Venta:
        try:
            # Se bloquea la venta: si dos personas la anulan a la vez, la segunda espera y ve "ya anulada".
            venta = db.scalar(select(Venta).where(Venta.id == venta_id).with_for_update())
            if venta is None:
                raise ReglaNegocioError("Venta no encontrada.", status_code=404)
            if venta.estado == EstadoVentaEnum.ANULADA:
                raise ReglaNegocioError("La venta ya está anulada.", status_code=409)

            crud_movimiento.registrar_movimiento(
                db,
                tipo=TipoMovimientoEnum.DEVOLUCION_CLIENTE,  # devuelve el stock
                usuario_id=usuario_id,
                items=[{"producto_id": d.producto_id, "cantidad": d.cantidad} for d in venta.detalles],
                observaciones=f"Anulación de la venta #{venta.id}",
                venta_id=venta.id,
                commit=False,
            )
            venta.estado = EstadoVentaEnum.ANULADA
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(venta)
        return venta


venta = CRUDVenta(Venta)
