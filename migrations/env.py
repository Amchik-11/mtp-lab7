"""Alembic подключается к выбранному файлу книжной базы."""

from alembic import context

from library import database_path
from models import Base, engine_for


if context.is_offline_mode():
    raise RuntimeError("Запустите миграцию с подключением к SQLite.")

path = context.config.attributes.get("database_file") or database_path()
engine = engine_for(path)
try:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
finally:
    engine.dispose()
