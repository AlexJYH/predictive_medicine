from backend.infrastructure.runtime import get_async_session_factory, get_id_generator, get_resources
from backend.repository.identity.postgres import PostgresIdentityRepository
from backend.services.identity.services.identity import IdentityService


def get_identity_service() -> IdentityService:
    resources = get_resources()
    return IdentityService(
        repository=PostgresIdentityRepository(),
        session_factory=resources.session_factory,
        id_generator=resources.id_generator,
    )