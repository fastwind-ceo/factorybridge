from pydantic import BaseModel, Field


class LandedCostCreate(BaseModel):
    calculation_name: str | None = None
    currency: str = Field(default="USD", min_length=3, max_length=8)
    quantity: float | None = Field(default=None, gt=0)
    factory_unit_price: float | None = Field(default=None, gt=0)
    tooling_cost: float | None = Field(default=None, ge=0)
    sample_cost: float | None = Field(default=None, ge=0)
    packaging_cost: float | None = Field(default=None, ge=0)
    china_local_logistics: float = Field(default=0, ge=0)
    export_handling_cost: float = Field(default=0, ge=0)
    international_freight: float = Field(default=0, ge=0)
    insurance_cost: float = Field(default=0, ge=0)
    customs_clearance_cost: float = Field(default=0, ge=0)
    duty_rate: float = Field(default=0, ge=0, le=100)
    vat_rate: float = Field(default=0, ge=0, le=100)
    certification_cost: float = Field(default=0, ge=0)
    local_delivery_cost: float = Field(default=0, ge=0)
    platform_fee_rate: float = Field(default=0, ge=0, le=100)
    margin_rate: float = Field(default=0, ge=0, le=100)
    risk_reserve_rate: float = Field(default=0, ge=0, le=100)
    notes: str | None = None


class LandedCostUpdate(BaseModel):
    calculation_name: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    factory_unit_price: float | None = Field(default=None, gt=0)
    tooling_cost: float | None = Field(default=None, ge=0)
    sample_cost: float | None = Field(default=None, ge=0)
    packaging_cost: float | None = Field(default=None, ge=0)
    china_local_logistics: float | None = Field(default=None, ge=0)
    export_handling_cost: float | None = Field(default=None, ge=0)
    international_freight: float | None = Field(default=None, ge=0)
    insurance_cost: float | None = Field(default=None, ge=0)
    customs_clearance_cost: float | None = Field(default=None, ge=0)
    duty_rate: float | None = Field(default=None, ge=0, le=100)
    vat_rate: float | None = Field(default=None, ge=0, le=100)
    certification_cost: float | None = Field(default=None, ge=0)
    local_delivery_cost: float | None = Field(default=None, ge=0)
    platform_fee_rate: float | None = Field(default=None, ge=0, le=100)
    margin_rate: float | None = Field(default=None, ge=0, le=100)
    risk_reserve_rate: float | None = Field(default=None, ge=0, le=100)
    notes: str | None = None
