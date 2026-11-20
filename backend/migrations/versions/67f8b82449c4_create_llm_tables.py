"""create llm tables

Revision ID: 67f8b82449c4
Revises: c744eca46b78
Create Date: 2026-11-17 13:42:24.275727
"""

from typing import Sequence, Union

from alembic import op

revision: str = "67f8b82449c4"
down_revision: Union[str, Sequence[str], None] = "c744eca46b78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create shared LLM vendors, model registrations and scenario routes."""
    op.execute("""
        CREATE TABLE public.pm_llm_vendor (
            id bigint PRIMARY KEY,
            vendor varchar(256) NOT NULL,
            status smallint NOT NULL DEFAULT 0,
            url varchar(512) NOT NULL,
            passport varchar(256) NOT NULL,
            created_by bigint,
            updated_by bigint,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            delete_flg smallint NOT NULL DEFAULT 0,
            CONSTRAINT ck_pm_llm_vendor_status CHECK (status IN (0, 1)),
            CONSTRAINT ck_pm_llm_vendor_delete_flg CHECK (delete_flg IN (0, 1))
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_llm_vendor_active
        ON public.pm_llm_vendor (vendor) WHERE delete_flg = 0
    """)
    op.execute("COMMENT ON TABLE public.pm_llm_vendor IS '平台共享的模型供应商连接'")
    op.execute("""
        COMMENT ON COLUMN public.pm_llm_vendor.passport
        IS '服务端凭证引用，例如环境变量名称；不保存明文 API Key'
    """)
    op.execute("COMMENT ON COLUMN public.pm_llm_vendor.url IS '供应商 API 基础地址'")

    op.execute("""
        CREATE TABLE public.pm_llm_model (
            id bigint PRIMARY KEY,
            model varchar(256) NOT NULL,
            vendor_id bigint NOT NULL,
            status smallint NOT NULL DEFAULT 0,
            created_by bigint,
            updated_by bigint,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            delete_flg smallint NOT NULL DEFAULT 0,
            CONSTRAINT ck_pm_llm_model_status CHECK (status IN (0, 1)),
            CONSTRAINT ck_pm_llm_model_delete_flg CHECK (delete_flg IN (0, 1))
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_llm_model_active
        ON public.pm_llm_model (vendor_id, model) WHERE delete_flg = 0
    """)
    op.execute("CREATE INDEX ix_pm_llm_model_vendor_id ON public.pm_llm_model (vendor_id)")
    op.execute("COMMENT ON TABLE public.pm_llm_model IS '供应商上的模型接入注册'")
    op.execute("""
        COMMENT ON COLUMN public.pm_llm_model.model
        IS '该供应商使用的精确上游模型标识'
    """)

    op.execute("""
        CREATE TABLE public.pm_model_route (
            id bigint PRIMARY KEY,
            model_id bigint NOT NULL,
            fallback_id bigint NOT NULL,
            scene varchar(256) NOT NULL,
            usage varchar(256) NOT NULL,
            status smallint NOT NULL DEFAULT 0,
            created_by bigint,
            updated_by bigint,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            delete_flg smallint NOT NULL DEFAULT 0,
            CONSTRAINT ck_model_route_distinct
                CHECK (fallback_id <> model_id),
            CONSTRAINT ck_pm_model_route_status CHECK (status IN (0, 1)),
            CONSTRAINT ck_pm_model_route_delete_flg CHECK (delete_flg IN (0, 1))
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_model_route_active
        ON public.pm_model_route (usage, scene) WHERE delete_flg = 0
    """)
    op.execute("CREATE INDEX ix_pm_model_route_model_id ON public.pm_model_route (model_id)")
    op.execute("CREATE INDEX ix_pm_model_route_fallback_id ON public.pm_model_route (fallback_id)")
    op.execute("COMMENT ON TABLE public.pm_model_route IS '能力与场景的主备模型路由'")
    op.execute("COMMENT ON COLUMN public.pm_model_route.model_id IS '主模型注册 ID'")
    op.execute("""
        COMMENT ON COLUMN public.pm_model_route.fallback_id
        IS '备用模型注册 ID，必填'
    """)

    for table in ("pm_llm_vendor", "pm_llm_model", "pm_model_route"):
        op.execute(f"COMMENT ON COLUMN public.{table}.status IS '状态：0启用，1禁用'")
        op.execute(f"COMMENT ON COLUMN public.{table}.delete_flg IS '软删除：0有效，1已删除'")
        op.execute(f"COMMENT ON COLUMN public.{table}.updated_at IS '更新时间，由应用更新时维护'")


def downgrade() -> None:
    """Drop routes before models and their referenced vendors."""
    op.execute("DROP TABLE public.pm_model_route")
    op.execute("DROP TABLE public.pm_llm_model")
    op.execute("DROP TABLE public.pm_llm_vendor")
