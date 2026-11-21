from decimal import Decimal
from pathlib import Path

from alembic.config import Config

PASSWORD = "contraseña-de-prueba-123"


def dec(valor) -> Decimal:
    """Convierte lo que devuelve la API (texto o número) a Decimal.

    Con dinero se compara con Decimal, nunca con float: 0.1 + 0.2 != 0.3 en float.
    """
    return Decimal(str(valor))


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


RAIZ = Path(__file__).resolve().parent.parent  # carpeta backend/


def config_alembic() -> Config:
    cfg = Config(str(RAIZ / "alembic.ini"))
    cfg.set_main_option("script_location", str(RAIZ / "migrations"))
    return cfg
