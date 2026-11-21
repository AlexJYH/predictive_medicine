from __future__ import annotations

from httpx import AsyncClient

from backend.infrastructure.httpx.dto.silicon_flow import SiliconModelListResponse


class SiliconFlowClient:

    def __init__(self, http_client: AsyncClient) -> None:
        self._http_client = http_client

    async def model_list(self, *,api_key: str,model_type: str | None = None,base_url:str,sub_type:str | None = None) -> list[SiliconModelListResponse]:
        params: dict[str, str] = {}
        if sub_type:
            params["sub_type"] = sub_type
        if type:
            params["type"] = model_type
        response = await self._http_client.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {api_key}"},
            params=params,
        )
        model_list = []
        payload = response.json()
        for item in payload["data"]:
            model_list.append(SiliconModelListResponse.model_validate(item))
        return model_list
