from datetime import UTC, datetime

from sqlalchemy import inspect, event
from sqlalchemy.orm import Session

from backend.common.identity.context import require_identity
from backend.infrastructure.database.mixins import BusinessEntityMixin


def _apply_audit_fields(
        session: Session,
        flush_context: object,
        instances: object,
) -> None:
    new_records = [
        obj
        for obj in session.new
        if isinstance(obj, BusinessEntityMixin)
    ]

    changed_records = [
        obj
        for obj in session.dirty
        if isinstance(obj, BusinessEntityMixin)
           and session.is_modified(obj, include_collections=False)
    ]

    if not new_records and not changed_records:
        return

    identity = require_identity()
    now = datetime.now(UTC)

    for record in new_records:
        record.created_at = now
        record.updated_at = now
        record.created_by = identity.user_id
        record.updated_by = identity.user_id
        record.tenant_id = identity.tenant_id

    for record in changed_records:
        state = inspect(record)

        if record.tenant_id != identity.tenant_id:
            raise ValueError("Record tenant does not match the current tenant")

        record.updated_at = now
        record.updated_by = identity.user_id


def register_audit_events() -> None:
    if not event.contains(Session, "before_flush", _apply_audit_fields):
        event.listen(Session, "before_flush", _apply_audit_fields)
