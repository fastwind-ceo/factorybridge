from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.landed_cost import LandedCost
from app.models.quote import Quote
from app.models.rfq import RFQ
from app.models.user import User
from app.schemas.landed_cost import LandedCostCreate, LandedCostUpdate
from app.services.audit_service import log_action
from app.services.auth_service import user_roles
from app.services.notification_service import notify_company
from app.services.quote_service import get_quote_or_404
from app.services.rfq_service import get_rfq_or_404, user_company_ids


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def money(value: float | Decimal | None, places: str = "0.01") -> Decimal:
    d = Decimal(str(value or 0))
    return d.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def pct(value: float | Decimal | None) -> Decimal:
    return Decimal(str(value or 0)) / Decimal("100")


def customer_can_view_landed_cost(user: User, rfq: RFQ) -> bool:
    return rfq.customer_company_id in user_company_ids(user)


def get_landed_cost_or_404(db: Session, landed_cost_id: str) -> LandedCost:
    landed_cost = db.get(LandedCost, landed_cost_id)
    if not landed_cost:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Landed cost not found")
    return landed_cost


def calculate_values(quote: Quote, payload: LandedCostCreate | LandedCostUpdate, *, existing: LandedCost | None = None) -> dict:
    def pick(name: str, fallback=None):
        value = getattr(payload, name, None)
        if value is not None:
            return value
        if existing is not None:
            return getattr(existing, name)
        return fallback

    quantity = money(pick("quantity", quote.quantity or quote.rfq.quantity or 1), "0.001")
    factory_unit_price = money(pick("factory_unit_price", quote.unit_price), "0.0001")
    tooling_cost = money(pick("tooling_cost", quote.tooling_cost))
    sample_cost = money(pick("sample_cost", quote.sample_cost))
    packaging_cost = money(pick("packaging_cost", quote.packaging_cost))
    china_local_logistics = money(pick("china_local_logistics", 0))
    export_handling_cost = money(pick("export_handling_cost", 0))
    international_freight = money(pick("international_freight", 0))
    insurance_cost = money(pick("insurance_cost", 0))
    customs_clearance_cost = money(pick("customs_clearance_cost", 0))
    certification_cost = money(pick("certification_cost", 0))
    local_delivery_cost = money(pick("local_delivery_cost", 0))
    duty_rate = money(pick("duty_rate", 0), "0.0001")
    vat_rate = money(pick("vat_rate", 0), "0.0001")
    platform_fee_rate = money(pick("platform_fee_rate", 0), "0.0001")
    margin_rate = money(pick("margin_rate", 0), "0.0001")
    risk_reserve_rate = money(pick("risk_reserve_rate", 0), "0.0001")

    factory_total_price = money(factory_unit_price * quantity)
    customs_base = money(factory_total_price + tooling_cost + sample_cost + packaging_cost + china_local_logistics + export_handling_cost + international_freight + insurance_cost)
    duty_amount = money(customs_base * pct(duty_rate))
    vat_base = money(customs_base + duty_amount + customs_clearance_cost + certification_cost)
    vat_amount = money(vat_base * pct(vat_rate))
    final_total_cost = money(vat_base + vat_amount + local_delivery_cost)
    platform_fee_amount = money(final_total_cost * pct(platform_fee_rate))
    margin_amount = money(final_total_cost * pct(margin_rate))
    risk_reserve_amount = money(final_total_cost * pct(risk_reserve_rate))
    final_customer_total_price = money(final_total_cost + platform_fee_amount + margin_amount + risk_reserve_amount)
    final_unit_cost = money(final_total_cost / quantity, "0.0001") if quantity else Decimal("0")
    final_customer_unit_price = money(final_customer_total_price / quantity, "0.0001") if quantity else Decimal("0")

    return {k: float(v) if isinstance(v, Decimal) else v for k, v in {
        "quantity": quantity,
        "factory_unit_price": factory_unit_price,
        "factory_total_price": factory_total_price,
        "tooling_cost": tooling_cost,
        "sample_cost": sample_cost,
        "packaging_cost": packaging_cost,
        "china_local_logistics": china_local_logistics,
        "export_handling_cost": export_handling_cost,
        "international_freight": international_freight,
        "insurance_cost": insurance_cost,
        "customs_clearance_cost": customs_clearance_cost,
        "duty_rate": duty_rate,
        "duty_amount": duty_amount,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "certification_cost": certification_cost,
        "local_delivery_cost": local_delivery_cost,
        "platform_fee_rate": platform_fee_rate,
        "platform_fee_amount": platform_fee_amount,
        "margin_rate": margin_rate,
        "margin_amount": margin_amount,
        "risk_reserve_rate": risk_reserve_rate,
        "risk_reserve_amount": risk_reserve_amount,
        "final_total_cost": final_total_cost,
        "final_unit_cost": final_unit_cost,
        "final_customer_total_price": final_customer_total_price,
        "final_customer_unit_price": final_customer_unit_price,
    }.items()}


def create_landed_cost(db: Session, user: User, quote_id: str, payload: LandedCostCreate) -> LandedCost:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can create landed cost")
    quote = get_quote_or_404(db, quote_id)
    values = calculate_values(quote, payload)
    landed_cost = LandedCost(
        rfq_id=quote.rfq_id,
        quote_id=quote.id,
        created_by_user_id=user.id,
        calculation_name=payload.calculation_name or "Delivered estimate",
        currency=payload.currency or quote.currency,
        notes=payload.notes,
        **values,
    )
    db.add(landed_cost)
    db.flush()
    log_action(db, actor_user_id=user.id, action="LANDED_COST_CREATED", object_type="LANDED_COST", object_id=landed_cost.id, after_data={"quote_id": quote_id})
    rfq = db.get(RFQ, quote.rfq_id)
    if rfq:
        notify_company(db, company_id=rfq.customer_company_id, title="Landed cost prepared", message=f"Delivered price calculation is ready for {rfq.rfq_number}", notification_type="LANDED_COST_CREATED", object_type="LANDED_COST", object_id=landed_cost.id)
    db.commit()
    db.refresh(landed_cost)
    return landed_cost


def update_landed_cost(db: Session, user: User, landed_cost: LandedCost, payload: LandedCostUpdate) -> LandedCost:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can update landed cost")
    quote = get_quote_or_404(db, landed_cost.quote_id)
    values = calculate_values(quote, payload, existing=landed_cost)
    for key, value in values.items():
        setattr(landed_cost, key, value)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key in {"calculation_name", "notes"}:
            setattr(landed_cost, key, value)
    log_action(db, actor_user_id=user.id, action="LANDED_COST_UPDATED", object_type="LANDED_COST", object_id=landed_cost.id)
    rfq = db.get(RFQ, landed_cost.rfq_id)
    if rfq:
        notify_company(db, company_id=rfq.customer_company_id, title="Landed cost updated", message=f"Delivered price calculation was updated for {rfq.rfq_number}", notification_type="LANDED_COST_UPDATED", object_type="LANDED_COST", object_id=landed_cost.id)
    db.commit()
    db.refresh(landed_cost)
    return landed_cost


def can_view_landed_cost(db: Session, user: User, landed_cost: LandedCost) -> bool:
    if is_operator_or_admin(user):
        return True
    rfq = db.get(RFQ, landed_cost.rfq_id)
    return bool(rfq and customer_can_view_landed_cost(user, rfq))


def list_landed_costs_for_rfq(db: Session, user: User, rfq_id: str) -> list[LandedCost]:
    rfq = get_rfq_or_404(db, rfq_id)
    if not is_operator_or_admin(user) and not customer_can_view_landed_cost(user, rfq):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Landed cost access denied")
    return list(db.scalars(select(LandedCost).where(LandedCost.rfq_id == rfq_id).order_by(LandedCost.created_at.desc())).all())


def serialize_landed_cost(landed_cost: LandedCost, *, customer_safe: bool = False) -> dict:
    data = {
        "id": landed_cost.id,
        "rfq_id": landed_cost.rfq_id,
        "quote_id": landed_cost.quote_id,
        "calculation_name": landed_cost.calculation_name,
        "currency": landed_cost.currency,
        "quantity": float(landed_cost.quantity),
        "factory_unit_price": float(landed_cost.factory_unit_price),
        "factory_total_price": float(landed_cost.factory_total_price),
        "tooling_cost": float(landed_cost.tooling_cost),
        "sample_cost": float(landed_cost.sample_cost),
        "packaging_cost": float(landed_cost.packaging_cost),
        "china_local_logistics": float(landed_cost.china_local_logistics),
        "export_handling_cost": float(landed_cost.export_handling_cost),
        "international_freight": float(landed_cost.international_freight),
        "insurance_cost": float(landed_cost.insurance_cost),
        "customs_clearance_cost": float(landed_cost.customs_clearance_cost),
        "duty_rate": float(landed_cost.duty_rate),
        "duty_amount": float(landed_cost.duty_amount),
        "vat_rate": float(landed_cost.vat_rate),
        "vat_amount": float(landed_cost.vat_amount),
        "certification_cost": float(landed_cost.certification_cost),
        "local_delivery_cost": float(landed_cost.local_delivery_cost),
        "final_total_cost": float(landed_cost.final_total_cost),
        "final_unit_cost": float(landed_cost.final_unit_cost),
        "final_customer_total_price": float(landed_cost.final_customer_total_price),
        "final_customer_unit_price": float(landed_cost.final_customer_unit_price),
        "notes": landed_cost.notes,
        "created_at": landed_cost.created_at.isoformat(),
        "updated_at": landed_cost.updated_at.isoformat(),
    }
    if not customer_safe:
        data.update({
            "created_by_user_id": landed_cost.created_by_user_id,
            "platform_fee_rate": float(landed_cost.platform_fee_rate),
            "platform_fee_amount": float(landed_cost.platform_fee_amount),
            "margin_rate": float(landed_cost.margin_rate),
            "margin_amount": float(landed_cost.margin_amount),
            "risk_reserve_rate": float(landed_cost.risk_reserve_rate),
            "risk_reserve_amount": float(landed_cost.risk_reserve_amount),
        })
    return data
