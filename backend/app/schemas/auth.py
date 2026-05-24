from pydantic import BaseModel, EmailStr, Field

from app.models.enums import CompanyType


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    company_name: str = Field(min_length=2, max_length=255)
    company_type: CompanyType = CompanyType.CUSTOMER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenUser(BaseModel):
    id: str
    email: EmailStr
    roles: list[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: TokenUser
