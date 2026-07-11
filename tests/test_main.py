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
