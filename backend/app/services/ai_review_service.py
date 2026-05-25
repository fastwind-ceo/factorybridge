from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ManufacturingProcess, RFQStatus, RFQType, UserRole
from app.models.rfq import RFQ, RFQAIReview
from app.models.user import User
from app.services.audit_service import log_action
from app.services.auth_service import user_roles
from app.services.rfq_service import can_view_rfq, serialize_rfq

AI_PROVIDER = "factorybridge-rule-engine"
AI_MODEL_NAME = "factorybridge-ai-mvp-v1"


@dataclass(frozen=True)
class MissingField:
    field: str
    priority: str
    question_ru: str
    question_en: str
    why_needed: str

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def ensure_ai_access(user: User, rfq: RFQ) -> None:
    if not can_view_rfq(user, rfq):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ access denied")


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def _keyword_text(rfq: RFQ) -> str:
    parts = [rfq.title or "", rfq.description or "", rfq.category or ""]
    if rfq.technical_spec:
        spec = rfq.technical_spec
        parts.extend([
            spec.material or "",
            spec.material_grade or "",
            spec.technical_notes or "",
            spec.working_environment or "",
            spec.quality_requirements or "",
        ])
    return " ".join(parts).lower()


def classify_process(rfq: RFQ) -> tuple[str, list[str], float, str]:
    if rfq.technical_spec and rfq.technical_spec.suggested_process:
        return (
            rfq.technical_spec.suggested_process,
            [],
            0.92,
            "Manufacturing process is already specified in the technical specification.",
        )

    text = _keyword_text(rfq)
    category = (rfq.category or "").upper()
    rfq_type = rfq.rfq_type

    rules: list[tuple[str, list[str], str, list[str]]] = [
        (ManufacturingProcess.PLASTIC_INJECTION_MOLDING.value, ["plastic", "пласт", "abs", "pp", "pom", "injection", "molding", "корпус пластиков"], "Plastic or polymer terms suggest injection molding.", [ManufacturingProcess.CNC_MACHINING.value]),
        (ManufacturingProcess.CNC_MACHINING.value, ["cnc", "machining", "мехобработ", "чпу", "вал", "втул", "фланец", "bracket", "bracket", "axis"], "Precision part / machining keywords suggest CNC machining.", [ManufacturingProcess.METAL_CASTING.value]),
        (ManufacturingProcess.METAL_CASTING.value, ["casting", "cast", "лить", "лит", "корпус насоса", "чугун", "cast iron"], "Casting keywords and metal body terms suggest metal casting.", [ManufacturingProcess.CNC_MACHINING.value]),
        (ManufacturingProcess.METAL_STAMPING.value, ["stamping", "штамп", "sheet", "лист", "пластина", "washer"], "Sheet or stamping terms suggest metal stamping / sheet metal fabrication.", [ManufacturingProcess.SHEET_METAL.value]),
        (ManufacturingProcess.RUBBER_MOLDING.value, ["rubber", "резин", "seal", "gasket", "уплот", "манжет"], "Rubber/sealing terms suggest rubber molding.", [ManufacturingProcess.SILICONE_MOLDING.value, ManufacturingProcess.PU_CASTING.value]),
        (ManufacturingProcess.TOOLING_MOLD_MAKING.value, ["mold", "tooling", "press-form", "пресс-форм", "оснаст"], "Tooling terms suggest mold/tooling production.", []),
    ]

    if "CNC" in category:
        return ManufacturingProcess.CNC_MACHINING.value, [ManufacturingProcess.METAL_CASTING.value], 0.78, "RFQ category indicates CNC parts."
    if "CAST" in category:
        return ManufacturingProcess.METAL_CASTING.value, [ManufacturingProcess.CNC_MACHINING.value], 0.78, "RFQ category indicates cast parts."
    if "RUBBER" in category:
        return ManufacturingProcess.RUBBER_MOLDING.value, [ManufacturingProcess.SILICONE_MOLDING.value], 0.78, "RFQ category indicates rubber parts."
    if "PLASTIC" in category:
        return ManufacturingProcess.PLASTIC_INJECTION_MOLDING.value, [ManufacturingProcess.CNC_MACHINING.value], 0.78, "RFQ category indicates plastic parts."

    for process, words, reason, alternatives in rules:
        if any(word in text for word in words):
            return process, alternatives, 0.74, reason

    if rfq_type == RFQType.BY_3D_MODEL.value:
        return ManufacturingProcess.CNC_MACHINING.value, [ManufacturingProcess.PLASTIC_INJECTION_MOLDING.value], 0.55, "3D model based RFQ often starts with CNC/prototyping unless volume indicates tooling."
    if rfq_type == RFQType.BY_PHOTO.value or rfq_type == RFQType.BY_SAMPLE.value:
        return ManufacturingProcess.UNKNOWN.value, [], 0.35, "Photo/sample RFQ requires human review and more technical data before process classification."

    return ManufacturingProcess.UNKNOWN.value, [], 0.30, "Insufficient structured data to classify manufacturing process confidently."


def build_missing_fields(rfq: RFQ) -> list[dict]:
    missing: list[MissingField] = []
    spec = rfq.technical_spec
    log = rfq.logistics_spec
    comm = rfq.commercial_spec

    if not _has_text(rfq.description):
        missing.append(MissingField("description", "HIGH", "Опишите назначение и требования к изделию.", "Please describe the part application and requirements.", "Suppliers need context to evaluate manufacturability and risk."))
    if not rfq.quantity:
        missing.append(MissingField("quantity", "HIGH", "Укажите количество первой партии.", "Please specify the first batch quantity.", "Quantity affects process choice, tooling economics and unit price."))
    if not _has_text(rfq.unit):
        missing.append(MissingField("unit", "MEDIUM", "Укажите единицу измерения: шт., комплект, кг и т.д.", "Please specify the unit: pcs, set, kg, etc.", "Units are required for comparable supplier quotations."))

    if not spec:
        missing.append(MissingField("technical_spec", "HIGH", "Заполните технический блок заявки.", "Please complete the technical specification block.", "Technical data is required before supplier tendering."))
    else:
        if not _has_text(spec.material):
            missing.append(MissingField("material", "HIGH", "Укажите материал изделия.", "Please specify the material.", "Material affects price, production route and quality control."))
        if not _has_text(spec.material_grade):
            missing.append(MissingField("material_grade", "MEDIUM", "Уточните марку материала, если она известна.", "Please specify material grade if known.", "Material grade improves quotation accuracy."))
        if not _has_text(spec.tolerances):
            missing.append(MissingField("tolerances", "MEDIUM", "Укажите допуски или подтвердите общие допуски.", "Please specify tolerances or confirm general tolerances are acceptable.", "Tolerance level may significantly affect cost."))
        if not (spec.drawing_available or spec.model_3d_available or spec.sample_available or rfq.files):
            missing.append(MissingField("technical_files", "HIGH", "Приложите чертёж, 3D-модель, фото или укажите наличие образца.", "Please attach drawing, 3D model, photo or confirm sample availability.", "Suppliers need technical reference to quote."))
        if not _has_text(spec.surface_finish):
            missing.append(MissingField("surface_finish", "LOW", "Укажите требования к покрытию/поверхности, если они есть.", "Please specify surface finish requirements if any.", "Surface treatment affects price and lead time."))

    if not _has_text(rfq.delivery_country) and not (log and _has_text(log.destination_country)):
        missing.append(MissingField("delivery_country", "MEDIUM", "Укажите страну поставки.", "Please specify destination country.", "Delivery destination is required for landed cost estimate."))
    if not _has_text(rfq.delivery_city) and not (log and _has_text(log.destination_city)):
        missing.append(MissingField("delivery_city", "LOW", "Укажите город поставки.", "Please specify destination city.", "City improves logistics estimation."))
    if comm and comm.requires_tooling and not comm.expected_tooling_budget:
        missing.append(MissingField("tooling_budget", "LOW", "Укажите ориентир по бюджету на оснастку, если он есть.", "Please specify expected tooling budget if available.", "Tooling budget helps filter unrealistic proposals."))

    return [item.as_dict() for item in missing]


def build_risk_flags(rfq: RFQ, missing_fields: list[dict], process: str) -> list[dict]:
    flags: list[dict] = []
    missing_codes = {item["field"] for item in missing_fields}
    if "technical_spec" in missing_codes or "technical_files" in missing_codes:
        flags.append({"type": "TECHNICAL_INCOMPLETE", "severity": "HIGH", "message": "RFQ lacks sufficient technical data for reliable supplier quotation."})
    if "material" in missing_codes or "material_grade" in missing_codes:
        flags.append({"type": "MISSING_MATERIAL", "severity": "MEDIUM", "message": "Material data is incomplete; quotation accuracy may be reduced."})
    if "tolerances" in missing_codes:
        flags.append({"type": "MISSING_TOLERANCES", "severity": "MEDIUM", "message": "Tolerances are not specified; suppliers may quote using assumptions."})
    if process == ManufacturingProcess.UNKNOWN.value:
        flags.append({"type": "UNCLEAR_PROCESS", "severity": "MEDIUM", "message": "Manufacturing process is unclear and requires operator/engineer review."})
    if rfq.quantity and rfq.quantity < 10 and process in {ManufacturingProcess.PLASTIC_INJECTION_MOLDING.value, ManufacturingProcess.DIE_CASTING.value, ManufacturingProcess.METAL_STAMPING.value}:
        flags.append({"type": "LOW_VOLUME_HIGH_TOOLING_COST", "severity": "MEDIUM", "message": "Low quantity may be uneconomic for tooling-based production."})
    text = _keyword_text(rfq)
    if any(word in text for word in ["weapon", "military", "боеприп", "оруж", "missile", "drone"]):
        flags.append({"type": "POSSIBLE_COMPLIANCE_RISK", "severity": "CRITICAL", "message": "RFQ contains terms that require compliance review before processing."})
    if rfq.rfq_type == RFQType.IMPORTED_PART_ALTERNATIVE.value:
        flags.append({"type": "POSSIBLE_IP_RISK", "severity": "MEDIUM", "message": "Imported part alternative requires functional-analog framing and IP risk review."})
    if not rfq.delivery_country and not (rfq.logistics_spec and rfq.logistics_spec.destination_country):
        flags.append({"type": "LOGISTICS_DATA_MISSING", "severity": "LOW", "message": "Destination data is incomplete; landed cost cannot be estimated accurately."})
    return flags


def calculate_completeness_score(rfq: RFQ, missing_fields: list[dict]) -> int:
    score = 0
    # Basic info, max 20.
    if _has_text(rfq.title):
        score += 5
    if _has_text(rfq.description):
        score += 5
    if rfq.quantity:
        score += 5
    if _has_text(rfq.unit):
        score += 5

    # Technical data, max 30.
    spec = rfq.technical_spec
    if spec:
        if _has_text(spec.material):
            score += 7
        if _has_text(spec.material_grade):
            score += 5
        if _has_text(spec.tolerances):
            score += 5
        if spec.drawing_available or spec.model_3d_available or spec.sample_available or rfq.files:
            score += 8
        if _has_text(spec.surface_finish) or _has_text(spec.quality_requirements) or _has_text(spec.technical_notes):
            score += 5

    # Files, max 20.
    if rfq.files:
        score += min(20, 8 + len(rfq.files) * 4)
    elif spec and (spec.drawing_available or spec.model_3d_available or spec.sample_available):
        score += 10

    # Commercial, max 10.
    comm = rfq.commercial_spec
    if comm:
        if comm.target_unit_price or comm.target_total_budget or rfq.target_price:
            score += 3
        if comm.payment_terms:
            score += 2
        if comm.deadline_for_quotes or comm.decision_deadline:
            score += 2
        score += 3
    elif rfq.target_price:
        score += 3

    # Logistics, max 10.
    log = rfq.logistics_spec
    if _has_text(rfq.delivery_country) or (log and _has_text(log.destination_country)):
        score += 4
    if _has_text(rfq.delivery_city) or (log and _has_text(log.destination_city)):
        score += 3
    if _has_text(rfq.delivery_address) or (log and _has_text(log.destination_address)) or (log and log.estimated_weight_kg):
        score += 3

    # Risk/compliance clarity, max 10.
    critical_missing = [item for item in missing_fields if item["priority"] == "HIGH"]
    score += 10 if not critical_missing else max(0, 10 - len(critical_missing) * 4)
    return min(100, max(0, score))


def readiness_level(score: int) -> str:
    if score <= 40:
        return "RAW_REQUEST"
    if score <= 60:
        return "NEEDS_CLARIFICATION"
    if score <= 80:
        return "LIMITED_SUPPLIER_REVIEW"
    return "READY_FOR_TENDER"


def generate_supplier_brief(rfq: RFQ, process: str, missing_fields: list[dict]) -> dict:
    spec = rfq.technical_spec
    material = spec.material if spec and spec.material else "to be confirmed"
    material_grade = spec.material_grade if spec and spec.material_grade else "to be confirmed"
    qty = f"{rfq.quantity:g} {rfq.unit or 'pcs'}" if rfq.quantity else "to be confirmed"
    destination = ", ".join([x for x in [rfq.delivery_city, rfq.delivery_country] if x]) or "to be confirmed"
    file_note = "Technical files are attached." if rfq.files else "Technical files/sample details need confirmation."
    missing_summary_ru = "; ".join(item["question_ru"] for item in missing_fields[:5]) or "Критичных уточнений не выявлено."
    missing_summary_en = "; ".join(item["question_en"] for item in missing_fields[:5]) or "No critical clarification detected."

    brief_ru = (
        f"Требуется изготовить изделие: {rfq.title}. "
        f"Описание: {rfq.description or 'не указано'}. "
        f"Предполагаемая технология: {process}. Материал: {material}, марка: {material_grade}. "
        f"Количество: {qty}. Поставка: {destination}. {file_note} "
        f"Поставщику необходимо указать цену за единицу, MOQ, стоимость образца/оснастки, срок образца, срок партии, условия оплаты и Incoterms. "
        f"Уточнения: {missing_summary_ru}"
    )
    brief_en = (
        f"Manufacturing RFQ: {rfq.title}. "
        f"Description: {rfq.description or 'not specified'}. "
        f"Suggested process: {process}. Material: {material}, grade: {material_grade}. "
        f"Quantity: {qty}. Destination: {destination}. {file_note} "
        f"Supplier must provide unit price, MOQ, sample/tooling cost, sample lead time, mass production lead time, payment terms and Incoterms. "
        f"Clarifications: {missing_summary_en}"
    )
    # MVP deterministic Chinese brief placeholder style; safe and transparent for offline operation.
    brief_cn = (
        f"制造询价：{rfq.title}。"
        f"说明：{rfq.description or '未提供'}。"
        f"建议工艺：{process}。材料：{material}，牌号：{material_grade}。"
        f"数量：{qty}。目的地：{destination}。"
        f"供应商需提供单价、最小起订量、样品/模具费用、样品周期、批量生产周期、付款条件和贸易条款。"
        f"需要确认的信息：{missing_summary_en}"
    )
    return {"brief_ru": brief_ru, "brief_en": brief_en, "brief_cn": brief_cn}


def build_ai_review_payload(rfq: RFQ, module: str) -> dict:
    process, alternatives, confidence, process_reason = classify_process(rfq)
    missing = build_missing_fields(rfq)
    score = calculate_completeness_score(rfq, missing)
    risks = build_risk_flags(rfq, missing, process)
    briefs = generate_supplier_brief(rfq, process, missing)
    recommended_questions = [item["question_en"] for item in missing[:8]]
    raw = {
        "success": True,
        "confidence": confidence,
        "summary": f"RFQ completeness is {score}%. Suggested process: {process}.",
        "data": {
            "completeness_score": score,
            "readiness_level": readiness_level(score),
            "primary_process": process,
            "alternative_processes": alternatives,
            "process_reasoning_summary": process_reason,
            "missing_fields": missing,
            "risk_flags": risks,
            "recommended_questions": recommended_questions,
            "supplier_brief_ru": briefs["brief_ru"],
            "supplier_brief_en": briefs["brief_en"],
            "supplier_brief_cn": briefs["brief_cn"],
        },
        "warnings": risks,
        "requires_human_review": True,
    }
    return raw


def serialize_ai_review(review: RFQAIReview) -> dict:
    return {
        "id": review.id,
        "rfq_id": review.rfq_id,
        "review_type": review.review_type,
        "provider": review.provider,
        "model_name": review.model_name,
        "completeness_score": int(review.completeness_score) if review.completeness_score is not None else None,
        "suggested_process": review.suggested_process,
        "suggested_category": review.suggested_category,
        "missing_fields": review.missing_fields,
        "risk_flags": review.risk_flags,
        "customer_recommendations": review.customer_recommendations,
        "supplier_brief_ru": review.supplier_brief_ru,
        "supplier_brief_en": review.supplier_brief_en,
        "supplier_brief_cn": review.supplier_brief_cn,
        "raw_response": review.raw_response,
        "created_at": review.created_at.isoformat(),
    }


def run_ai_review(db: Session, rfq: RFQ, user: User, review_type: str = "COMPLETENESS_CHECK") -> tuple[RFQAIReview, bool]:
    ensure_ai_access(user, rfq)
    payload = build_ai_review_payload(rfq, review_type)
    data = payload["data"]
    review = RFQAIReview(
        rfq_id=rfq.id,
        review_type=review_type,
        provider=AI_PROVIDER,
        model_name=AI_MODEL_NAME,
        completeness_score=data["completeness_score"],
        suggested_process=data["primary_process"],
        suggested_category=rfq.category,
        missing_fields=data["missing_fields"],
        risk_flags=data["risk_flags"],
        customer_recommendations="; ".join(data["recommended_questions"]),
        supplier_brief_ru=data["supplier_brief_ru"],
        supplier_brief_en=data["supplier_brief_en"],
        supplier_brief_cn=data["supplier_brief_cn"],
        raw_response=payload,
    )
    db.add(review)
    status_updated = False
    if rfq.status == RFQStatus.SUBMITTED.value:
        old = rfq.status
        rfq.status = RFQStatus.AI_REVIEWED.value
        status_updated = True
        from app.models.rfq import RFQStatusHistory
        db.add(RFQStatusHistory(rfq_id=rfq.id, old_status=old, new_status=rfq.status, changed_by_user_id=user.id, comment="AI review completed"))
    log_action(db, actor_user_id=user.id, action="AI_RFQ_REVIEW_CREATED", object_type="RFQ", object_id=rfq.id, after_data={"review_type": review_type, "score": data["completeness_score"]})
    db.commit()
    db.refresh(review)
    return review, status_updated


def list_ai_reviews(db: Session, rfq: RFQ, user: User) -> list[RFQAIReview]:
    ensure_ai_access(user, rfq)
    stmt = select(RFQAIReview).where(RFQAIReview.rfq_id == rfq.id).order_by(RFQAIReview.created_at.desc())
    return list(db.scalars(stmt).all())
