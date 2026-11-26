from asyncio import to_thread
from datetime import datetime
from multiprocessing import AuthenticationError

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.common.id.snowflake import SnowflakeIdGenerator
from backend.common.identity.context import require_identity
from backend.common.identity.model.identity import IdentityContext
from backend.common.secuirty.password import verify_password, hash_password
from backend.repository.identity.protocol import IdentityRepository
from backend.services.identity.model.common import TenantRequest, RegisterRequest, RegisterVO
from backend.services.identity.model.relationship import TenantUserRelationDTO
from backend.services.identity.model.tenant import TenantDTO
from backend.services.identity.model.user import UserDTO


class IdentityService:

    def __init__(self, repository: IdentityRepository, session_factory: async_sessionmaker[AsyncSession],
                 id_generator: SnowflakeIdGenerator) -> None:
        self._repository = repository
        self._session_factory = session_factory
        self._id_generator = id_generator

    async def authenticate_credentials(self, username: str, password: str, tenant_id: int) -> IdentityContext | None:
        async with self._session_factory() as session:
            user_dto = await self._repository.get_user(None, username, session)

        if not user_dto:
            raise AuthenticationError("User not found")

        valid = await to_thread(
            verify_password,
            password,
            user_dto.password_hash,
        )
        if not valid:
            raise AuthenticationError("Invalid account,password or tenant_id")

        async with self._session_factory() as session:
            tenant_dto = await self._repository.get_tenant(tenant_id, session)
            tenant_user_relation_dto = await self._repository.get_tenant_user_relation(tenant_id, user_dto.id, session)

        if not tenant_user_relation_dto:
            raise AuthenticationError("Tenant user does not exist")

        if not tenant_dto:
            raise AuthenticationError("Tenant does not exist")

        return IdentityContext(
            user_id=user_dto.id,
            tenant_id=tenant_dto.id,
        )

    async def validate_identity(self, identity: IdentityContext) -> bool:
        async with self._session_factory() as session:
            tenant_dto = await self._repository.get_tenant(identity.tenant_id, session)
            user_dto = await self._repository.get_user(user_id=identity.user_id, username=None, session_factory=session)
            tenant_user_relation_dto = await self._repository.get_tenant_user_relation(identity.tenant_id,
                                                                                       identity.user_id, session)

            if not tenant_dto or not user_dto or not tenant_user_relation_dto:
                return False

        return True

    async def create_tenant(self, request: TenantRequest) -> TenantDTO | None:
        user_id = require_identity().user_id
        tenant = TenantDTO(
            id=self._id_generator.generate_next_id(),
            company_name=request.company_name,
            company_code=request.company_code,
            status=0,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            delete_flg=0,
        )

        async with self._session_factory() as session:
            async with session.begin():
                valid = await self._repository.create_tenant(tenant_dto=tenant, session_factory=session, )
                if not valid:
                    return None

        return tenant

    async def register(self, request: RegisterRequest) -> RegisterVO | None:
        now = datetime.now()
        tenant_id = self._id_generator.generate_next_id()
        user_id = self._id_generator.generate_next_id()
        password_hash = await to_thread(hash_password, request.password)

        tenant = TenantDTO(
            id=tenant_id,
            company_name=request.company_name,
            company_code=request.company_code,
            status=0,
            created_by=user_id,
            updated_by=user_id,
            created_at=now,
            updated_at=now,
            delete_flg=0,
        )

        user = UserDTO(
            id=user_id,
            username=request.username,
            password_hash=password_hash,
            mail=request.mail,
            status=0,
            created_by=user_id,
            updated_by=user_id,
            created_at=now,
            updated_at=now,
            delete_flg=0,
        )

        tenant_user_relation = TenantUserRelationDTO(
            user_id=user_id,
            status=0,
            id=self._id_generator.generate_next_id(),
            tenant_id=tenant_id,
            created_at=now,
            updated_at=now,
            delete_flg=0,
            created_by=user_id,
            updated_by=user_id,
        )

        async with self._session_factory() as session:
            async with session.begin():
                await self._repository.create_tenant(tenant_dto=tenant, session_factory=session, )
                await self._repository.create_user(user_dto=user, session_factory=session, )
                await self._repository.create_tenant_user_relation(tenant_user_relation_dto=tenant_user_relation,session_factory=session, )


        return RegisterVO(
            user_id = user_id,
            tenant_id = tenant_id,
            username = request.username,
            mail = request.mail,
        )
