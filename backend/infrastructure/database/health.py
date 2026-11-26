import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


async def check_connection(
        session_factory: async_sessionmaker[AsyncSession],
        *,
        timeout_seconds:float = 5.0,
) -> None:
    async with asyncio.timeout(timeout_seconds):
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))