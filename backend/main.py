import os
from pathlib import Path

from backend.common.config.bootstrap import load_batch_config, BatchConfig
from backend.app.factor import create_app, load_alembic_info

if __name__ == "__main__":
    import uvicorn

    main_path = Path(__file__).resolve().parent

    different = os.environ.get("APP_ENV")
    env_dir = str(main_path / "env" / different)
    config_dir = str(main_path / "config")

    batch_config = load_batch_config(
        env_dir=env_dir,
        config_dir=config_dir,
    )
    server = batch_config.server_setting.server
    create_app = create_app(batch_config)
    load_alembic_info(main_path)
    uvicorn.run(
        create_app,
        host=server.host,
        port=server.port,
    )
