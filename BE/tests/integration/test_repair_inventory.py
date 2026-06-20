import pytest

from tests.conftest import login


CASE_PAYLOAD = {
    "customer_name": "Jane Doe",
    "customer_phone": "0641112233",
    "device_type": "Laptop",
    "device_brand": "Dell",
    "device_model": "XPS 13",
    "reported_issue": "Screen flickering",
}


@pytest.mark.integration
def test_repair_event_deducts_part_stock(seeded_client) -> None:
    client = seeded_client
    login(client)

    case_response = client.post("/api/cases", json=CASE_PAYLOAD)
    assert case_response.status_code == 201
    case_id = case_response.json()["id"]

    part_response = client.post(
        "/api/inventory/parts",
        json={
            "name": "SSD 512GB",
            "unit_price": "8000.00",
            "quantity_on_hand": 5,
        },
    )
    assert part_response.status_code == 201
    part_id = part_response.json()["id"]

    repair_response = client.post(
        f"/api/cases/{case_id}/events",
        json={
            "event_type": "repair",
            "description": "Replaced storage drive",
            "parts_used": [{"part_id": part_id, "quantity": 2}],
        },
    )
    assert repair_response.status_code == 201
    assert repair_response.json()["parts_used"][0]["part_name"] == "SSD 512GB"
    assert repair_response.json()["parts_used"][0]["quantity"] == 2

    part_detail = client.get(f"/api/inventory/parts/{part_id}")
    assert part_detail.status_code == 200
    assert part_detail.json()["quantity_on_hand"] == 3
