from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from rules import check_high_value_new_payee, check_very_high_value_payment

from database import initialise_database, save_payment


app = FastAPI(title="Allica Payment Screener")

initialise_database()

class Payee(BaseModel):
    name: str
    sort_code: str
    account_number: str
    is_new_payee: bool
    country: str


class Payment(BaseModel):
    payment_id: str
    timestamp: datetime
    account_id: str
    amount: float
    currency: str
    direction: str
    channel: str
    device_id: str
    payee: Payee


def get_decision(risk_score):
    if risk_score >= 80:
        return "block"

    if risk_score >= 40:
        return "review"

    return "approve"


@app.get("/")
def read_root():
    return {"message": "Payment screening service is running"}


@app.post("/payments/screen")
def screen_payment(payment: Payment):
    risk_score = 0
    reasons = []

    high_value_new_payee_reason = check_high_value_new_payee(payment)

    if high_value_new_payee_reason:
        risk_score += high_value_new_payee_reason["score"]
        reasons.append(high_value_new_payee_reason)

    very_high_value_reason = check_very_high_value_payment(payment)

    if very_high_value_reason:
        risk_score += very_high_value_reason["score"]
        reasons.append(very_high_value_reason)

    decision = get_decision(risk_score)

    if reasons:
        message = f"Payment requires {decision} because one or more fraud rules were triggered."
    else:
        message = "Payment approved because no fraud rules were triggered."

    save_payment(payment)

    return {
        "payment_id": payment.payment_id,
        "decision": decision,
        "risk_score": risk_score,
        "message": message,
        "reasons": reasons,
    }
