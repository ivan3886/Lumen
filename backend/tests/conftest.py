"""Fixtures compartidas por todos los tests.

SEGURIDAD: los tests BORRAN y recrean todas las tablas. Por eso se fuerza una base
distinta a la real (por defecto 'lumen_test') y se aborta si el nombre no termina en '_test'.
"""
import itertools
import os
from decimal import Decimal

# 1) La base de pruebas se fija ANTES de importar la app. Las variables de entorno
#    tienen prioridad sobre el .env, así que esto pisa el DB_NAME real.
os.environ["DB_NAME"] = os.environ.get("TEST_DB_NAME", "lumen_test")
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests-" + "x" * 40)

import bcrypt
import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.config import settings
from app.crud.usuario import usuario as crud_usuario
from app.db.database import SessionLocal, engine
from app.enums import RolEnum
from app.main import app
from app.models import Categoria, Producto, Proveedor
from app.schemas.usuario import UsuarioCreate
from tests.helpers import PASSWORD, RAIZ, bearer, config_alembic

# 2) Freno de seguridad: jamás correr contra una base que no sea de pruebas.
if not settings.DB_NAME.endswith("_test"):
    pytest.exit(
        f"ABORTADO: la base '{settings.DB_NAME}' no termina en '_test'. "
        "Los tests borran todas las tablas.",
        returncode=2,
    )

SQL_DIR = RAIZ / "database"

TABLAS = (
    "auditoria, movimiento_stock_detalle, movimiento_stock, remito, venta_detalle, venta, "
    "compra_detalle, compra, producto_proveedor, producto, subcategoria, categoria, "
    "proveedor, cliente, usuario, intento_login"
)


def _ejecutar_sql(sql: str) -> None:
    # Conexión "cruda" del driver: permite ejecutar un archivo .sql con varias sentencias.
    conexion = engine.raw_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql)
        conexion.commit()
    finally:
        conexion.close()


def _leer_sql(nombre: str) -> str:
    return (SQL_DIR / nombre).read_text(encoding="utf-8")


# --------------------------------------------------------------------------- base de datos
@pytest.fixture(scope="session", autouse=True)
def bcrypt_rapido():
    """bcrypt es lento a propósito (12 rondas). En tests usamos 4 para no esperar; en producción no cambia."""
    original = bcrypt.gensalt
    parche = pytest.MonkeyPatch()
    parche.setattr(bcrypt, "gensalt", lambda rounds=4, prefix=b"2b": original(rounds=rounds, prefix=prefix))
    yield
    parche.undo()


@pytest.fixture(scope="session", autouse=True)
def esquema():
    """Una vez por sesión: vacía la base de pruebas y la construye con las MIGRACIONES de Alembic.

    Así los tests ejercitan el mismo camino que una instalación nueva: si una migración
    está rota, los tests lo detectan.
    """
    _ejecutar_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    command.upgrade(config_alembic(), "head")
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def base_limpia(esquema):
    """Antes de CADA test: tablas vacías y datos iniciales. Así ningún test depende de otro."""  # noqa
    _ejecutar_sql(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE;")
    _ejecutar_sql(_leer_sql("seed.sql"))


@pytest.fixture
def db():
    with SessionLocal() as sesion:
        yield sesion


@pytest.fixture
def client():
    return TestClient(app)


# --------------------------------------------------------------------------- usuarios
@pytest.fixture
def nuevo_usuario(db):
    """Fábrica de usuarios (todos con la contraseña PASSWORD)."""

    def _crear(usuario: str, rol: RolEnum, activo: bool = True):
        return crud_usuario.create(
            db,
            obj_in=UsuarioCreate(
                nombre=usuario.capitalize(), usuario=usuario, password=PASSWORD, rol=rol, activo=activo
            ),
        )

    return _crear


@pytest.fixture
def admin(nuevo_usuario):
    return nuevo_usuario("admin_test", RolEnum.ADMIN)


@pytest.fixture
def empleado(nuevo_usuario):
    return nuevo_usuario("empleado_test", RolEnum.EMPLEADO)


@pytest.fixture
def login(client):
    def _login(usuario: str, password: str = PASSWORD):
        return client.post("/api/v1/auth/login", data={"username": usuario, "password": password})

    return _login


@pytest.fixture
def auth_admin(admin, login):
    return bearer(login("admin_test").json()["access_token"])


@pytest.fixture
def auth_empleado(empleado, login):
    return bearer(login("empleado_test").json()["access_token"])


# --------------------------------------------------------------------------- datos de negocio
@pytest.fixture
def crear_producto(db):
    """Fábrica de productos: devuelve el id. Inserta directo en la base (rápido y sin depender de la API)."""
    categoria = Categoria(nombre="General")
    db.add(categoria)
    db.commit()
    categoria_id = categoria.id
    numeros = itertools.count(1)

    def _crear(stock=10, precio="1000.00", costo="600.00", activo=True):
        n = next(numeros)
        producto = Producto(
            codigo_interno=f"P{n:04d}",
            titulo=f"Libro {n}",
            categoria_id=categoria_id,
            costo_actual=Decimal(costo),
            precio_venta=Decimal(precio),
            stock_actual=stock,
            activo=activo,
        )
        db.add(producto)
        db.commit()
        return producto.id

    return _crear


@pytest.fixture
def crear_proveedor(db):
    def _crear(nombre="Distribuidora de Prueba", activo=True):
        proveedor = Proveedor(nombre=nombre, activo=activo)
        db.add(proveedor)
        db.commit()
        return proveedor.id

    return _crear


@pytest.fixture
def stock_de(db):
    """Lee el stock directo de la base (consulta de columna: nunca devuelve un valor viejo en caché)."""

    def _stock(producto_id: int) -> int:
        return db.scalar(select(Producto.stock_actual).where(Producto.id == producto_id))

    return _stock


@pytest.fixture
def contar(db):
    def _contar(modelo) -> int:
        return db.scalar(select(func.count()).select_from(modelo))

    return _contar
