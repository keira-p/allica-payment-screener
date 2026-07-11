HIGH_VALUE_NEW_PAYEE_THRESHOLD = 1000
HIGH_VALUE_NEW_PAYEE_SCORE = 40

VERY_HIGH_VALUE_THRESHOLD = 25000
VERY_HIGH_VALUE_SCORE = 50


def check_high_value_new_payee(payment):
    """Return a fraud reason when a high-value payment goes to a new payee."""

    if (
        payment.direction == "OUTBOUND"
        and payment.payee.is_new_payee
        and payment.amount > HIGH_VALUE_NEW_PAYEE_THRESHOLD
    ):
        return {
            "code": "HIGH_VALUE_NEW_PAYEE",
            "score": HIGH_VALUE_NEW_PAYEE_SCORE,
            "message": (
                f"Outbound payment of £{payment.amount:,.2f} is above the "
                f"£{HIGH_VALUE_NEW_PAYEE_THRESHOLD:,.2f} threshold "
                "for a new payee."
            ),
        }

    return None


def check_very_high_value_payment(payment):
    """Return a fraud reason when an outbound payment exceeds £25,000."""

    if (
        payment.direction == "OUTBOUND"
        and payment.amount > VERY_HIGH_VALUE_THRESHOLD
    ):
        return {
            "code": "VERY_HIGH_VALUE_PAYMENT",
            "score": VERY_HIGH_VALUE_SCORE,
            "message": (
                f"Outbound payment of £{payment.amount:,.2f} is above the "
                f"£{VERY_HIGH_VALUE_THRESHOLD:,.2f} very high-value threshold."
            ),
        }

    return None
