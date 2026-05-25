from datetime import date

from pydantic import BaseModel, Field


class QuoteCreate(BaseModel):
    unit_price: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    quantity: float | None = Field(default=None, gt=0)
    moq: float | None = Field(default=None, ge=0)
    tooling_cost: float | None = Field(default=None, ge=0)
    sample_cost: float | None = Field(default=None, ge=0)
    packaging_cost: float | None = Field(default=None, ge=0)
    lead_time_sample_days: int | None = Field(default=None, ge=0)
    lead_time_mass_days: int | None = Field(default=None, ge=0)
    payment_terms: str | None = None
    incoterms: str | None = None
    valid_until: date | None = None
    estimated_weight_kg: float | None = Field(default=None, ge=0)
    estimated_volume_cbm: float | None = Field(default=None, ge=0)
    alternative_material: str | None = None
    alternative_process: str | None = None
    supplier_comments: str | None = None


class QuoteUpdate(BaseModel):
    unit_price: float | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=8)
    quantity: float | None = Field(default=None, gt=0)
    moq: float | None = Field(default=None, ge=0)
    tooling_cost: float | None = Field(default=None, ge=0)
    sample_cost: float | None = Field(default=None, ge=0)
    packaging_cost: float | None = Field(default=None, ge=0)
    lead_time_sample_days: int | None = Field(default=None, ge=0)
    lead_time_mass_days: int | None = Field(default=None, ge=0)
    payment_terms: str | None = None
    incoterms: str | None = None
    valid_until: date | None = None
    estimated_weight_kg: float | None = Field(default=None, ge=0)
    estimated_volume_cbm: float | None = Field(default=None, ge=0)
    alternative_material: str | None = None
    alternative_process: str | None = None
    supplier_comments: str | None = None
    operator_notes: str | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)
