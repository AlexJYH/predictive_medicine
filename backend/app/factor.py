from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.common.config.bootstrap import BatchConfig


def create_app(config:BatchConfig) -> FastAPI:
    app = FastAPI(
        title="predictive medicine"
    )
    app.include_router(
        api_router,
        prefix=config.server_setting.server.prefix
   )
    return app
