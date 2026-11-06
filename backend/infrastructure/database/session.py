from __future__ import annotations
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine

from backend.common.config.model.database import DatabaseConfig


@dataclass(slots=True)
class DatabaseRuntime:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    @classmethod
    def create(cls, config: DatabaseConfig) -> DatabaseRuntime:
        engine = create_async_engine(
            config.url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_pre_ping=config.pool_pre_ping,
        )
        session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )
        return cls(engine=engine, session_factory=session_factory)

    async def close(self) -> None:
        await self.engine.dispose()