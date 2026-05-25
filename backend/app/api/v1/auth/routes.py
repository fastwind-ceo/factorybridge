from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, MeResponse, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.common import APIResponse
from app.security.dependencies import get_current_user
from app.security.jwt import TokenError, create_access_token, create_refresh_token, decode_token
from app.services.audit_service import log_action
from app.services.auth_service import authenticate_user, get_user_by_id, register_user_with_company, user_roles

router = APIRouter(prefix="/auth", tags=["auth"])


def build_token_response(user: User) -> TokenResponse:
    roles = user_roles(user)
    return TokenResponse(
        access_token=create_access_token(user.id, roles),
        refresh_token=create_refresh_token(user.id),
        user={"id": user.id, "email": user.email, "roles": roles},
    )


@router.post("/register", response_model=APIResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user, company = register_user_with_company(db, payload)
    return APIResponse(data={"user_id": user.id, "company_id": company.id, "email": user.email})


@router.post("/login", response_model=APIResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    log_action(db, actor_user_id=user.id, action="USER_LOGIN", object_type="USER", object_id=user.id)
    db.commit()
    return APIResponse(data=build_token_response(user).model_dump())


@router.post("/refresh", response_model=APIResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        decoded = decode_token(payload.refresh_token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token") from exc
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user_id = decoded.get("sub")
    user = get_user_by_id(db, user_id) if isinstance(user_id, str) else None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return APIResponse(data=build_token_response(user).model_dump())


@router.get("/me", response_model=APIResponse)
def me(current_user: User = Depends(get_current_user)):
    companies = [
        {
            "id": membership.company.id,
            "name": membership.company.name,
            "company_type": membership.company.company_type,
        }
        for membership in current_user.memberships
    ]
    data = MeResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        roles=user_roles(current_user),
        companies=companies,
    )
    return APIResponse(data=data.model_dump())
