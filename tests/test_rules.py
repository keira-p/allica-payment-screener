from types import SimpleNamespace

from rules import check_high_value_new_payee, check_very_high_value_payment, check_high_payment_velocity

def make_payment(
    amount=4500.00,
    direction="OUTBOUND",
    is_new_payee=True,
):
    """Create a simple payment object for testing the fraud rule."""

    payee = SimpleNamespace(
        is_new_payee=is_new_payee,
    )

    return SimpleNamespace(
        amount=amount,
        direction=direction,
        payee=payee,
    )


# -----------------------------
# Rule 1: high-value new payee
# -----------------------------

def test_high_value_new_payee_rule_fires():
    payment = make_payment(
        amount=4500.00,
        direction="OUTBOUND",
        is_new_payee=True,
    )

    result = check_high_value_new_payee(payment)

    assert result is not None
    assert result["code"] == "HIGH_VALUE_NEW_PAYEE"
    assert result["score"] == 40
    assert "£4,500.00" in result["message"]


def test_high_value_new_payee_rule_does_not_fire_below_threshold():
    payment = make_payment(
        amount=500.00,
        direction="OUTBOUND",
        is_new_payee=True,
    )

    result = check_high_value_new_payee(payment)

    assert result is None


def test_high_value_new_payee_rule_does_not_fire_for_existing_payee():
    payment = make_payment(
        amount=4500.00,
        direction="OUTBOUND",
        is_new_payee=False,
    )

    result = check_high_value_new_payee(payment)

    assert result is None


def test_high_value_new_payee_rule_does_not_fire_for_inbound_payment():
    payment = make_payment(
        amount=4500.00,
        direction="INBOUND",
        is_new_payee=True,
    )

    result = check_high_value_new_payee(payment)

    assert result is None


# -----------------------------
# Rule 2: very high value payment
# -----------------------------

def test_very_high_value_payment_rule_fires():
    payment = make_payment(
        amount=30000.00,
        direction="OUTBOUND",
        is_new_payee=False,
    )

    result = check_very_high_value_payment(payment)

    assert result is not None
    assert result["code"] == "VERY_HIGH_VALUE_PAYMENT"
    assert result["score"] == 50
    assert "£30,000.00" in result["message"]


def test_very_high_value_payment_rule_does_not_fire_below_threshold():
    payment = make_payment(
        amount=20000.00,
        direction="OUTBOUND",
        is_new_payee=False,
    )

    result = check_very_high_value_payment(payment)

    assert result is None


def test_very_high_value_payment_rule_does_not_fire_for_inbound_payment():
    payment = make_payment(
        amount=30000.00,
        direction="INBOUND",
        is_new_payee=False,
    )

    result = check_very_high_value_payment(payment)

    assert result is None


# -----------------------------
# Rule 3: high payment velocity
# -----------------------------

def test_high_payment_velocity_rule_fires_for_three_payments():
    result = check_high_payment_velocity(payment_count=3)

    assert result is not None
    assert result["code"] == "HIGH_PAYMENT_VELOCITY"
    assert result["score"] == 50
    assert "3 outbound payments" in result["message"]


def test_high_payment_velocity_rule_does_not_fire_for_two_payments():
    result = check_high_payment_velocity(payment_count=2)

    assert result is None


def test_high_payment_velocity_rule_fires_for_more_than_three_payments():
    result = check_high_payment_velocity(payment_count=4)

    assert result is not None
    assert result["code"] == "HIGH_PAYMENT_VELOCITY"
    assert result["score"] == 50
    assert "4 outbound payments" in result["message"]
