from collections import defaultdict
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ReglaNegocioError
from app.enums import TipoMovimientoEnum
from app.models.movimiento_stock import MovimientoStock
from app.models.movimiento_stock_detalle import MovimientoStockDetalle
from app.models.producto import Producto

# El TIPO decide si el stock sube (+1) o baja (-1). Así nadie puede cargar una
# "MERMA" que sume stock por error de signo.
SIGNO_POR_TIPO = {
    TipoMovimientoEnum.COMPRA: 1,
    TipoMovimientoEnum.VENTA: -1,
    TipoMovimientoEnum.MERMA: -1,
    TipoMovimientoEnum.PERDIDA: -1,
    TipoMovimientoEnum.AJUSTE_POSITIVO: 1,
    TipoMovimientoEnum.AJUSTE_NEGATIVO: -1,
    TipoMovimientoEnum.DEVOLUCION_CLIENTE: 1,
    TipoMovimientoEnum.DEVOLUCION_PROVEEDOR: -1,
}


class CRUDMovimientoStock:
    def registrar_movimiento(
        self,
        db: Session,
        *,
        tipo: TipoMovimientoEnum,
        usuario_id: int,
        items: List[dict],  # [{"producto_id": int, "cantidad": int}], cantidad SIEMPRE positiva
        observaciones: Optional[str] = None,
        compra_id: Optional[int] = None,
        venta_id: Optional[int] = None,
        commit: bool = True,
    ) -> MovimientoStock:
        """Es el ÚNICO lugar del sistema donde cambia el stock.

        commit=False lo usan ventas y compras: el movimiento se une a SU transacción,
        de modo que todo se guarda junto o nada se guarda.
        """
        if not items:
            raise ReglaNegocioError("El movimiento debe incluir al menos un producto.")

        cantidades: dict[int, int] = defaultdict(int)
        for item in items:
            if item["cantidad"] <= 0:
                raise ReglaNegocioError("Las cantidades deben ser mayores a cero.")
            cantidades[item["producto_id"]] += item["cantidad"]

        signo = SIGNO_POR_TIPO[tipo]
        try:
            db_mov = MovimientoStock(
                tipo=tipo,
                usuario_id=usuario_id,
                observaciones=observaciones,
                compra_id=compra_id,
                venta_id=venta_id,
            )
            db.add(db_mov)
            db.flush()  # obtiene db_mov.id sin cerrar la transacción

            # Se recorren los productos ordenados por id: si dos operaciones bloquean
            # los mismos productos siempre en el mismo orden, no se traban entre sí (deadlock).
            for producto_id in sorted(cantidades):
                # with_for_update = SELECT ... FOR UPDATE: bloquea la fila hasta el commit.
                # Otra venta del mismo libro espera y recién ahí lee el stock ya descontado.
                producto = db.scalar(
                    select(Producto).where(Producto.id == producto_id).with_for_update()
                )
                if producto is None:
                    raise ReglaNegocioError(f"Producto ID {producto_id} no encontrado.", status_code=404)

                cambio = signo * cantidades[producto_id]
                nuevo_stock = producto.stock_actual + cambio
                if nuevo_stock < 0:
                    raise ReglaNegocioError(
                        f"Stock insuficiente para '{producto.titulo}'. Disponible: {producto.stock_actual}.",
                        status_code=409,
                    )

                producto.stock_actual = nuevo_stock
                db.add(
                    MovimientoStockDetalle(
                        movimiento_id=db_mov.id,
                        producto_id=producto_id,
                        cantidad=cambio,
                        stock_resultante=nuevo_stock,
                    )
                )

            if commit:
                db.commit()
                db.refresh(db_mov)
            else:
                db.flush()
            return db_mov
        except Exception:
            db.rollback()
            raise


movimiento_stock = CRUDMovimientoStock()
