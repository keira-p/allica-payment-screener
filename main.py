from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Allica Payment Screener")


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


@app.get("/")
def read_root():
    return {"message": "Payment screening service is running"}


@app.post("/payments/screen")
def screen_payment(payment: Payment):
    return {
        "payment_id": payment.payment_id,
        "message": "Payment received for screening",
    }
