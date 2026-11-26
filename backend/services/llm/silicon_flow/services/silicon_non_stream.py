from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.common.id.snowflake import SnowflakeIdGenerator
from backend.infrastructure.httpx.runtime import get_silicon_client
from backend.services.llm.silicon_flow.model.silicon_response import ModelListResponse
from backend.services.llm.vendor_model.model.llm_model import LLMVendorDTO


class SiliconNonStreamService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], id_generator: SnowflakeIdGenerator) -> None:
        self._session_factory = session_factory
        self._id_generator = id_generator

    async def model_list(self,vendor_dto: LLMVendorDTO,model_type: str | None = None,sub_type: str | None = None,) -> list[ModelListResponse]:
        response = await get_silicon_client().model_list(
            api_key=vendor_dto.api_key,
            sub_type=sub_type,
            model_type=model_type,
            base_url=vendor_dto.url
        )
        result = []
        for silicon_model in response:
            model_list_response = ModelListResponse(
                model_name=silicon_model.id,
                object=silicon_model.object,
                created=silicon_model.created,
                owned_by=silicon_model.owned_by,
            )
            result.append(model_list_response)
        return result