import os
from logging.config import fileConfig

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
    """Return database URL from environment or config."""
    default_url = config.get_main_option("sqlalchemy.url")
    return os.getenv("DATABASE_URL", default_url)

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
