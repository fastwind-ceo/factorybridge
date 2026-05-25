from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LandedCost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "landed_costs"

    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id", ondelete="CASCADE"), index=True, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    calculation_name: Mapped[str | None] = mapped_column(String(160))
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(18, 3), nullable=False)

    factory_unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    factory_total_price: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    tooling_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    sample_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    packaging_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    china_local_logistics: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    export_handling_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    international_freight: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    insurance_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    customs_clearance_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    duty_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    duty_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    vat_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    vat_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    certification_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    local_delivery_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    platform_fee_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    platform_fee_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    margin_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    margin_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    risk_reserve_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    risk_reserve_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    final_total_cost: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    final_unit_cost: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    final_customer_total_price: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    final_customer_unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    rfq: Mapped["RFQ"] = relationship()
    quote: Mapped["Quote"] = relationship()


class LandedCostItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "landed_cost_items"

    landed_cost_id: Mapped[str] = mapped_column(ForeignKey("landed_costs.id", ondelete="CASCADE"), index=True, nullable=False)
    item_name: Mapped[str] = mapped_column(String(120), nullable=False)
    item_type: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    landed_cost: Mapped[LandedCost] = relationship()
