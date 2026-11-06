from __future__ import annotations

from logging.config import fileConfig

from alembic import context

import asyncio
import os
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from backend.common.config.bootstrap import load_batch_config
from backend.infrastructure.database.base import Base

alembic_config = context.config

if (
        alembic_config.config_file_name is not None
        and alembic_config.file_config.has_section("loggers")
):
    fileConfig(
        alembic_config.config_file_name,
        disable_existing_loggers=False,
    )

def load_database_url() -> str:
    backend_dir_value = alembic_config.get_main_option("backend_dir")
    backend_dir = Path(backend_dir_value).expanduser().resolve()
    app_env = os.environ.get("APP_ENV").strip()
    batch_config = load_batch_config(
        env_dir=str(backend_dir / "env" / app_env),
        config_dir=str(backend_dir / "config"),
    )
    url = batch_config.database_setting.database.url.strip()
    return url


database_url = load_database_url()
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
        echo=False,
    )

    try:
        async with engine.connect() as connection:
            await connection.run_sync(run_migrations)
    finally:
        await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
