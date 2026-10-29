from backend.common.config.bootstrap import load_batch_config
from backend.app.factor import create_app

if __name__ == "__main__":
    import uvicorn

    batch_config = load_batch_config()
    server = batch_config.server_setting.server
    create_app = create_app(batch_config)
    uvicorn.run(
        create_app,
        host=server.host,
        port=server.port,
    )
