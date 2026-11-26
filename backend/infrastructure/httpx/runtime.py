from backend.infrastructure.httpx.client.silicon_flow import SiliconFlowClient
from backend.infrastructure.runtime import get_resources


def get_silicon_client() -> SiliconFlowClient:
    http_client = get_resources().http_client
    return SiliconFlowClient(
        http_client=http_client
    )