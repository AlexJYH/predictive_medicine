from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repository.llm_model.orm import LLMVendorORM, LLMModelORM, ModelRouteORM
from backend.repository.llm_model.protocol import LLMModelRepository
from backend.services.llm.vendor_model.model.llm_model import LLMVendorDTO, LLMModelDTO, ModelRouteDTO


class PostgresLLMModelRepository(LLMModelRepository):

    async def create_llm_vendor(self, vendor_dtos: list[LLMVendorDTO], session_factory: AsyncSession) -> None:
        for vendor_dto in vendor_dtos:
            llm_vendor_orm = LLMVendorORM(
                vendor=vendor_dto.vendor,
                url=vendor_dto.url,
                passport=vendor_dto.passport,
                status=vendor_dto.status,
                id=vendor_dto.id,
                created_by=vendor_dto.created_by,
                updated_by=vendor_dto.updated_by,
                updated_at=vendor_dto.updated_at,
                delete_flg=vendor_dto.delete_flg,
                created_at=vendor_dto.created_at,
            )
            session_factory.add(llm_vendor_orm)
        await session_factory.flush()

    async def update_llm_vendor(self, vendor_dtos: list[LLMVendorDTO], session_factory: AsyncSession) -> None:
        vendor_ids = []
        for vendor_dto in vendor_dtos:
            vendor_ids.append(vendor_dto.id)

        statement = select(LLMVendorORM).where(LLMVendorORM.id.in_(vendor_ids), LLMVendorORM.delete_flg == 0)
        result = await session_factory.execute(statement)
        for vendor in result.scalars().all():
            dto = next(dto for dto in vendor_dtos if dto.id == vendor.id)
            vendor.vendor = dto.vendor
            vendor.url = dto.url
            vendor.passport = dto.passport
            vendor.status = dto.status
            vendor.updated_at = dto.updated_at
            vendor.updated_by = dto.updated_by
            vendor.delete_flg = dto.delete_flg

        await session_factory.flush()

    async def delete_llm_vendor(self, vendor_ids: list[int], session_factory: AsyncSession) -> None:
        statement = select(LLMVendorORM).where(LLMVendorORM.id.in_(vendor_ids),LLMVendorORM.delete_flg == 0)
        result = await session_factory.execute(statement)
        for vendor in result.scalars().all():
            vendor.delete_flg = 1

        await session_factory.flush()

    async def search_llm_vendor(self, *, vendor_ids: list[int] | None=None, vendor_name: str | None, session_factory: AsyncSession) -> list[LLMVendorDTO]:
        statement = select(LLMVendorORM).where(LLMVendorORM.delete_flg == 0)
        if vendor_ids:
            statement = statement.where(LLMVendorORM.id.in_(vendor_ids))
        if vendor_name and vendor_name.strip():
            statement = statement.where(LLMVendorORM.vendor.like(f"%{vendor_name}%"))
        result = await session_factory.execute(statement)

        vendor_dtos = []
        for vendor in result.scalars().all():
            vendor_dtos.append(LLMVendorDTO(
                vendor=vendor.vendor,
                url=vendor.url,
                passport=vendor.passport,
                status=vendor.status,
                id=vendor.id,
                created_by=vendor.created_by,
                updated_by=vendor.updated_by,
                updated_at=vendor.updated_at,
                delete_flg=vendor.delete_flg,
                created_at=vendor.created_at,
            ))

        return vendor_dtos

    async def create_llm_model(self, model_dtos: list[LLMModelDTO], session_factory: AsyncSession) -> None:
        for model_dto in model_dtos:
            session_factory.add(LLMModelORM(**model_dto.model_dump()))
        await session_factory.flush()

    async def update_llm_model(self, model_dtos: list[LLMModelDTO], session_factory: AsyncSession) -> None:
        model_ids = []
        for model_dto in model_dtos:
            model_ids.append(model_dto.id)
        statement = select(LLMModelORM).where(LLMModelORM.id.in_(model_ids),LLMModelORM.delete_flg == 0)
        result = await session_factory.execute(statement)

        for model in result.scalars().all():
            model_dto = next(dto for dto in model_dtos if dto.id == model.id)
            if model_dto:
                model.model = model_dto.model
                model.vendor_id = model_dto.vendor_id
                model.status = model_dto.status
                model.updated_at = model_dto.updated_at
                model.updated_by = model_dto.updated_by
                model.delete_flg = model_dto.delete_flg

        await session_factory.flush()

    async def delete_llm_model(self, model_ids: list[int], session_factory: AsyncSession) -> None:
        statement = select(LLMModelORM).where(LLMModelORM.id.in_(model_ids), LLMModelORM.delete_flg == 0)
        result = await session_factory.execute(statement)
        for model in result.scalars().all():
            model.delete_flg = 1
        await session_factory.flush()

    async def search_llm_model(self, vendor_ids: list[int] | None, model: str | None, model_ids: list[int] | None , session_factory: AsyncSession) -> list[LLMModelDTO]:
        statement = select(LLMModelORM).where(LLMModelORM.delete_flg == 0)
        if vendor_ids:
            statement = statement.where(LLMModelORM.vendor_id.in_(vendor_ids))
        if model_ids:
            statement = statement.where(LLMModelORM.id.in_(model_ids))
        if model and model.strip():
            statement = statement.where(LLMModelORM.model.like(f"%{model}%"))

        result = await session_factory.execute(statement)
        model_dtos = []
        for model in result.scalars().all():
            model_dtos.append(LLMModelDTO(
                model=model.model,
                vendor_id=model.vendor_id,
                status=model.status,
                id=model.id,
                created_by=model.created_by,
                updated_by=model.updated_by,
                updated_at=model.updated_at,
                created_at=model.created_at,
                delete_flg=model.delete_flg,
            ))

        return model_dtos

    async def create_model_route(self, route_dtos: list[ModelRouteDTO], session_factory: AsyncSession) -> None:
        for route_dto in route_dtos:
            session_factory.add(ModelRouteORM(**route_dto.model_dump()))
        await session_factory.flush()

    async def update_model_route(self, route_dtos: list[ModelRouteDTO], session_factory: AsyncSession) -> None:
        route_ids = [dto.id for dto in route_dtos]
        statement = select(ModelRouteORM).where(ModelRouteORM.id.in_(route_ids), ModelRouteORM.delete_flg == 0)

        result = await session_factory.execute(statement)
        for route in result.scalars().all():
            route_dto = next(dto for dto in route_dtos if dto.id == route.id)
            route.model_id = route_dto.model_id
            route.updated_at = route_dto.updated_at
            route.updated_by = route_dto.updated_by
            route.delete_flg = route_dto.delete_flg
            route.fallback_id = route_dto.fallback_id
            route.scene = route_dto.scene
            route.usage = route_dto.usage
            route.status = route_dto.status

        await session_factory.flush()

    async def delete_model_route(self, route_ids: list[int], session_factory: AsyncSession) -> None:
        statement = select(ModelRouteORM).where(ModelRouteORM.delete_flg == 0, ModelRouteORM.id.in_(route_ids))
        result = await session_factory.execute(statement)
        for route in result.scalars().all():
            route.delete_flg = 1

        await session_factory.flush()

    async def search_model_route(self, model_ids: list[int] | None, fallback_ids: list[int] | None,scene: str | None, usage: str | None, session_factory: AsyncSession) -> list[ModelRouteDTO]:
        statement = select(ModelRouteORM).where(ModelRouteORM.delete_flg == 0)
        if model_ids:
            statement = statement.where(ModelRouteORM.model_id.in_(model_ids))
        if fallback_ids:
            statement = statement.where(ModelRouteORM.fallback_id.in_(fallback_ids))
        if scene and scene.strip():
            statement = statement.where(ModelRouteORM.scene.like(f"%{scene}%"))
        if usage and usage.strip():
            statement = statement.where(ModelRouteORM.usage.like(f"%{usage}%"))

        result = await session_factory.execute(statement)
        model_routes = []
        for route in result.scalars().all():
            model_routes.append(ModelRouteDTO(
                id=route.id,
                model_id=route.model_id,
                fallback_id=route.fallback_id,
                scene=route.scene,
                usage=route.usage,
                status=route.status,
                created_by=route.created_by,
                updated_by=route.updated_by,
                updated_at=route.updated_at,
                created_at=route.created_at,
                delete_flg=route.delete_flg,
            ))

        return model_routes
