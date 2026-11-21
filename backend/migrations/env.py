"""Configuración de Alembic: de dónde sale la URL de la base y cómo se ejecutan las migraciones."""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.models import Base  # importa todos los modelos

config = context.config
if config.config_file_name is not None:
    # disable_existing_loggers=False: no silenciar los logs de la app (ni los de pytest)
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo 'alembic upgrade head --sql': solo imprime el SQL, sin conectarse a la base."""
    context.configure(
        url=settings.database_url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # La misma configuración (y la misma contraseña) que usa la API; NullPool: conexión de un solo uso.
    engine = create_engine(settings.database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
