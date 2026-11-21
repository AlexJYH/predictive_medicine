from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.common.config.manager import get_config
from backend.common.config.model.llm_vendor import LLMVendorSetting
from backend.common.enums.router import LLMVendor
from backend.common.id.snowflake import SnowflakeIdGenerator
from backend.common.identity.context import require_identity
from backend.repository.llm_model.protocol import LLMModelRepository
from backend.services.llm.silicon_flow.model.silicon_response import ModelListResponse
from backend.services.llm.silicon_flow.services.silicon_non_stream import SiliconNonStreamService
from backend.services.llm.vendor_model.model.llm_model import LLMModelInfoDTO, LLMModelDTO

from backend.services.llm.vendor_model.model.llm_model import LLMVendorDTO


class LLMModelService:

    def __init__(
            self,
            repository: LLMModelRepository,
            session_factory: async_sessionmaker[AsyncSession],
            id_generator: SnowflakeIdGenerator,
            silicon_non_stream_service: SiliconNonStreamService,
    ) -> None:
        self._repository = repository
        self._session_factory = session_factory
        self._id_generator = id_generator
        self._silicon_non_stream_service = silicon_non_stream_service

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

    async def get_vendor_info(self, vendor_name:str) -> LLMVendorDTO | None:
        async with self._session_factory() as session:
            vendor_dtos = await self._repository.search_llm_vendor(vendor_name=vendor_name,session_factory=session)
        if not vendor_dtos or len(vendor_dtos) == 0:
            raise Exception(f"Vendor {vendor_name} not found")
        vendor = next(vendor_dto for vendor_dto in vendor_dtos if vendor_dto.vendor == vendor_name)
        vendor.api_key = self._conversion_passport(passport=vendor.passport)
        return vendor if vendor else None

    async def create_vendor(self,llm_vendor_lists: list[LLMVendorDTO]) -> None:
        identity = require_identity()
        now = datetime.now(UTC)
        for llm_vendor_dto in llm_vendor_lists:
            llm_vendor_dto.id = self._id_generator.generate_next_id()
            llm_vendor_dto.status = 0
            llm_vendor_dto.created_by = identity.user_id
            llm_vendor_dto.updated_by = identity.user_id
            llm_vendor_dto.updated_at = now
            llm_vendor_dto.created_at = now
            llm_vendor_dto.delete_flg = 0
        async with self._session_factory() as session:
            async with session.begin():
                await self._repository.create_llm_vendor(llm_vendor_lists,session)

    async def create_llm_model(self, vendor_dto:LLMVendorDTO,model_list_responses:list[ModelListResponse]) -> None:
        identity = require_identity()
        now = datetime.now(UTC)
        llm_model_dtos = []
        for model_list_response in model_list_responses:
            llm_model_dto = LLMModelDTO(
                model = model_list_response.model_name,
                vendor_id=vendor_dto.id,
                id=self._id_generator.generate_next_id(),
                status=0,
                created_at=now,
                updated_at=now,
                created_by=identity.user_id,
                updated_by=identity.user_id,
                delete_flg = 0,
            )
            llm_model_dtos.append(llm_model_dto)
        async with self._session_factory() as session:
            async with session.begin():
                await self._repository.create_llm_model(model_dtos=llm_model_dtos,session_factory=session,)


    def _conversion_passport(self,passport: str) -> str | None:
        llm_vendor_setting = get_config(LLMVendorSetting)
        for vendor_config in llm_vendor_setting.vendor:
            if passport == vendor_config.vendor_name:
                return vendor_config.vendor_api_key
        return None