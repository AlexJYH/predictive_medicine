from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.repository.health.protocol import HealthRepository
from backend.services.health.model.health import HealthResponse


class HealthService:

    def __init__(
            self,
            repository: HealthRepository,
            session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._repository = repository
        self._session_factory = session_factory

    async def get_health(self) -> HealthResponse:
        result = HealthResponse(
            status="ok",
            environment="configured",
        )
        return result
