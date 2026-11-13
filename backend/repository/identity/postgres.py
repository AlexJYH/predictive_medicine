
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, session

from backend.repository.identity.orm import UserORM, TenantORM, TenantUserRelationORM
from backend.repository.identity.protocol import IdentityRepository
from backend.services.identity.model.relationship import TenantUserRelationDTO
from backend.services.identity.model.tenant import TenantDTO
from backend.services.identity.model.user import UserDTO


class PostgresIdentityRepository(IdentityRepository):

    async def get_user(self, user_id: int, username: str, session_factory:AsyncSession) -> UserDTO | None:
        statement = select(UserORM).where(UserORM.status == 0)
        if user_id:
            statement = statement.where(UserORM.id == user_id)
        if username:
            statement = statement.where(UserORM.username == username)
        statement = statement.where(UserORM.delete_flg == 0)
        statement = statement.execution_options(authentication_query=True)

        result = await session_factory.execute(statement)
        user = result.scalar_one_or_none()
        if not user:
            return None
        return UserDTO(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
            mail=user.mail,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            created_by=user.created_by,
            updated_by=user.updated_by,
            delete_flg=user.delete_flg,
        )


    async def get_tenant(self, tenant_id: int, session_factory: AsyncSession) -> TenantDTO | None:
        statement = select(TenantORM).where(TenantORM.delete_flg == 0, TenantORM.status == 0,)
        if tenant_id:
            statement = statement.where(TenantORM.id == tenant_id)
        statement = statement.execution_options(authentication_query=True)

        result = await session_factory.execute(statement)
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None
        return TenantDTO(
            id = tenant.id,
            company_code=tenant.company_code,
            company_name=tenant.company_name,
            status=tenant.status,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
            created_by=tenant.created_by,
            updated_by=tenant.updated_by,
            delete_flg=tenant.delete_flg,
        )


    async def get_tenant_user_relation(self, tenant_id: int, user_id: int,
                                       session_factory: AsyncSession) -> TenantUserRelationDTO | None:
        statement = select(TenantUserRelationORM).where(TenantUserRelationORM.delete_flg == 0, TenantUserRelationORM.status == 0,)
        statement = statement.where(TenantUserRelationORM.tenant_id == tenant_id)
        statement = statement.where(TenantUserRelationORM.user_id == user_id)
        statement = statement.execution_options(authentication_query=True)

        result = await session_factory.execute(statement)
        tenant_user_relation = result.scalar_one_or_none()

        if not tenant_user_relation:
            return None

        return TenantUserRelationDTO(
            user_id=tenant_user_relation.user_id,
            tenant_id=tenant_user_relation.tenant_id,
            status=tenant_user_relation.status,
            id=tenant_user_relation.id,
            created_by=tenant_user_relation.created_by,
            updated_by=tenant_user_relation.updated_by,
            delete_flg=tenant_user_relation.delete_flg,
            created_at=tenant_user_relation.created_at,
            updated_at=tenant_user_relation.updated_at,
        )


    async def create_tenant(self, tenant_dto: TenantDTO, session_factory: AsyncSession,) -> bool:
        session_factory.add(TenantORM(**tenant_dto.model_dump()))
        try:
            await session_factory.flush()
            return True
        except IntegrityError:
            return False

    async def create_user(self, user_dto: UserDTO, session_factory: AsyncSession, ) -> None:
        session_factory.add(UserORM(**user_dto.model_dump()))
        await session_factory.flush()

    async def create_tenant_user_relation(self, tenant_user_relation_dto: TenantUserRelationDTO, session_factory: AsyncSession, ) -> None:
        session_factory.add(TenantUserRelationORM(**tenant_user_relation_dto.model_dump()))
        await session_factory.flush()
