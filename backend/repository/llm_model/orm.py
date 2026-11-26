from sqlalchemy import BigInteger, Index, String, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.base import Base
from backend.infrastructure.database.mixins import BusinessEntityMixin


class LLMModelORM(BusinessEntityMixin, Base):
    __tablename__ = "pm_llm_model"
    __table_args__ = (
        Index("ix_pm_llm_model_vendor_id", "vendor_id"),
        Index("ix_pm_llm_model_vendor_model", "vendor_id", "model"),
        {"schema": "public"},
    )

    model: Mapped[str] = mapped_column(String(256), nullable=False)
    vendor_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=False,default=0)


class LLMVendorORM(BusinessEntityMixin, Base):
    __tablename__ = "pm_llm_vendor"
    __table_args__ = (
        Index("ix_pm_llm_vendor_vendor", "vendor"),
        {"schema": "public"},
    )

    vendor: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=False,default=0)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    passport: Mapped[str] = mapped_column(String(256), nullable=False)


class ModelRouteORM(BusinessEntityMixin, Base):
    __tablename__ = "pm_model_route"
    __table_args__ = (
        Index("ix_pm_model_route_usage_scene", "usage", "scene"),
        Index("ix_pm_model_route_model_id", "model_id"),
        Index("ix_pm_model_route_fallback_id", "fallback_id"),
        {"schema": "public"},
    )

    model_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fallback_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    scene: Mapped[str] = mapped_column(String(256), nullable=False)
    usage: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False)