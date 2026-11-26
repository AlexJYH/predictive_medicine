"""add api_prefix in pm_llm_model

Revision ID: ff5b84cfb538
Revises: b7cfe304ade1
Create Date: 2026-11-26 14:06:22.882133
"""

from typing import Sequence, Union

from alembic import op



revision: str = 'ff5b84cfb538'
down_revision: Union[str, Sequence[str], None] = 'b7cfe304ade1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply this migration."""
    # Existing registrations use the OpenAI-compatible SiliconFlow endpoint.
    op.execute("""
        ALTER TABLE public.pm_llm_model
        ADD COLUMN api_prefix varchar(64) NOT NULL DEFAULT 'openai'
    """)
    op.execute("""
        COMMENT ON COLUMN public.pm_llm_model.api_prefix
        IS 'LiteLLM 接入适配器标识，如 openai；不包含末尾斜杠'
    """)
    # Future registrations must explicitly select their adapter.
    op.execute("""
        ALTER TABLE public.pm_llm_model
        ALTER COLUMN api_prefix DROP DEFAULT
    """)


def downgrade() -> None:
    """Revert this migration."""
    op.execute("ALTER TABLE public.pm_llm_model DROP COLUMN api_prefix")
