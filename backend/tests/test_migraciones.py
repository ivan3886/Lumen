"""Las migraciones de Alembic: estado coherente de la base de pruebas."""
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

from app.db.database import engine
from tests.helpers import config_alembic


def test_hay_una_sola_cabeza_de_migraciones():
    """Dos 'heads' significan que dos migraciones se crearon en paralelo y hay que unirlas."""
    cabezas = ScriptDirectory.from_config(config_alembic()).get_heads()
    assert len(cabezas) == 1


def test_la_base_esta_en_la_ultima_migracion(db):
    cabeza = ScriptDirectory.from_config(config_alembic()).get_current_head()
    actual = db.scalar(text("SELECT version_num FROM alembic_version"))
    assert actual == cabeza


def test_las_migraciones_crean_todas_las_tablas():
    tablas = set(inspect(engine).get_table_names())
    esperadas = {
        "usuario", "cliente", "categoria", "subcategoria", "proveedor", "producto",
        "producto_proveedor", "compra", "compra_detalle", "venta", "venta_detalle",
        "remito", "movimiento_stock", "movimiento_stock_detalle", "auditoria",
        "intento_login", "alembic_version",
    }
    assert esperadas <= tablas, f"Faltan tablas: {esperadas - tablas}"
