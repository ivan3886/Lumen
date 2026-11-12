from fastapi import APIRouter
from app.api.v1.endpoints import (
    categorias, 
    subcategorias, 
    productos, 
    clientes, 
    proveedores, 
    compras, 
    ventas, 
    movimientos,
    usuarios
)

api_router = APIRouter()

api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["Categorías"])
api_router.include_router(subcategorias.router, prefix="/subcategorias", tags=["Subcategorías"])
api_router.include_router(productos.router, prefix="/productos", tags=["Productos"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(proveedores.router, prefix="/proveedores", tags=["Proveedores"])
api_router.include_router(compras.router, prefix="/compras", tags=["Compras"])
api_router.include_router(ventas.router, prefix="/ventas", tags=["Ventas"])
api_router.include_router(movimientos.router, prefix="/movimientos-stock", tags=["Movimientos de Stock"])