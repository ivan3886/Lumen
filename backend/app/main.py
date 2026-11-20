import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.v1.api import api_router
from app.core.exceptions import ReglaNegocioError

logger = logging.getLogger("lumen")

app = FastAPI(
    title="Lumen API",
    description="Sistema de gestión comercial e inventario para librerías",
    version="1.0.0",
)


@app.exception_handler(ReglaNegocioError)
async def regla_negocio_handler(request: Request, exc: ReglaNegocioError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})


@app.exception_handler(IntegrityError)
async def integridad_handler(request: Request, exc: IntegrityError):
    # El detalle técnico va al log del servidor, NO al cliente (podría revelar
    # nombres de tablas, columnas o restricciones a un atacante).
    logger.warning("IntegrityError: %s", exc.orig)
    return JSONResponse(
        status_code=409,
        content={"detail": "La operación viola una restricción de datos (valor duplicado o referencia inexistente)."},
    )


# Cualquier otro error inesperado devuelve un 500 genérico (FastAPI no expone el detalle).
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Bienvenido a Lumen API 🚀", "status": "activo"}
