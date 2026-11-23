import os
import sqlite3

DB_PATH = os.path.join("data", "bank_simulator.db")
DATA_DIR = "data"

def init_database():
    """Creeaza folderul data și tabelele bazei de date daca nu exista."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            iban TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            account_name TEXT NOT NULL,
            currency TEXT DEFAULT 'RON',
            balance REAL DEFAULT 0.0,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_iban TEXT,
            target_iban TEXT,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (source_iban) REFERENCES accounts(iban),
            FOREIGN KEY (target_iban) REFERENCES accounts(iban)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            beneficiary_name TEXT NOT NULL,
            iban TEXT NOT NULL,
            bank_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()