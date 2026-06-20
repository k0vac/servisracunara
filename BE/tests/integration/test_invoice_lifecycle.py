import pytest

from tests.conftest import login


CASE_PAYLOAD = {
    "customer_name": "John Smith",
    "customer_phone": "0654445566",
    "device_type": "Desktop",
    "device_brand": "HP",
    "device_model": "Pavilion",
    "reported_issue": "Won't boot",
}


@pytest.mark.integration
def test_invoice_generate_then_mark_paid_closes_case(seeded_client) -> None:
    client = seeded_client
    login(client)

    case_response = client.post("/api/cases", json=CASE_PAYLOAD)
    assert case_response.status_code == 201
    case_id = case_response.json()["id"]

    part_response = client.post(
        "/api/inventory/parts",
        json={
            "name": "RAM 8GB",
            "unit_price": "3500.00",
            "quantity_on_hand": 10,
        },
    )
    assert part_response.status_code == 201
    part_id = part_response.json()["id"]

    repair_response = client.post(
        f"/api/cases/{case_id}/events",
        json={
            "event_type": "repair",
            "description": "Installed new memory",
            "parts_used": [{"part_id": part_id, "quantity": 1}],
        },
    )
    assert repair_response.status_code == 201

    generate_response = client.post(f"/api/cases/{case_id}/invoice/generate")
    assert generate_response.status_code == 201
    invoice = generate_response.json()
    assert invoice["status"] == "pending"
    assert invoice["subtotal"] == "3500.00"
    assert invoice["tax_amount"] == "700.00"
    assert invoice["total"] == "4200.00"

    case_detail = client.get(f"/api/cases/{case_id}")
    assert case_detail.status_code == 200
    assert case_detail.json()["status"] == "awaiting_payment"
    assert case_detail.json()["is_locked"] is True

    paid_response = client.post(f"/api/cases/{case_id}/invoice/mark-paid")
    assert paid_response.status_code == 200
    assert paid_response.json()["status"] == "paid"

    closed_case = client.get(f"/api/cases/{case_id}")
    assert closed_case.status_code == 200
    assert closed_case.json()["status"] == "closed"
    assert closed_case.json()["closed_at"] is not None
