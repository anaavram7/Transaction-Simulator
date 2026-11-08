import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

DB_PATH = os.path.join("data", "bank_simulator.db")

def hash_password(plain_password: str, salt: str = None):
    if not salt:
        salt = secrets.token_hex(16)
    encoded = (plain_password + salt).encode('utf-8')
    password_hash = hashlib.sha256(encoded).hexdigest()
    return password_hash, salt

def seed_database():
    if not os.path.exists(DB_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Verificăm dacă tabelele au deja date
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    
    if user_count > 0:
        # Baza de date există și e deja populată, nu facem nimic (foarte rapid!)
        conn.close()
        return

    now = datetime.now().isoformat()

    # Utilizatori Heistbank
    users_data = [
        ("alex.popescu@heistbank.ro", "ParolaSigura123!", "Alexandru", "Popescu"),
        ("elena.ionescu@heistbank.ro", "BancaMea2026$", "Elena", "Ionescu"),
        ("mihai.georgescu@heistbank.ro", "Securitate99#", "Mihai", "Georgescu")
    ]

    print("[INFO] Prima pornire detectată: Se populează baza de date cu date de test...")
    user_map = {}
    for email, plain_pass, first, last in users_data:
        pwd_hash, salt = hash_password(plain_pass)
        cursor.execute("""
            INSERT INTO users (email, password_hash, salt, first_name, last_name, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (email, pwd_hash, salt, first, last, now))
        user_map[email] = cursor.lastrowid

    # Conturi bancare
    accounts_data = [
        (user_map["alex.popescu@heistbank.ro"], "RO24HEIS0001001", "Cont Principal", "RON", 2500.0),
        (user_map["elena.ionescu@heistbank.ro"], "RO24HEIS0002002", "Cont Curent", "RON", 5400.5),
        (user_map["mihai.georgescu@heistbank.ro"], "RO24HEIS0003003", "Portofel Digital", "RON", 1200.0)
    ]

    for user_id, iban, acc_name, currency, balance in accounts_data:
        cursor.execute("""
            INSERT INTO accounts (user_id, iban, account_name, currency, balance, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (user_id, iban, acc_name, currency, balance, now))

    conn.commit()
    conn.close()
    print("[SUCCES] Baza de date a fost pregătită cu succes!")