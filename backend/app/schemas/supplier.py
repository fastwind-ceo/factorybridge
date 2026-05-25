from pydantic import BaseModel, Field

from app.models.enums import ManufacturingProcess, MaterialType


class SupplierProfileCreate(BaseModel):
    company_id: str | None = None
    chinese_name: str | None = None
    english_name: str | None = None
    province: str | None = None
    city: str | None = None
    factory_address: str | None = None
    year_established: int | None = Field(default=None, ge=1900, le=2100)
    employee_count: int | None = Field(default=None, ge=0)
    export_experience: bool = False
    export_countries: str | None = None
    main_industries: str | None = None
    notes: str | None = None


class SupplierProfileUpdate(BaseModel):
    chinese_name: str | None = None
    english_name: str | None = None
    province: str | None = None
    city: str | None = None
    factory_address: str | None = None
    year_established: int | None = Field(default=None, ge=1900, le=2100)
    employee_count: int | None = Field(default=None, ge=0)
    export_experience: bool | None = None
    export_countries: str | None = None
    main_industries: str | None = None
    is_available: bool | None = None
    notes: str | None = None


class SupplierCapabilityCreate(BaseModel):
    process: ManufacturingProcess
    materials: list[MaterialType] = Field(default_factory=list)
    min_order_quantity: int | None = Field(default=None, ge=0)
    max_part_size: str | None = None
    tolerance_level: str | None = None
    surface_treatments: list[str] = Field(default_factory=list)
    has_tooling_capability: bool = False
    has_design_support: bool = False
    has_qc_team: bool = False
    lead_time_sample_days: int | None = Field(default=None, ge=0)
    lead_time_mass_days: int | None = Field(default=None, ge=0)
    description: str | None = None


class SupplierVerifyRequest(BaseModel):
    verification_level: str = Field(min_length=2, max_length=60)
    company_verification_status: str | None = None
    notes: str | None = None
