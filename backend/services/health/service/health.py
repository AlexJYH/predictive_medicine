from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.common.constants.health_check import SUCCESS_HEALTH_CHECK_MESSAGE
from backend.common.enums.result_code import ResultCode
from backend.common.id.snowflake import SnowflakeIdGenerator
from backend.common.identity.context import require_identity
from backend.infrastructure.database.tenant_scope import apply_database_scope
from backend.repository.health.protocol import HealthRepository
from backend.services.health.model.health import HealthResponse, HealthCheckDTO


class HealthService:

    def __init__(
            self,
            repository: HealthRepository,
            session_factory: async_sessionmaker[AsyncSession],
            id_generator: SnowflakeIdGenerator
    ) -> None:
        self._repository = repository
        self._session_factory = session_factory
        self._id_generator = id_generator

    async def get_health(self) -> HealthResponse:
        health_check_list = []
        time_now = datetime.now(UTC)
        health_check_id = self._id_generator.generate_next_id()
        identity = require_identity()
        health_check_list.append(HealthCheckDTO(
            id = health_check_id,
            tenant_id = identity.tenant_id,
            created_at=time_now,
            updated_at=time_now,
            created_by=identity.user_id,
            updated_by=identity.user_id,
            delete_flg=False,
            status = ResultCode.SUCCESS,
            message = SUCCESS_HEALTH_CHECK_MESSAGE,
        ))

        async with self._session_factory() as session:
            async with session.begin():
                await apply_database_scope(session)
                await self._repository.create_health_check_logs(
                    health_check_list,
                    session,
                )

        result = HealthResponse(
            id=health_check_id,
            status=ResultCode.SUCCESS,
            message=SUCCESS_HEALTH_CHECK_MESSAGE,
        )
        return result
