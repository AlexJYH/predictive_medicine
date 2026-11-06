from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.common.config.bootstrap import BatchConfig
from backend.infrastructure.database.audit import register_audit_events
from backend.infrastructure.database.health import check_connection
from backend.infrastructure.database.session import DatabaseRuntime
from backend.infrastructure.database.tenant_scope import register_tenant_scope_updates


def create_app(config: BatchConfig) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app_life: FastAPI):
        runtime = DatabaseRuntime.create(config.database_setting.database)
        try:
            await check_connection(runtime.session_factory)
            app_life.state.session_factory = runtime.session_factory
            yield
        finally:
            await runtime.close()

    register_audit_events()
    register_tenant_scope_updates()

    app = FastAPI(
        title="predictive medicine",
        lifespan=lifespan,
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

