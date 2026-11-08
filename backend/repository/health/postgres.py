from dataclasses import asdict

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.repository.health.orm import HealthCheckORM
from backend.repository.health.protocol import HealthRepository
from backend.services.health.model.health import HealthCheckDTO


class PostgresHealthRepository(HealthRepository):

    async def create_health_check_logs(self, health_checks: list[HealthCheckDTO], session: AsyncSession) -> None:
        row = [HealthCheckORM(**item.model_dump()) for item in health_checks]
        session.add_all(row)
        await session.flush()
