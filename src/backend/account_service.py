import sqlite3
import os
import hashlib

DB_PATH = os.path.join("data", "bank_simulator.db")

def get_user_accounts(user_id: int):
    """Returneaza toate conturile bancare asociate unui utilizator."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT iban, account_name, currency, balance, status 
        FROM accounts WHERE user_id = ?
    """, (user_id,))
    accounts = cursor.fetchall()
    conn.close()
    return accounts