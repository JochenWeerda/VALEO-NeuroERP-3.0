import os
from pathlib import Path
from logging.config import fileConfig

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

from sqlalchemy import engine_from_config, text
from sqlalchemy import pool
from sqlalchemy import MetaData

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData object for 'autogenerate' support
metadata = MetaData()

def _get_database_url() -> str:
    """DATABASE_URL-Umgebung, alembic.ini sqlalchemy.url oder App-Defaults (wie FastAPI)."""
    ini_url = (config.get_main_option("sqlalchemy.url") or "").strip()
    url = (os.getenv("DATABASE_URL") or ini_url).strip()
    if url:
        return url
    try:
        from app.core.config import settings

        u = (getattr(settings, "DATABASE_URL", None) or "").strip()
        if u:
            return u
    except Exception:
        pass
    raise RuntimeError(
        "Keine Datenbank-URL für Alembic: setzen Sie DATABASE_URL (z. B. in .env) "
        "oder sqlalchemy.url in alembic.ini."
    )

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = _get_database_url()
    context.configure(
        url=url,
        target_metadata=metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    section = config.get_section(config.config_ini_section)
    section["sqlalchemy.url"] = _get_database_url()

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Ensure version_num column is wide enough for long revision IDs
        connection.execute(text(
            "CREATE TABLE IF NOT EXISTS alembic_version ("
            "  version_num VARCHAR(128) NOT NULL, "
            "  CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
            ");"
        ))
        connection.execute(text(
            "ALTER TABLE alembic_version "
            "ALTER COLUMN version_num TYPE VARCHAR(128);"
        ))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
