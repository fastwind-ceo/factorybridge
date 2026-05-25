from datetime import date

from pydantic import BaseModel, Field

from app.models.enums import OrderStatus


class OrderCreateFromQuote(BaseModel):
    landed_cost_id: str | None = None
    payment_terms: str | None = None
    production_start_date: date | None = None
    planned_ready_date: date | None = None
    planned_delivery_date: date | None = None
    notes: str | None = None


class OrderStatusChange(BaseModel):
    new_status: OrderStatus
    comment: str | None = None


class OrderEventCreate(BaseModel):
    event_type: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
