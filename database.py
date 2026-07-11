import sqlite3
from datetime import timedelta

DATABASE_NAME = "payments.db"


def initialise_database():
    """Create the payments table if it does not already exist."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                amount REAL NOT NULL,
                direction TEXT NOT NULL
            )
            """
        )


def save_payment(payment):
    """Save a screened payment to the database."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute(
            """
            INSERT INTO payments (
                payment_id,
                account_id,
                timestamp,
                amount,
                direction
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payment.payment_id,
                payment.account_id,
                payment.timestamp.isoformat(),
                payment.amount,
                payment.direction,
            ),
        )

def count_recent_outbound_payments(payment):
    """Count earlier outbound payments from this account in the previous 10 minutes."""

    window_start = payment.timestamp - timedelta(minutes=10)

    with sqlite3.connect(DATABASE_NAME) as connection:
        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM payments
            WHERE account_id = ?
              AND direction = 'OUTBOUND'
              AND timestamp >= ?
              AND timestamp < ?
            """,
            (
                payment.account_id,
                window_start.isoformat(),
                payment.timestamp.isoformat(),
            ),
        ).fetchone()

    return result[0]

def payment_exists(payment_id):
    """Return True when a payment ID has already been stored."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        result = connection.execute(
            """
            SELECT 1
            FROM payments
            WHERE payment_id = ?
            LIMIT 1
            """,
            (payment_id,),
        ).fetchone()

    return result is not None
