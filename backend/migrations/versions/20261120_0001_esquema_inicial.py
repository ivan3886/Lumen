"""Esquema inicial

Crea todo el esquema de Lumen en una base VACÍA. En una base que ya existe (como la tuya)
NO se ejecuta: se la marca como "ya aplicada" con `alembic stamp head`.

Revision ID: 0001
Revises:
Create Date: 2026-11-20
"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SQL_INICIAL = Path(__file__).resolve().parent.parent / "sql" / "0001_esquema_inicial.sql"


def upgrade() -> None:
    # Se usa el cursor del driver porque el archivo tiene muchas sentencias juntas.
    # Corre dentro de la MISMA transacción de Alembic: si algo falla, no queda nada creado.
    conexion = op.get_bind().connection
    with conexion.cursor() as cursor:
        cursor.execute(SQL_INICIAL.read_text(encoding="utf-8"))


def downgrade() -> None:
    raise NotImplementedError(
        "El esquema inicial no se revierte: borraría TODAS las tablas y sus datos."
    )
