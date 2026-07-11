# -----------------------------
# Rule 1: high-value new payee
# -----------------------------
HIGH_VALUE_NEW_PAYEE_THRESHOLD = 1000
HIGH_VALUE_NEW_PAYEE_SCORE = 40


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
