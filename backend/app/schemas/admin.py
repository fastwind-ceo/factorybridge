from pydantic import BaseModel, EmailStr


class UserAdminRead(BaseModel):
    id: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    roles: list[str]


class AssignRoleRequest(BaseModel):
    role: str
