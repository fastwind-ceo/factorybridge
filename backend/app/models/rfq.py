from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RFQ(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "rfqs"

    rfq_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    customer_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    rfq_type: Mapped[str] = mapped_column(String(60), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(60), default="DRAFT", index=True, nullable=False)
    quantity: Mapped[float | None] = mapped_column(Numeric(18, 3))
    unit: Mapped[str | None] = mapped_column(String(30))
    target_price: Mapped[float | None] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    delivery_country: Mapped[str | None] = mapped_column(String(100))
    delivery_city: Mapped[str | None] = mapped_column(String(100))
    delivery_address: Mapped[str | None] = mapped_column(Text)
    delivery_deadline: Mapped[date | None] = mapped_column(Date)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurring_frequency: Mapped[str | None] = mapped_column(String(60))
    annual_volume: Mapped[float | None] = mapped_column(Numeric(18, 3))
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allows_alternative_material: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allows_alternative_process: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    operator_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    engineer_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    files: Mapped[list["RFQFile"]] = relationship(back_populates="rfq", cascade="all, delete-orphan")
    technical_spec: Mapped["RFQTechnicalSpec | None"] = relationship(back_populates="rfq", cascade="all, delete-orphan", uselist=False)
    logistics_spec: Mapped["RFQLogisticsSpec | None"] = relationship(back_populates="rfq", cascade="all, delete-orphan", uselist=False)
    commercial_spec: Mapped["RFQCommercialSpec | None"] = relationship(back_populates="rfq", cascade="all, delete-orphan", uselist=False)
    status_history: Mapped[list["RFQStatusHistory"]] = relationship(back_populates="rfq", cascade="all, delete-orphan")
    ai_reviews: Mapped[list["RFQAIReview"]] = relationship(cascade="all, delete-orphan")
    tender_invitations: Mapped[list["TenderInvitation"]] = relationship(back_populates="rfq", cascade="all, delete-orphan")


class RFQTechnicalSpec(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "rfq_technical_specs"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), unique=True, nullable=False)
    suggested_process: Mapped[str | None] = mapped_column(String(80))
    material: Mapped[str | None] = mapped_column(String(80))
    material_grade: Mapped[str | None] = mapped_column(String(120))
    tolerances: Mapped[str | None] = mapped_column(Text)
    surface_finish: Mapped[str | None] = mapped_column(Text)
    heat_treatment: Mapped[str | None] = mapped_column(Text)
    hardness: Mapped[str | None] = mapped_column(String(120))
    working_environment: Mapped[str | None] = mapped_column(Text)
    temperature_range: Mapped[str | None] = mapped_column(String(120))
    load_requirements: Mapped[str | None] = mapped_column(Text)
    quality_requirements: Mapped[str | None] = mapped_column(Text)
    testing_requirements: Mapped[str | None] = mapped_column(Text)
    packaging_requirements: Mapped[str | None] = mapped_column(Text)
    drawing_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    model_3d_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sample_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    technical_notes: Mapped[str | None] = mapped_column(Text)

    rfq: Mapped[RFQ] = relationship(back_populates="technical_spec")


class RFQLogisticsSpec(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "rfq_logistics_specs"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), unique=True, nullable=False)
    origin_country: Mapped[str | None] = mapped_column(String(100), default="China")
    origin_city: Mapped[str | None] = mapped_column(String(100))
    destination_country: Mapped[str | None] = mapped_column(String(100))
    destination_city: Mapped[str | None] = mapped_column(String(100))
    destination_address: Mapped[str | None] = mapped_column(Text)
    preferred_incoterms: Mapped[str | None] = mapped_column(String(20))
    preferred_transport_mode: Mapped[str | None] = mapped_column(String(40))
    estimated_weight_kg: Mapped[float | None] = mapped_column(Numeric(18, 3))
    estimated_volume_cbm: Mapped[float | None] = mapped_column(Numeric(18, 3))
    requires_customs_clearance: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_certification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    certification_notes: Mapped[str | None] = mapped_column(Text)

    rfq: Mapped[RFQ] = relationship(back_populates="logistics_spec")


class RFQCommercialSpec(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "rfq_commercial_specs"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), unique=True, nullable=False)
    target_unit_price: Mapped[float | None] = mapped_column(Numeric(18, 2))
    target_total_budget: Mapped[float | None] = mapped_column(Numeric(18, 2))
    current_purchase_price: Mapped[float | None] = mapped_column(Numeric(18, 2))
    original_part_price: Mapped[float | None] = mapped_column(Numeric(18, 2))
    payment_terms: Mapped[str | None] = mapped_column(Text)
    requires_sample: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_tooling: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expected_tooling_budget: Mapped[float | None] = mapped_column(Numeric(18, 2))
    deadline_for_quotes: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    commercial_notes: Mapped[str | None] = mapped_column(Text)

    rfq: Mapped[RFQ] = relationship(back_populates="commercial_spec")


class RFQFile(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "rfq_files"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    uploaded_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(80))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    file_size: Mapped[int | None] = mapped_column(Numeric(18, 0))
    storage_bucket: Mapped[str | None] = mapped_column(String(120))
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_category: Mapped[str | None] = mapped_column(String(80))
    access_level: Mapped[str] = mapped_column(String(60), default="PRIVATE", nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    rfq: Mapped[RFQ] = relationship(back_populates="files")


class RFQAIReview(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "rfq_ai_reviews"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    review_type: Mapped[str] = mapped_column(String(80), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(120))
    completeness_score: Mapped[int | None] = mapped_column(Numeric(3, 0))
    suggested_process: Mapped[str | None] = mapped_column(String(80))
    suggested_category: Mapped[str | None] = mapped_column(String(80))
    missing_fields: Mapped[dict | None] = mapped_column(JSON)
    risk_flags: Mapped[dict | None] = mapped_column(JSON)
    customer_recommendations: Mapped[str | None] = mapped_column(Text)
    supplier_brief_ru: Mapped[str | None] = mapped_column(Text)
    supplier_brief_en: Mapped[str | None] = mapped_column(Text)
    supplier_brief_cn: Mapped[str | None] = mapped_column(Text)
    raw_response: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class RFQStatusHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "rfq_status_history"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(60))
    new_status: Mapped[str] = mapped_column(String(60), nullable=False)
    changed_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    rfq: Mapped[RFQ] = relationship(back_populates="status_history")

class TenderInvitation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "tender_invitations"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    supplier_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    invited_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="INVITED", index=True, nullable=False)
    access_level: Mapped[str] = mapped_column(String(40), default="PREVIEW", nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rfq: Mapped[RFQ] = relationship(back_populates="tender_invitations")
    supplier_company: Mapped["Company"] = relationship()
