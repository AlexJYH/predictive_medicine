"""add tenant in llm table

Revision ID: b7cfe304ade1
Revises: 67f8b82449c4
Create Date: 2026-11-21 17:56:57.646710
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = 'b7cfe304ade1'
down_revision: Union[str, Sequence[str], None] = '67f8b82449c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LLM_TABLES = ("pm_llm_vendor", "pm_llm_model", "pm_model_route")


def upgrade() -> None:
    """Apply this migration."""
    for table in LLM_TABLES:
        op.add_column(
            table,
            sa.Column(
                "tenant_id",
                sa.BigInteger(),
                nullable=False,
                server_default=sa.text("0"),
                comment="租户 ID",
            ),
            schema="public",
        )
        op.alter_column(table, "tenant_id", server_default=None, schema="public")
        op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"], schema="public")


def downgrade() -> None:
    """Revert this migration."""
    for table in reversed(LLM_TABLES):
        op.drop_index(f"ix_{table}_tenant_id", table_name=table, schema="public")
        op.drop_column(table, "tenant_id", schema="public")
