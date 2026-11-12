from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.compra import Compra
from app.models.compra_detalle import CompraDetalle
from app.models.producto import Producto
from app.schemas.compra import CompraCreate, CompraUpdate

class CRUDCompra(CRUDBase[Compra, CompraCreate, CompraUpdate]):
    def create_with_detalles(self, db: Session, *, obj_in: CompraCreate, usuario_id: int) -> Compra:
        monto_total = sum(det.cantidad * det.costo_unitario for det in obj_in.detalles)
        
        db_compra = Compra(
            proveedor_id=obj_in.proveedor_id,
            usuario_id=usuario_id,
            numero_comprobante=obj_in.numero_comprobante,
            monto_total=monto_total,
            observaciones=obj_in.observaciones
        )
        db.add(db_compra)
        db.commit()
        db.refresh(db_compra)

        # 3. Crear los detalles y ACTUALIZAR EL STOCK DEL PRODUCTO
        for detalle_in in obj_in.detalles:
            subtotal = detalle_in.cantidad * detalle_in.costo_unitario
            
            db_detalle = CompraDetalle(
                compra_id=db_compra.id,
                producto_id=detalle_in.producto_id,
                cantidad=detalle_in.cantidad,
                costo_unitario=detalle_in.costo_unitario,
                subtotal=subtotal
            )
            db.add(db_detalle)

            # --- ¡ESTO ES LO QUE FALTABA ACTUALIZAR! ---
            producto = db.query(Producto).filter(Producto.id == detalle_in.producto_id).first()
            if producto:
                producto.stock_actual += detalle_in.cantidad
                # Opcional: actualizar el costo actual del producto si cambió
                producto.costo_actual = detalle_in.costo_unitario
                db.add(producto)

        db.commit()
        db.refresh(db_compra)
        return db_compra

compra = CRUDCompra(Compra)