from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid4().hex[:10]}@example.com"


def register_and_login(company_type: str, prefix: str):
    init_db()
    email = unique_email(prefix)
    password = "StrongPassword123"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "company_name": f"{prefix} Company",
            "company_type": company_type,
        },
    )
    assert reg.status_code == 200, reg.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return reg.json()["data"], {"Authorization": f"Bearer {login.json()['data']['access_token']}"}


def test_full_factorybridge_workflow_customer_operator_supplier_to_order():
    customer, customer_headers = register_and_login("CUSTOMER", "customer.full.workflow")
    supplier, supplier_headers = register_and_login("SUPPLIER", "supplier.full.workflow")
    operator, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.full.workflow")

    # 1. Supplier prepares production capability before tender participation.
    profile = client.post(
        "/api/v1/suppliers/profile",
        json={
            "company_id": supplier["company_id"],
            "english_name": "Ningbo Precision CNC Factory",
            "province": "Zhejiang",
            "city": "Ningbo",
            "export_experience": True,
            "main_industries": "Industrial machinery, truck parts",
        },
        headers=supplier_headers,
    )
    assert profile.status_code == 200, profile.text
    capability = client.post(
        f"/api/v1/suppliers/{supplier['company_id']}/capabilities",
        json={
            "process": "CNC_MACHINING",
            "materials": ["ALUMINUM", "CARBON_STEEL"],
            "min_order_quantity": 50,
            "has_qc_team": True,
            "lead_time_sample_days": 7,
            "lead_time_mass_days": 25,
        },
        headers=supplier_headers,
    )
    assert capability.status_code == 200, capability.text

    # 2. Customer creates RFQ and technical blocks.
    rfq_resp = client.post(
        "/api/v1/rfqs",
        json={
            "title": "Aluminum CNC bracket pilot batch",
            "description": "Need brackets by drawing for industrial equipment.",
            "rfq_type": "BY_DRAWING",
            "category": "CNC_PARTS",
            "quantity": 500,
            "unit": "PCS",
            "currency": "USD",
            "delivery_country": "Russia",
            "delivery_city": "Moscow",
            "allows_alternative_material": True,
        },
        headers=customer_headers,
    )
    assert rfq_resp.status_code == 200, rfq_resp.text
    rfq = rfq_resp.json()["data"]

    specs = client.put(
        f"/api/v1/rfqs/{rfq['id']}/technical-specs",
        json={
            "suggested_process": "CNC_MACHINING",
            "material": "ALUMINUM",
            "material_grade": "6061-T6",
            "tolerances": "General ISO 2768-m unless specified",
            "drawing_available": True,
        },
        headers=customer_headers,
    )
    assert specs.status_code == 200, specs.text

    submitted = client.post(f"/api/v1/rfqs/{rfq['id']}/submit", headers=customer_headers)
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["data"]["status"] == "SUBMITTED"

    # 3. AI review creates score and supplier-ready brief.
    ai_review = client.post(f"/api/v1/ai/rfqs/{rfq['id']}/completeness-check", headers=operator_headers)
    assert ai_review.status_code == 200, ai_review.text
    ai_data = ai_review.json()["data"]["review"]
    assert ai_data["completeness_score"] >= 60
    assert "supplier_brief_en" in ai_data

    # 4. Operator approves RFQ and invites supplier.
    approved = client.post(
        f"/api/v1/rfqs/{rfq['id']}/status",
        json={"new_status": "APPROVED_FOR_TENDER", "comment": "Approved for pilot tender."},
        headers=operator_headers,
    )
    assert approved.status_code == 200, approved.text

    invite = client.post(
        f"/api/v1/tenders/rfqs/{rfq['id']}/invite",
        json={"supplier_company_ids": [supplier["company_id"]], "access_level": "PREVIEW"},
        headers=operator_headers,
    )
    assert invite.status_code == 200, invite.text
    invitation_id = invite.json()["data"]["items"][0]["id"]

    available = client.get("/api/v1/tenders/supplier/rfqs", headers=supplier_headers)
    assert available.status_code == 200, available.text
    assert any(item["rfq_id"] == rfq["id"] for item in available.json()["data"]["items"])

    accepted_invite = client.post(f"/api/v1/tenders/invitations/{invitation_id}/accept", headers=supplier_headers)
    assert accepted_invite.status_code == 200, accepted_invite.text

    # 5. Supplier submits quote; customer sees safe comparison.
    quote_resp = client.post(
        f"/api/v1/quotes/rfqs/{rfq['id']}",
        json={
            "unit_price": 12.5,
            "currency": "USD",
            "quantity": 500,
            "moq": 300,
            "sample_cost": 80,
            "packaging_cost": 50,
            "lead_time_sample_days": 7,
            "lead_time_mass_days": 25,
            "payment_terms": "30% deposit, 70% before shipment",
            "incoterms": "EXW",
        },
        headers=supplier_headers,
    )
    assert quote_resp.status_code == 200, quote_resp.text
    quote = quote_resp.json()["data"]
    submit_quote = client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)
    assert submit_quote.status_code == 200, submit_quote.text

    comparison = client.get(f"/api/v1/quotes/rfqs/{rfq['id']}/customer-comparison", headers=customer_headers)
    assert comparison.status_code == 200, comparison.text
    assert comparison.json()["data"]["summary"]["quote_count"] >= 1

    # 6. Operator calculates landed cost; customer accepts quote; operator creates order.
    landed = client.post(
        f"/api/v1/landed-costs/quotes/{quote['id']}",
        json={
            "calculation_name": "Pilot DDP Moscow estimate",
            "quantity": 500,
            "factory_unit_price": 12.5,
            "packaging_cost": 50,
            "china_local_logistics": 200,
            "international_freight": 900,
            "customs_clearance_cost": 250,
            "duty_rate": 5,
            "vat_rate": 20,
            "local_delivery_cost": 180,
            "platform_fee_rate": 5,
            "margin_rate": 15,
            "risk_reserve_rate": 3,
        },
        headers=operator_headers,
    )
    assert landed.status_code == 200, landed.text
    landed_data = landed.json()["data"]
    assert landed_data["final_customer_total_price"] > landed_data["factory_total_price"]

    accept_quote = client.post(f"/api/v1/quotes/{quote['id']}/accept", headers=customer_headers)
    assert accept_quote.status_code == 200, accept_quote.text
    assert accept_quote.json()["data"]["status"] == "ACCEPTED"

    order_resp = client.post(
        f"/api/v1/orders/from-quote/{quote['id']}",
        json={
            "landed_cost_id": landed_data["id"],
            "payment_terms": "50% deposit, 50% before shipment",
            "planned_ready_date": "2026-07-15",
            "planned_delivery_date": "2026-08-10",
            "notes": "STEP 016 full workflow pilot order",
        },
        headers=operator_headers,
    )
    assert order_resp.status_code == 200, order_resp.text
    order = order_resp.json()["data"]
    assert order["order_number"].startswith("FB-ORD-")
    assert order["status"] == "CREATED"
    assert len(order["timeline"]) >= 1

    # 7. Access checks and observability checks.
    customer_orders = client.get("/api/v1/orders/my", headers=customer_headers)
    assert customer_orders.status_code == 200, customer_orders.text
    assert any(item["id"] == order["id"] for item in customer_orders.json()["data"]["items"])

    supplier_orders = client.get("/api/v1/orders/my", headers=supplier_headers)
    assert supplier_orders.status_code == 200, supplier_orders.text
    assert any(item["id"] == order["id"] for item in supplier_orders.json()["data"]["items"])

    audit = client.get("/api/v1/admin/audit/logs", headers=operator_headers)
    assert audit.status_code == 200, audit.text
    actions = [item["action"] for item in audit.json()["data"]["items"]]
    assert "ORDER_CREATED" in actions

    operator_notifications = client.get("/api/v1/notifications/my", headers=operator_headers)
    assert operator_notifications.status_code == 200, operator_notifications.text
    assert operator_notifications.json()["data"]["items"]
