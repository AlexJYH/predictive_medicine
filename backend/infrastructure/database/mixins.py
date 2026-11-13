from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column


class BusinessEntityMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="业务主键 ID")
    tenant_id: Mapped[int] = mapped_column(BigInteger, index=True, default=0, comment="租户 ID")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="更新时间")
    created_by: Mapped[int] = mapped_column(BigInteger, default=0, comment="创建人用户 ID")
    updated_by: Mapped[int] = mapped_column(BigInteger, default=0, comment="最后更新人用户 ID")
    delete_flg: Mapped[int] = mapped_column(SmallInteger, index=True, default=0,
                                            comment="软删除标记，0 表示有效，1 表示已删除")
