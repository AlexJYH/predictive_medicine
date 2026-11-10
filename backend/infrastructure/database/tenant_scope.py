from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import ORMExecuteState, with_loader_criteria, Session

from backend.common.identity.context import require_identity
from backend.infrastructure.database.mixins import BusinessEntityMixin


def _require_tenant_id() -> int:
    identity = require_identity()
    return identity.tenant_id


def _apply_query_scope(execute_state: ORMExecuteState) -> None:
    if not execute_state.is_orm_statement:
        return

    if execute_state.is_update or execute_state.is_delete:
        raise RuntimeError(
            "Bulk ORM updates and deletes are not supported. "
            "Load records and modify them within a scoped transaction."
        )

    if not execute_state.is_select or execute_state.execution_options.get("authentication_query", False):
        return

    tenant_id = _require_tenant_id()

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            BusinessEntityMixin,
            lambda model: (
                    (model.tenant_id == tenant_id)
                    & (model.delete_flg == 0)
            ),
            include_aliases=True,
        )
    )


def register_tenant_scope_updates() -> None:
    if not event.contains(Session, "do_orm_execute", _apply_query_scope):
        event.listen(Session, "do_orm_execute", _apply_query_scope)


async def apply_database_scope(session: AsyncSession) -> None:
    if not session.in_transaction():
        raise RuntimeError("Database scope must be applied inside an explicit transaction")

    tenant_id = _require_tenant_id()
    identity = require_identity()

    if identity.user_id <= 0:
        raise ValueError("User ID must be positive")

    await session.execute(
        text(
            """
            SELECT
                set_config('app.tenant_id', :tenant_id, true),
                set_config('app.user_id', :user_id, true)
            """
        ),
        {
            "tenant_id": str(tenant_id),
            "user_id": str(identity.user_id),
        },
    )
