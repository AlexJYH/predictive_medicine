from typing import Protocol

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.services.health.model.health import HealthCheckDTO


class HealthRepository(Protocol):

    async def create_health_check_logs(self, health_checks: list[HealthCheckDTO],
                                       session: AsyncSession) -> None: ...
