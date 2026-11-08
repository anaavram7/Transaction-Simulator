import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

DB_PATH = os.path.join("data", "bank_simulator.db")

def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """Verifică dacă parola introdusă corespunde cu hash-ul și salt-ul din DB."""
    encoded = (plain_password + salt).encode('utf-8')
    computed_hash = hashlib.sha256(encoded).hexdigest()
    return computed_hash == stored_hash

def authenticate_user(email: str, plain_password: str):
    """Încearcă să autentifice un utilizator. Returnează datele lui dacă reușește, sau None."""
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, password_hash, salt, first_name, last_name, status 
        FROM users WHERE email = ?
    """, (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    user_id, db_email, db_password_hash, db_salt, first_name, last_name, status = user

    if status != 'ACTIVE':
        print("Contul este inactiv!")
        return None

    # Verificăm parola
    if verify_password(plain_password, db_password_hash, db_salt):
        return {
            "id": user_id,
            "email": db_email,
            "first_name": first_name,
            "last_name": last_name
        }
    
    return None

def register_user(first_name: str, last_name: str, email: str, plain_password: str):
    """Înregistrează un utilizator nou și îi creează automat un cont bancar Heistbank."""
    if not os.path.exists(DB_PATH):
        return False, "Baza de date nu există."

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Verificăm dacă emailul există deja
    cursor.execute("SELECT id FROM users WHERE email = ?;", (email,))
    if cursor.fetchone():
        conn.close()
        return False, "⚠️ Ai deja un cont asociat acestui mail!"

    now = datetime.now().isoformat()
    
    # Generăm salt și hash pentru parolă (securitate standard)
    salt = secrets.token_hex(16)
    encoded = (plain_password + salt).encode('utf-8')
    password_hash = hashlib.sha256(encoded).hexdigest()

    try:
        # 1. Inserăm utilizatorul nou
        cursor.execute("""
            INSERT INTO users (email, password_hash, salt, first_name, last_name, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (email, password_hash, salt, first_name, last_name, now))
        
        user_id = cursor.lastrowid

        # 2. Generăm un IBAN unicat cu prefixul tău cerut: RO24HEIS
        random_digits = secrets.randbelow(900000) + 100000
        new_iban = f"RO24HEIS{random_digits}"

        # 3. Creăm automat un cont bancar principal în RON cu 100.00 RON bonus de bun venit
        cursor.execute("""
            INSERT INTO accounts (iban, user_id, account_name, currency, balance, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (new_iban, user_id, "Cont Principal", "RON", 100.0, now))

        conn.commit()
        conn.close()
        return True, "Cont creat cu succes!"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Eroare: {str(e)}"