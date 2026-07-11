# Allica Payment Screener

A small FastAPI service that screens outbound payments against fraud rules and returns an `approve`, `review`, or `block` decision.

## How it works

Payments are submitted as JSON to:

`POST /payments/screen`

Each payment is evaluated against a set of fraud rules. Rules that fire contribute to a total risk score, which determines the final decision. The response includes the payment ID, decision, total risk score, an overall message, and structured reasons explaining which rules fired.

Payment history is stored in SQLite so that the service can consider an account's recent activity across multiple requests.

## Fraud rules

| Rule | Condition | Risk score |
| --- | --- | ---: |
| High-value new payee | Outbound payment to a new payee over £1,000 | +40 |
| High payment velocity | 3 or more outbound payments from the same account within 10 minutes | +50 |
| Very high-value payment | Outbound payment over £25,000 | +50 |

### Decision thresholds

| Total risk score | Decision |
| --- | --- |
| 0–39 | `approve` |
| 40–79 | `review` |
| 80+ | `block` |

These rules and thresholds are illustrative rather than intended as production fraud controls. In a production system, they would need to be calibrated using actual customer transaction behaviour, observed fraud patterns, and acceptable false-positive rates.

The very high-value threshold is set at £25,000 rather than a lower consumer-banking threshold, recognising that Allica serves business banking customers for whom larger payments may be routine.

## Setup

This service was developed and tested with Python 3.12.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the service:

```bash
uvicorn main:app --reload
```

The interactive API documentation is then available at:

`http://127.0.0.1:8000/docs`

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/payments/screen" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "1776f7f1-989f-4615-a66c-29dc38f8c636",
    "timestamp": "2026-01-15T09:32:00Z",
    "account_id": "4e66eac6-f6b3-4483-ae0f-6f5699dab930",
    "amount": 4500.00,
    "currency": "GBP",
    "direction": "OUTBOUND",
    "channel": "mobile_app",
    "device_id": "ABCD123456789",
    "payee": {
      "name": "Interview Test",
      "sort_code": "00-00-00",
      "account_number": "12345678",
      "is_new_payee": true,
      "country": "GB"
    }
  }'
```

## Example response

```json
{
  "payment_id":"1776f7f1-989f-4615-a66c-29dc38f8c636",
  "decision":"review",
  "risk_score":40,
  "message":"Payment requires review because one or more fraud rules were triggered.",
  "reasons":[
    {
      "code":"HIGH_VALUE_NEW_PAYEE",
      "score":40,
      "message":"Outbound payment of £4,500.00 is above the £1,000.00 threshold for a new payee."
    }
  ]
}

## Testing

Run the test suite with:

```bash
python -m pytest
```

The test suite covers individual fraud rules and API behaviour, including:

- `approve`, `review`, and `block` decisions
- combined risk signals
- payment velocity across multiple requests
- duplicate payment IDs
- invalid negative payment amounts

## Design decisions and assumptions

- Payments are submitted as JSON using an HTTP `POST` request because screening creates a decision and persists payment history.
- SQLite provides lightweight local persistence without requiring an external service or Docker.
- Only outbound payments contribute to the implemented fraud controls.
- The payment currently being screened is included when calculating payment velocity.
- The 10-minute velocity window is calculated using the payment's supplied timestamp, making the behaviour deterministic and straightforward to test.
- Exactly 3 payments within 10 minutes triggers the velocity rule.
- Duplicate payment IDs return HTTP `409 Conflict` rather than being processed twice.
- Zero or negative payment amounts are rejected through request validation.
- A blocked payment still returns HTTP `200 OK` because the API request was successfully processed; `block` is the fraud decision rather than an HTTP error.
- Rule scores and decision thresholds are illustrative and would require calibration against real customer and fraud data.

## Project structure

```text
.
├── main.py              # FastAPI endpoint and screening flow
├── rules.py             # Fraud rules and scoring logic
├── database.py          # SQLite persistence and payment history queries
├── tests/
│   ├── test_main.py     # API and integration tests
│   └── test_rules.py    # Unit tests for individual fraud rules
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## What I would do with more time

For a production service, I would consider:

### Evolve the fraud controls

The current rules are deliberately simple and explainable. With more time, I would:

- move rule thresholds and risk scores into configurable settings rather than hard-coding them
- support multiple currencies by converting payment values to a consistent base currency before applying value-based rules
- explore additional controls such as unusual payment amounts relative to an account's history, new or rapidly changing devices, and unusual payee behaviour
- calibrate rules against real transaction behaviour and known fraud patterns, balancing fraud detection against false positives and the impact on genuine customers

### Measure effectiveness

I would add reporting and monitoring to understand how the screening service performs in practice, including:

- how frequently individual rules fire
- overall approve, review, and block rates
- false-positive rates
- the effectiveness of individual controls at identifying confirmed fraud

### Strengthen production readiness

For a production environment, I would consider:

- richer audit records including screening decisions and reasons
- database indexes to support efficient account and timestamp queries at greater scale
- structured logging and operational monitoring
- authentication and authorisation

### Expand validation and testing

The current test suite covers the core rules, full API behaviour, payment velocity across multiple requests, duplicate payments, and invalid negative amounts. With more time, I would add:

- stronger validation of supported currencies, directions, channels, and identifier formats
- broader tests around time-window boundaries and additional unhappy paths
- tests for concurrent requests
- an automated CI workflow to run tests on every change

**Note**: I deliberately kept the scope focused on the backend service rather than adding the optional frontend. FastAPI's interactive `/docs` interface provides a simple way to submit payments and inspect responses locally.
