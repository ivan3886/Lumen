from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.movimiento_stock import MovimientoStock
from app.models.movimiento_stock_detalle import MovimientoStockDetalle
from app.enums import TipoMovimientoEnum

class CRUDMovimientoStock:
    def registrar_movimiento(
        self, 
        db: Session, 
        *, 
        tipo: TipoMovimientoEnum, 
        usuario_id: int, 
        items: list,  # Lista de diccionarios: [{"producto_id": int, "cantidad": int}] (positivo o negativo)
        observaciones: str = None,
        compra_id: int = None,
        venta_id: int = None
    ) -> MovimientoStock:
        
        db_mov = MovimientoStock(
            tipo=tipo,
            usuario_id=usuario_id,
            observaciones=observaciones,
            compra_id=compra_id,
            venta_id=venta_id
        )
        db.add(db_mov)
        db.flush()

        for item in items:
            producto_id = item["producto_id"]
            cantidad_cambio = item["cantidad"] # ej: +10 o -2

            producto = db.get(__import__('app.models.producto', fromlist=['Producto']).Producto, producto_id)
            if not producto:
                raise ValueError(f"Producto ID {producto_id} no encontrado.")

            producto.stock_actual += cantidad_cambio
            if producto.stock_actual < 0:
                raise ValueError(f"El stock resultante no puede ser negativo para el producto {producto.titulo}")

            db.add(producto)

            db_detalle = MovimientoStockDetalle(
                movimiento_id=db_mov.id,
                producto_id=producto_id,
                cantidad=cantidad_cambio,
                stock_resultante=producto.stock_actual
            )
            db.add(db_detalle)

        db.commit()
        db.refresh(db_mov)
        return db_mov

movimiento_stock = CRUDMovimientoStock()