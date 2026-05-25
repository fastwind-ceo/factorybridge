from pydantic import BaseModel, Field


class AIRiskFlag(BaseModel):
    type: str
    severity: str
    message: str


class AIReviewRead(BaseModel):
    id: str
    rfq_id: str
    review_type: str
    provider: str | None = None
    model_name: str | None = None
    completeness_score: int | None = None
    suggested_process: str | None = None
    suggested_category: str | None = None
    missing_fields: list[dict] | dict | None = None
    risk_flags: list[dict] | dict | None = None
    customer_recommendations: str | None = None
    supplier_brief_ru: str | None = None
    supplier_brief_en: str | None = None
    supplier_brief_cn: str | None = None
    raw_response: dict | None = None
    created_at: str


class SupplierBriefRequest(BaseModel):
    include_chinese: bool = True
    include_quote_requirements: bool = True


class AIReviewRunResponse(BaseModel):
    review: AIReviewRead
    status_updated: bool = False
