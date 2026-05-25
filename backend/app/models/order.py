from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True, nullable=False)
    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    supplier_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    landed_cost_id: Mapped[str | None] = mapped_column(ForeignKey("landed_costs.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="CREATED", index=True, nullable=False)
    total_amount: Mapped[float | None] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    payment_terms: Mapped[str | None] = mapped_column(Text)
    production_start_date: Mapped[date | None] = mapped_column(Date)
    planned_ready_date: Mapped[date | None] = mapped_column(Date)
    planned_delivery_date: Mapped[date | None] = mapped_column(Date)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date)
    operator_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    rfq: Mapped["RFQ"] = relationship()
    quote: Mapped["Quote"] = relationship()
    landed_cost: Mapped["LandedCost"] = relationship()
    customer_company: Mapped["Company"] = relationship(foreign_keys=[customer_company_id])
    supplier_company: Mapped["Company"] = relationship(foreign_keys=[supplier_company_id])


class OrderEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "order_events"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    order: Mapped[Order] = relationship()
