import os
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.middleware.authentication.auth import AuthenticationMiddleware
from backend.common.config.bootstrap import BatchConfig
from backend.common.id.snowflake import SnowflakeIdGenerator
from backend.infrastructure.database.audit import register_audit_events
from backend.infrastructure.database.health import check_connection
from backend.infrastructure.database.session import DatabaseRuntime
from backend.infrastructure.database.tenant_scope import register_tenant_scope_updates
from backend.infrastructure.runtime import RuntimeResources, clear_resources, initialize_resources


def create_app(config: BatchConfig) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        runtime = DatabaseRuntime.create(config.database_setting.database)
        generator = SnowflakeIdGenerator(
            worker_id=config.id_generator_setting.id_generator.worker_id,
            epoch_ms=int(config.id_generator_setting.id_generator.epoch.timestamp() * 1000),
            sequence_wait_timeout_ms=config.id_generator_setting.id_generator.sequence_wait_timeout_ms,
        )
        try:
            await check_connection(runtime.session_factory)
            resources = RuntimeResources(
                session_factory=runtime.session_factory,
                id_generator=generator,
            )
            initialize_resources(resources)
            try:
                yield
            finally:
                clear_resources()
        finally:
            await runtime.close()

    register_audit_events()
    register_tenant_scope_updates()

    app = FastAPI(
        title="predictive medicine",
        lifespan=lifespan,
    )
    app.add_middleware(
        AuthenticationMiddleware,
        environment=os.environ.get("APP_ENV"),
        public_routes={
            (route.method.upper(), f"{config.server_setting.server.prefix}{route.path}")
            for route in config.routers_setting.routers
        },
        token_verifier = None,
        verification_timeout_seconds = config.identity_setting.identity.verification_timeout_seconds,
    )
    app.include_router(
        api_router,
        prefix=config.server_setting.server.prefix
    )
    return app

def load_alembic_info(main_path: Path):
    """Load the Alembic configuration and apply pending database migrations."""
    alembic_config = Config(str(main_path / "alembic.ini"))
    command.upgrade(alembic_config,"head")

