from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.base import Base
from backend.infrastructure.database.mixins import BusinessEntityMixin


class HealthCheckORM(BusinessEntityMixin, Base):
    """Map health check records to the PostgreSQL table."""

    __tablename__ = "pm_health_checks"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )
    status: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
