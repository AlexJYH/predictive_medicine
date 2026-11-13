"""create identity tables

Revision ID: c744eca46b78
Revises: 0ad06793132d
Create Date: 2026-11-08 22:51:59.167566
"""

from typing import Sequence, Union

from alembic import op


revision: str = "c744eca46b78"
down_revision: Union[str, Sequence[str], None] = "0ad06793132d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create global users, tenants and tenant memberships."""
    op.execute("""
        CREATE TABLE public.pm_user (
            id bigint PRIMARY KEY,
            username varchar(256) NOT NULL,
            password_hash varchar(512) NOT NULL,
            mail varchar(128),
            status smallint NOT NULL DEFAULT 0,
            created_by bigint,
            updated_by bigint,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            delete_flg smallint NOT NULL DEFAULT 0,
            CONSTRAINT ck_pm_user_username CHECK (
                length(btrim(username)) > 0
                AND username = btrim(username)
            ),
            CONSTRAINT ck_pm_user_password_hash
                CHECK (length(btrim(password_hash)) > 0),
            CONSTRAINT ck_pm_user_mail CHECK (
                mail IS NULL OR (
                    length(btrim(mail)) > 0 AND mail = btrim(mail)
                )
            ),
            CONSTRAINT ck_pm_user_status CHECK (status IN (0, 1)),
            CONSTRAINT ck_pm_user_delete_flg CHECK (delete_flg IN (0, 1))
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX ux_pm_user_username
        ON public.pm_user (lower(username))
    """)
    op.execute("COMMENT ON TABLE public.pm_user IS '全局用户'")
    op.execute("""
        COMMENT ON COLUMN public.pm_user.password_hash
        IS '密码哈希，不保存明文密码'
    """)
    op.execute("COMMENT ON COLUMN public.pm_user.status IS '账号状态：1禁用，0启用'")

    op.execute("""
        CREATE TABLE public.pm_tenant (
            id bigint PRIMARY KEY,
            company_name varchar(512) NOT NULL,
            company_code varchar(64),
            status smallint NOT NULL DEFAULT 0,
            created_by bigint,
            updated_by bigint,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            delete_flg smallint NOT NULL DEFAULT 0,
            CONSTRAINT uq_pm_tenant_company_code UNIQUE (company_code),
            CONSTRAINT ck_pm_tenant_company_name
                CHECK (length(btrim(company_name)) > 0),
            CONSTRAINT ck_pm_tenant_company_code CHECK (
                company_code IS NULL OR (
                    length(btrim(company_code)) > 0
                    AND company_code = btrim(company_code)
                )
            ),
            CONSTRAINT ck_pm_tenant_status CHECK (status IN (0, 1)),
            CONSTRAINT ck_pm_tenant_delete_flg CHECK (delete_flg IN (0, 1))
        )
    """)
    op.execute("COMMENT ON TABLE public.pm_tenant IS '租户'")
    op.execute("""
        COMMENT ON COLUMN public.pm_tenant.company_code
        IS '公司或业务编码，可空；提供时必须唯一'
    """)
    op.execute("COMMENT ON COLUMN public.pm_tenant.status IS '租户状态：1禁用，0启用'")

    op.execute("""
        CREATE TABLE public.pm_tenant_user_relation (
            id bigint PRIMARY KEY,
            tenant_id bigint NOT NULL,
            user_id bigint NOT NULL,
            status smallint NOT NULL DEFAULT 0,
            created_by bigint NOT NULL,
            updated_by bigint NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            delete_flg smallint NOT NULL DEFAULT 0,
            CONSTRAINT fk_pm_tenant_user_relation_tenant
                FOREIGN KEY (tenant_id) REFERENCES public.pm_tenant (id)
                ON DELETE RESTRICT,
            CONSTRAINT fk_pm_tenant_user_relation_user
                FOREIGN KEY (user_id) REFERENCES public.pm_user (id)
                ON DELETE RESTRICT,
            CONSTRAINT uq_pm_tenant_user_relation_tenant_user
                UNIQUE (tenant_id, user_id),
            CONSTRAINT ck_pm_tenant_user_relation_status CHECK (status IN (0, 1)),
            CONSTRAINT ck_pm_tenant_user_relation_delete_flg CHECK (delete_flg IN (0, 1))
        )
    """)
    op.execute("""
        CREATE INDEX ix_pm_tenant_user_relation_user_id
        ON public.pm_tenant_user_relation (user_id)
    """)
    op.execute("""
        CREATE INDEX ix_pm_tenant_user_relation_tenant_id
        ON public.pm_tenant_user_relation (tenant_id)
    """)
    op.execute("""
        CREATE INDEX ix_pm_tenant_user_relation_delete_flg
        ON public.pm_tenant_user_relation (delete_flg)
    """)
    op.execute("COMMENT ON TABLE public.pm_tenant_user_relation IS '租户成员关系'")
    op.execute("""
        COMMENT ON COLUMN public.pm_tenant_user_relation.status
        IS '成员状态：1禁用，0启用'
    """)


def downgrade() -> None:
    """Drop memberships before the referenced tenant and user tables."""
    op.execute("DROP TABLE public.pm_tenant_user_relation")
    op.execute("DROP TABLE public.pm_tenant")
    op.execute("DROP TABLE public.pm_user")
