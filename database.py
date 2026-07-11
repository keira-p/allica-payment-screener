import sqlite3

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
