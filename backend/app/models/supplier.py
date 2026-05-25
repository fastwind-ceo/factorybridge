from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SupplierProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "supplier_profiles"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False)
    chinese_name: Mapped[str | None] = mapped_column(String(255))
    english_name: Mapped[str | None] = mapped_column(String(255))
    province: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    factory_address: Mapped[str | None] = mapped_column(Text)
    year_established: Mapped[int | None] = mapped_column(Integer)
    employee_count: Mapped[int | None] = mapped_column(Integer)
    export_experience: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    export_countries: Mapped[str | None] = mapped_column(Text)
    main_industries: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    verification_level: Mapped[str] = mapped_column(String(40), default="UNVERIFIED", nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    company: Mapped["Company"] = relationship(back_populates="supplier_profile")
    capabilities: Mapped[list["SupplierCapability"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")


class SupplierCapability(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "supplier_capabilities"

    supplier_profile_id: Mapped[str] = mapped_column(ForeignKey("supplier_profiles.id", ondelete="CASCADE"), nullable=False)
    process: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    materials: Mapped[list[str] | None] = mapped_column(JSON)
    min_order_quantity: Mapped[int | None] = mapped_column(Integer)
    max_part_size: Mapped[str | None] = mapped_column(String(120))
    tolerance_level: Mapped[str | None] = mapped_column(String(120))
    surface_treatments: Mapped[list[str] | None] = mapped_column(JSON)
    has_tooling_capability: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_design_support: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_qc_team: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lead_time_sample_days: Mapped[int | None] = mapped_column(Integer)
    lead_time_mass_days: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)

    supplier: Mapped[SupplierProfile] = relationship(back_populates="capabilities")
