from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.venta import Venta
from app.models.venta_detalle import VentaDetalle
from app.models.remito import Remito
from app.models.producto import Producto
from app.schemas.venta import VentaCreate, VentaUpdate

class CRUDVenta(CRUDBase[Venta, VentaCreate, VentaUpdate]):
    def create_venta_completa(self, db: Session, *, obj_in: VentaCreate, usuario_id: int) -> Venta:
        monto_total = 0
        detalles_data = []

        for item in obj_in.detalles:
            producto = db.get(Producto, item.producto_id)
            if not producto:
                raise ValueError(f"El producto con ID {item.producto_id} no existe.")
            if producto.stock_actual < item.cantidad:
                raise ValueError(f"Stock insuficiente para el producto: {producto.titulo}. Stock actual: {producto.stock_actual}")

            precio_unitario = producto.precio_venta
            costo_historico = producto.costo_actual
            subtotal = item.cantidad * precio_unitario
            monto_total += subtotal

            detalles_data.append({
                "producto_id": item.producto_id,
                "cantidad": item.cantidad,
                "precio_unitario": precio_unitario,
                "costo_historico": costo_historico,
                "subtotal": subtotal,
                "producto_obj": producto
            })

        # 1. Crear la Venta
        db_venta = Venta(
            cliente_id=obj_in.cliente_id,
            usuario_id=usuario_id,
            monto_total=monto_total,
            medio_pago=obj_in.medio_pago,
            observaciones=obj_in.observaciones
        )
        db.add(db_venta)
        db.flush()

        numero_remito_generado = f"REM-{db_venta.id:07d}"
        db_remito = Remito(
            numero_remito=numero_remito_generado,
            venta_id=db_venta.id
        )
        db.add(db_remito)

        for item in detalles_data:
            db_detalle = VentaDetalle(
                venta_id=db_venta.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                costo_historico=item["costo_historico"],
                subtotal=item["subtotal"]
            )
            db.add(db_detalle)

            prod = item["producto_obj"]
            prod.stock_actual -= item["cantidad"]
            db.add(prod)

        db.commit()
        db.refresh(db_venta)
        return db_venta

venta = CRUDVenta(Venta)