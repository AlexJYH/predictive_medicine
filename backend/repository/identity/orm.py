"""Identity mappings matching the identity tables migration."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import conv

from backend.infrastructure.database.base import Base


class UserORM(Base):
    __tablename__ = "pm_user"
    __table_args__ = (
        CheckConstraint(
            "length(btrim(username)) > 0 AND username = btrim(username)",
            name=conv("ck_pm_user_username"),
        ),
        CheckConstraint(
            "length(btrim(password_hash)) > 0",
            name=conv("ck_pm_user_password_hash"),
        ),
        CheckConstraint(
            "mail IS NULL OR (length(btrim(mail)) > 0 AND mail = btrim(mail))",
            name=conv("ck_pm_user_mail"),
        ),
        CheckConstraint("status IN (0, 1)", name=conv("ck_pm_user_status")),
        CheckConstraint("delete_flg IN (0, 1)", name=conv("ck_pm_user_delete_flg")),
        {"schema": "public", "comment": "全局用户"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String(256), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False, comment="密码哈希，不保存明文密码")
    mail: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"),comment="账号状态：1禁用，0启用",)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    delete_flg: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))


Index("ux_pm_user_username", func.lower(UserORM.username), unique=True)


class TenantORM(Base):
    __tablename__ = "pm_tenant"
    __table_args__ = (
        UniqueConstraint("company_code", name="uq_pm_tenant_company_code"),
        CheckConstraint(
            "length(btrim(company_name)) > 0",
            name=conv("ck_pm_tenant_company_name"),
        ),
        CheckConstraint(
            "company_code IS NULL OR "
            "(length(btrim(company_code)) > 0 AND company_code = btrim(company_code))",
            name=conv("ck_pm_tenant_company_code"),
        ),
        CheckConstraint("status IN (0, 1)", name=conv("ck_pm_tenant_status")),
        CheckConstraint("delete_flg IN (0, 1)", name=conv("ck_pm_tenant_delete_flg")),
        {"schema": "public", "comment": "租户"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    company_name: Mapped[str] = mapped_column(String(512), nullable=False)
    company_code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="公司或业务编码，可空；提供时必须唯一")
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"),comment="租户状态：1禁用，0启用",)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    delete_flg: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))


class TenantUserRelationORM(Base):
    __tablename__ = "pm_tenant_user_relation"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "user_id", name="uq_pm_tenant_user_relation_tenant_user"
        ),
        CheckConstraint(
            "status IN (0, 1)", name=conv("ck_pm_tenant_user_relation_status")
        ),
        CheckConstraint(
            "delete_flg IN (0, 1)", name=conv("ck_pm_tenant_user_relation_delete_flg")
        ),
        Index("ix_pm_tenant_user_relation_user_id", "user_id"),
        {"schema": "public", "comment": "租户成员关系"},
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "public.pm_tenant.id",
            name="fk_pm_tenant_user_relation_tenant",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "public.pm_user.id",
            name="fk_pm_tenant_user_relation_user",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0"),
        comment="成员状态：1禁用，0启用",
    )
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    delete_flg: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0"), index=True
    )
