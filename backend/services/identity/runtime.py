from backend.infrastructure.runtime import get_async_session_factory, get_id_generator
from backend.repository.identity.postgres import PostgresIdentityRepository
from backend.services.identity.services.identity import IdentityService


def get_identity_service() -> IdentityService:
    session_factory = get_async_session_factory()
    id_generator = get_id_generator()
    return IdentityService(
        repository=PostgresIdentityRepository(),
        session_factory=session_factory,
        id_generator=id_generator,
    )