from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_roles
from app.api.v1.endpoints import (
    auth,
    categorias,
    subcategorias,
    productos,
    clientes,
    proveedores,
    compras,
    ventas,
    movimientos,
    usuarios,
)
from app.enums import RolEnum

api_router = APIRouter()

# Seguro por defecto: TODO requiere un usuario logueado, salvo el login.
# Dentro de cada archivo, las operaciones sensibles piden además rol admin.
logueado = [Depends(get_current_user)]
solo_admin = [Depends(require_roles(RolEnum.ADMIN))]

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"], dependencies=logueado)
api_router.include_router(categorias.router, prefix="/categorias", tags=["Categorías"], dependencies=logueado)
api_router.include_router(subcategorias.router, prefix="/subcategorias", tags=["Subcategorías"], dependencies=logueado)
api_router.include_router(productos.router, prefix="/productos", tags=["Productos"], dependencies=logueado)
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"], dependencies=logueado)
api_router.include_router(proveedores.router, prefix="/proveedores", tags=["Proveedores"], dependencies=logueado)
api_router.include_router(ventas.router, prefix="/ventas", tags=["Ventas"], dependencies=logueado)
# Compras y movimientos manuales de stock: solo administrador (manejan costos y ajustes)
api_router.include_router(compras.router, prefix="/compras", tags=["Compras"], dependencies=solo_admin)
api_router.include_router(movimientos.router, prefix="/movimientos-stock", tags=["Movimientos de Stock"], dependencies=solo_admin)
