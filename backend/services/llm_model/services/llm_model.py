from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.common.config.model.llm_vendor import LLMVendorSetting
from backend.common.id.snowflake import SnowflakeIdGenerator
from backend.repository.llm_model.protocol import LLMModelRepository
from backend.services.llm_model.model.llm_model import LLMModelInfoDTO


class LLMModelService:

    def __init__(
            self,
            repository: LLMModelRepository,
            session_factory: async_sessionmaker[AsyncSession],
            id_generator: SnowflakeIdGenerator,
            llm_vendor_setting: LLMVendorSetting,
    ) -> None:
        self._repository = repository
        self._session_factory = session_factory
        self._id_generator = id_generator
        self._llm_vendor_setting = llm_vendor_setting

    async def get_model_info(self, scene: str) -> LLMModelInfoDTO | None:
        async with self._session_factory() as session:
            model_route_dtos = await self._repository.search_model_route(model_ids=None, fallback_ids=None, scene=scene,usage=None, session_factory=session)
            if not model_route_dtos or len(model_route_dtos) > 1:
                return None
            model_route_dto = next(dto for dto in model_route_dtos)

            model_ids = [model_route_dto.model_id , model_route_dto.fallback_id]

            llm_model_dtos = await self._repository.search_llm_model(vendor_ids=None, model=None,model_ids=model_ids,session_factory=session)
            vendor_ids = []
            for llm_model_dto in llm_model_dtos:
                vendor_ids.append(llm_model_dto.vendor_id)

            llm_vendor_dtos = await self._repository.search_llm_vendor(vendor_ids=vendor_ids,vendor_name=None, session_factory=session)
            for llm_vendor_dto in llm_vendor_dtos:
                api_key = self._conversion_passport(llm_vendor_dto.passport)
                if not api_key:
                    raise Exception(f"Passport {llm_vendor_dto.passport} not found")
                llm_vendor_dto.api_key = api_key

        return LLMModelInfoDTO(
            model_route_dto=model_route_dto,
            llm_model_dtos=llm_model_dtos,
            llm_vendor_dtos=llm_vendor_dtos,
        )

    def _conversion_passport(self,passport: str) -> str | None:
        llm_vendor_setting = self._llm_vendor_setting
        for vendor_config in llm_vendor_setting.vendor:
            if passport == vendor_config.vendor_name:
                return vendor_config.vendor_api_key
        return None