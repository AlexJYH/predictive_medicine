from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.identity.model.relationship import TenantUserRelationDTO
from backend.services.identity.model.tenant import TenantDTO
from backend.services.identity.model.user import UserDTO


class IdentityRepository(Protocol):

    async def get_user(self, user_id: int | None, username: str | None, session_factory: AsyncSession) -> UserDTO | None: ...

    async def get_tenant(self, tenant_id: int, session_factory: AsyncSession) -> TenantDTO | None: ...

    async def get_tenant_user_relation(self, tenant_id: int, user_id: int,
                                       session_factory: AsyncSession) -> TenantUserRelationDTO | None: ...

    async def create_tenant(self, tenant_dto: TenantDTO, session_factory: AsyncSession,) -> bool:...

    async def create_user(self, user_dto: UserDTO, session_factory: AsyncSession,) -> None:...

    async def create_tenant_user_relation(self, tenant_user_relation_dto: TenantUserRelationDTO, session_factory: AsyncSession,) -> None:...
