from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import ManufacturingProcess, MaterialType, RFQStatus, RFQType


class RFQCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None
    rfq_type: RFQType
    category: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = None
    target_price: float | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    delivery_country: str | None = None
    delivery_city: str | None = None
    delivery_address: str | None = None
    delivery_deadline: date | None = None
    is_recurring: bool = False
    recurring_frequency: str | None = None
    annual_volume: float | None = Field(default=None, ge=0)
    is_confidential: bool = True
    allows_alternative_material: bool = False
    allows_alternative_process: bool = False


class RFQUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    category: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = None
    target_price: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=8)
    delivery_country: str | None = None
    delivery_city: str | None = None
    delivery_address: str | None = None
    delivery_deadline: date | None = None
    is_recurring: bool | None = None
    recurring_frequency: str | None = None
    annual_volume: float | None = Field(default=None, ge=0)
    is_confidential: bool | None = None
    allows_alternative_material: bool | None = None
    allows_alternative_process: bool | None = None


class RFQStatusChange(BaseModel):
    new_status: RFQStatus
    comment: str | None = None


class RFQTechnicalSpecUpsert(BaseModel):
    suggested_process: ManufacturingProcess | None = None
    material: MaterialType | None = None
    material_grade: str | None = None
    tolerances: str | None = None
    surface_finish: str | None = None
    heat_treatment: str | None = None
    hardness: str | None = None
    working_environment: str | None = None
    temperature_range: str | None = None
    load_requirements: str | None = None
    quality_requirements: str | None = None
    testing_requirements: str | None = None
    packaging_requirements: str | None = None
    drawing_available: bool = False
    model_3d_available: bool = False
    sample_available: bool = False
    technical_notes: str | None = None


class RFQLogisticsSpecUpsert(BaseModel):
    origin_country: str | None = "China"
    origin_city: str | None = None
    destination_country: str | None = None
    destination_city: str | None = None
    destination_address: str | None = None
    preferred_incoterms: str | None = None
    preferred_transport_mode: str | None = None
    estimated_weight_kg: float | None = Field(default=None, ge=0)
    estimated_volume_cbm: float | None = Field(default=None, ge=0)
    requires_customs_clearance: bool = True
    requires_certification: bool = False
    certification_notes: str | None = None


class RFQCommercialSpecUpsert(BaseModel):
    target_unit_price: float | None = Field(default=None, ge=0)
    target_total_budget: float | None = Field(default=None, ge=0)
    current_purchase_price: float | None = Field(default=None, ge=0)
    original_part_price: float | None = Field(default=None, ge=0)
    payment_terms: str | None = None
    requires_sample: bool = True
    requires_tooling: bool = False
    expected_tooling_budget: float | None = Field(default=None, ge=0)
    deadline_for_quotes: datetime | None = None
    decision_deadline: datetime | None = None
    commercial_notes: str | None = None
