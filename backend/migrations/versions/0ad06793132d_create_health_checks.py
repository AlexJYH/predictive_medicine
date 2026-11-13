"""create health checks

Revision ID: 0ad06793132d
Revises: 
Create Date: 2026-11-06 10:23:33.920219
"""

from typing import Sequence, Union

from alembic import op



revision: str = '0ad06793132d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply this migration."""
    op.execute("""
                    CREATE TABLE public.pm_health_checks (
                    id bigint PRIMARY KEY,
                    tenant_id bigint NOT NULL,
                    created_at timestamptz(6) NOT NULL DEFAULT now(),
                    updated_at timestamptz(6) NOT NULL DEFAULT now(),
                    created_by bigint NOT NULL,
                    updated_by bigint NOT NULL,
                    delete_flg smallint NOT NULL DEFAULT 0,
                    status bigint,
                    message varchar(1024),
                    CONSTRAINT ck_pm_health_checks_delete_flg CHECK (delete_flg IN (0, 1))
                    )
               """
    )


    op.execute(
        """
            CREATE INDEX ix_pm_health_checks_tenant_created_at
            ON public.pm_health_checks (tenant_id, created_at DESC)
            WHERE delete_flg = 0;
        """
    )


    op.execute(
        """
            COMMENT ON TABLE public.pm_health_checks
            IS 'Health check records';
        """
    )


def downgrade() -> None:
    """Revert this migration."""
    op.execute("DROP TABLE public.pm_health_checks")
