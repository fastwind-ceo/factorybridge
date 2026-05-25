from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.models.user import User, UserRoleModel
from app.schemas.admin import AssignRoleRequest
from app.schemas.common import APIResponse
from app.security.dependencies import require_roles
from app.services.audit_service import log_action
from app.services.auth_service import user_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=APIResponse)
def dashboard(_: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)), db: Session = Depends(get_db)):
    users_total = len(db.scalars(select(User)).all())
    companies_total = len(db.scalars(select(Company)).all())
    return APIResponse(data={"users_total": users_total, "companies_total": companies_total, "step": "004-company-supplier-profiles"})


@router.get("/users", response_model=APIResponse)
def list_users(_: User = Depends(require_roles(UserRole.ADMIN.value)), db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return APIResponse(data=[{"id": u.id, "email": u.email, "is_active": u.is_active, "roles": user_roles(u)} for u in users])


@router.post("/users/{user_id}/roles", response_model=APIResponse)
def assign_role(user_id: str, payload: AssignRoleRequest, current_user: User = Depends(require_roles(UserRole.ADMIN.value)), db: Session = Depends(get_db)):
    try:
        role = UserRole(payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown role") from exc
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if role.value not in user_roles(user):
        db.add(UserRoleModel(user_id=user.id, role=role.value))
        log_action(db, actor_user_id=current_user.id, action="ROLE_ASSIGNED", object_type="USER", object_id=user.id, after_data={"role": role.value})
        db.commit()
        db.refresh(user)
    return APIResponse(data={"id": user.id, "roles": user_roles(user)})


@router.get("/audit/logs", response_model=APIResponse)
def audit_logs(_: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)), db: Session = Depends(get_db)):
    logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc())).all()
    return APIResponse(data={"items": [
        {
            "id": item.id,
            "actor_user_id": item.actor_user_id,
            "action": item.action,
            "object_type": item.object_type,
            "object_id": item.object_id,
            "before_data": item.before_data,
            "after_data": item.after_data,
            "created_at": item.created_at.isoformat(),
        }
        for item in logs
    ], "total": len(logs)})
