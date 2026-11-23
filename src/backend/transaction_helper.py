import os
import sqlite3
from datetime import datetime
from src.backend.auth_service import log_audit_event

DB_PATH = os.path.join("data", "bank_simulator.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def save_transaction_and_audit(
    cursor,
    user_id: int,
    source_iban: str | None,
    target_iban: str | None,
    amount: float,
    currency: str,
    tx_status: str,
    audit_action: str,
    audit_details: str,
):
    """Salveaza randul in transactions si evenimentul corespunzator in audit_logs."""
    now = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO transactions (source_iban, target_iban, amount, currency, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (source_iban, target_iban, amount, currency, tx_status, now),
    )

    log_audit_event(user_id, audit_action, audit_details, conn=cursor.connection)