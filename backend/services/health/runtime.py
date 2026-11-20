from backend.infrastructure.runtime import get_async_session_factory, get_id_generator, get_resources
from backend.repository.health.postgres import PostgresHealthRepository
from backend.services.health.service.health import HealthService


def get_health_service() -> HealthService:
    resources = get_resources()
    return HealthService(
        repository=PostgresHealthRepository(),
        session_factory=resources.session_factory,
        id_generator=resources.id_generator,
    )