import database
import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def use_test_database(tmp_path, monkeypatch):
    """
    Give each test its own temporary SQLite database.

    This keeps test payments separate from the local payments.db file
    used when running the service normally.
    """

    test_database = tmp_path / "test_payments.db"

    monkeypatch.setattr(
        database,
        "DATABASE_NAME",
        str(test_database),
    )

    database.initialise_database()


def make_payment(
    payment_id="test-payment-001",
    amount=500.00,
    is_new_payee=False,
):
    """Return a valid payment request that tests can customise."""

    return {
        "payment_id": payment_id,
        "timestamp": "2026-01-15T09:32:00Z",
        "account_id": "test-account-001",
        "amount": amount,
        "currency": "GBP",
        "direction": "OUTBOUND",
        "channel": "mobile_app",
        "device_id": "ABCD123456789",
        "payee": {
            "name": "Test Payee",
            "sort_code": "00-00-00",
            "account_number": "12345678",
            "is_new_payee": is_new_payee,
            "country": "GB",
        },
    }


def test_normal_payment_is_approved():
    payment = make_payment(
        amount=500.00,
        is_new_payee=False,
    )

    response = client.post(
        "/payments/screen",
        json=payment,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["payment_id"] == "test-payment-001"
    assert result["decision"] == "approve"
    assert result["risk_score"] == 0
    assert result["reasons"] == []


def test_high_value_new_payee_payment_is_reviewed():
    payment = make_payment(
        amount=4500.00,
        is_new_payee=True,
    )

    response = client.post(
        "/payments/screen",
        json=payment,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["decision"] == "review"
    assert result["risk_score"] == 40
    assert result["reasons"][0]["code"] == "HIGH_VALUE_NEW_PAYEE"


def test_very_high_value_new_payee_payment_is_blocked():
    payment = make_payment(
        amount=30000.00,
        is_new_payee=True,
    )

    response = client.post(
        "/payments/screen",
        json=payment,
    )

    assert response.status_code == 200

    result = response.json()

    reason_codes = [
        reason["code"]
        for reason in result["reasons"]
    ]

    assert result["decision"] == "block"
    assert result["risk_score"] == 90
    assert "HIGH_VALUE_NEW_PAYEE" in reason_codes
    assert "VERY_HIGH_VALUE_PAYMENT" in reason_codes


def test_third_payment_within_ten_minutes_is_reviewed():
    payment_one = make_payment(
        payment_id="velocity-payment-001",
        amount=500.00,
        is_new_payee=False,
    )
    payment_one["timestamp"] = "2026-01-15T09:00:00Z"
    payment_one["account_id"] = "velocity-test-account"

    payment_two = make_payment(
        payment_id="velocity-payment-002",
        amount=500.00,
        is_new_payee=False,
    )
    payment_two["timestamp"] = "2026-01-15T09:04:00Z"
    payment_two["account_id"] = "velocity-test-account"

    payment_three = make_payment(
        payment_id="velocity-payment-003",
        amount=500.00,
        is_new_payee=False,
    )
    payment_three["timestamp"] = "2026-01-15T09:08:00Z"
    payment_three["account_id"] = "velocity-test-account"

    first_response = client.post(
        "/payments/screen",
        json=payment_one,
    )
    second_response = client.post(
        "/payments/screen",
        json=payment_two,
    )
    third_response = client.post(
        "/payments/screen",
        json=payment_three,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert third_response.status_code == 200

    assert first_response.json()["decision"] == "approve"
    assert second_response.json()["decision"] == "approve"

    third_result = third_response.json()

    assert third_result["decision"] == "review"
    assert third_result["risk_score"] == 50
    assert third_result["reasons"][0]["code"] == "HIGH_PAYMENT_VELOCITY"


def test_duplicate_payment_id_returns_conflict():
    payment = make_payment(
        payment_id="duplicate-payment-001",
        amount=500.00,
        is_new_payee=False,
    )

    first_response = client.post(
        "/payments/screen",
        json=payment,
    )
    duplicate_response = client.post(
        "/payments/screen",
        json=payment,
    )

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == (
        "Payment with ID duplicate-payment-001 "
        "has already been screened."
    )


def test_negative_payment_amount_is_rejected():
    payment = make_payment(
        payment_id="negative-payment-001",
        amount=-500.00,
        is_new_payee=False,
    )

    response = client.post(
        "/payments/screen",
        json=payment,
    )

    assert response.status_code == 422
