from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Quote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quotes"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    supplier_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    submitted_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    quote_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="DRAFT", index=True, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    quantity: Mapped[float | None] = mapped_column(Numeric(18, 3))
    moq: Mapped[float | None] = mapped_column(Numeric(18, 3))
    tooling_cost: Mapped[float | None] = mapped_column(Numeric(18, 2))
    sample_cost: Mapped[float | None] = mapped_column(Numeric(18, 2))
    packaging_cost: Mapped[float | None] = mapped_column(Numeric(18, 2))
    lead_time_sample_days: Mapped[int | None] = mapped_column(Numeric(10, 0))
    lead_time_mass_days: Mapped[int | None] = mapped_column(Numeric(10, 0))
    payment_terms: Mapped[str | None] = mapped_column(Text)
    incoterms: Mapped[str | None] = mapped_column(String(20))
    valid_until: Mapped[date | None] = mapped_column(Date)
    estimated_weight_kg: Mapped[float | None] = mapped_column(Numeric(18, 3))
    estimated_volume_cbm: Mapped[float | None] = mapped_column(Numeric(18, 3))
    alternative_material: Mapped[str | None] = mapped_column(Text)
    alternative_process: Mapped[str | None] = mapped_column(Text)
    supplier_comments: Mapped[str | None] = mapped_column(Text)
    operator_notes: Mapped[str | None] = mapped_column(Text)
    risk_score: Mapped[int | None] = mapped_column(Numeric(3, 0))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rfq: Mapped["RFQ"] = relationship()
    supplier_company: Mapped["Company"] = relationship()


class QuoteComparisonNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quote_comparison_notes"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id", ondelete="CASCADE"), index=True, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    price_score: Mapped[int | None] = mapped_column(Numeric(3, 0))
    delivery_score: Mapped[int | None] = mapped_column(Numeric(3, 0))
    quality_score: Mapped[int | None] = mapped_column(Numeric(3, 0))
    risk_score: Mapped[int | None] = mapped_column(Numeric(3, 0))
    overall_score: Mapped[int | None] = mapped_column(Numeric(3, 0))
    notes: Mapped[str | None] = mapped_column(Text)

    quote: Mapped[Quote] = relationship()
