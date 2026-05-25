from datetime import datetime

from pydantic import BaseModel, Field


class TenderInviteCreate(BaseModel):
    supplier_company_ids: list[str] = Field(min_length=1)
    deadline: datetime | None = None
    access_level: str = Field(default="PREVIEW")
    message: str | None = None


class TenderInvitationDecision(BaseModel):
    reason: str | None = None
