from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.common.id.snowflake import SnowflakeIdGenerator


@dataclass(frozen=True, slots=True)
class RuntimeResources:
    session_factory: async_sessionmaker[AsyncSession]
    id_generator: SnowflakeIdGenerator


_resources: RuntimeResources


def initialize_resources(resources: RuntimeResources) -> None:
    global _resources
    _resources = resources


def get_resources() -> RuntimeResources:
    return _resources


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    return get_resources().session_factory


def get_id_generator() -> SnowflakeIdGenerator:
    return get_resources().id_generator


def clear_resources() -> None:
    global _resources
    _resources = None
