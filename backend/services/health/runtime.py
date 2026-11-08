from starlette.requests import Request

from backend.infrastructure.runtime import get_async_session_factory, get_id_generator
from backend.repository.health.postgres import PostgresHealthRepository
from backend.services.health.service.health import HealthService


def get_health_service() -> HealthService:
    session_factory = get_async_session_factory()
    id_generator = get_id_generator()
    return HealthService(
        repository=PostgresHealthRepository(),
        session_factory=session_factory,
        id_generator=id_generator,
    )