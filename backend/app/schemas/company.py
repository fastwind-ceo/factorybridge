from pydantic import BaseModel


class CompanyRead(BaseModel):
    id: str
    name: str
    company_type: str
    country: str | None = None
    city: str | None = None
    verification_status: str


class CompanyUpdate(BaseModel):
    name: str | None = None
    country: str | None = None
    city: str | None = None
    website: str | None = None
    description: str | None = None
