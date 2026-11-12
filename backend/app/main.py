from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(
    title="Lumen API",
    description="Sistema de gestión comercial e inventario para librerías",
    version="1.0.0"
)

# Incluir las rutas de la API v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Bienvenido a Lumen API 🚀", "status": "activo"}