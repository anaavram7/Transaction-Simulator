import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

DB_PATH = os.path.join("data", "bank_simulator.db")


def log_audit_event(user_id, action: str, details: str = None, conn=None):
    """Insereaza un eveniment in tabela existenta audit_logs."""
    if not os.path.exists(DB_PATH):
        return

    own_conn = conn is None
    if own_conn:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")

    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO audit_logs (user_id, action, details, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, action, details, timestamp),
    )

    if own_conn:
        conn.commit()
        conn.close()


class User:
    def __init__(
        self,
        user_id: int,
        email: str,
        first_name: str,
        last_name: str,
        status: str = "ACTIVE",
        created_at: str = None,
    ):
        self.id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.status = status
        self.created_at = created_at

    @staticmethod
    def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
        """Verifica daca parola introdusa corespunde cu hash-ul si salt-ul din DB."""
        encoded = (plain_password + salt).encode("utf-8")
        computed_hash = hashlib.sha256(encoded).hexdigest()
        return computed_hash == stored_hash

    @classmethod
    def authenticate(cls, email: str, plain_password: str):
        """Autentifica utilizatorul si logheaza doar LOGIN_SUCCESS."""
        if not os.path.exists(DB_PATH):
            return None

        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, email, password_hash, salt, first_name, last_name, status, created_at
            FROM users WHERE email = ?
            """,
            (email,),
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        user_id, db_email, db_password_hash, db_salt, first_name, last_name, status, created_at = row

        if status != "ACTIVE":
            conn.close()
            print("Contul este inactiv!")
            return None

        if cls.verify_password(plain_password, db_password_hash, db_salt):
            log_audit_event(
                user_id,
                "LOGIN_SUCCESS",
                f"Autentificare reusita pentru {db_email}",
                conn=conn,
            )
            conn.commit()
            conn.close()
            return cls(
                user_id=user_id,
                email=db_email,
                first_name=first_name,
                last_name=last_name,
                status=status,
                created_at=created_at,
            )

        conn.close()
        return None

    @classmethod
    def register(cls, first_name: str, last_name: str, email: str, plain_password: str):
        """Inregistreaza un utilizator nou, ii creeaza contul initial si logheaza succesul."""
        if not os.path.exists(DB_PATH):
            return False, "Baza de date nu exista."

        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = ?;", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "⚠️ Ai deja un cont asociat acestui mail!"

        now = datetime.now().isoformat()
        salt = secrets.token_hex(16)
        encoded = (plain_password + salt).encode("utf-8")
        password_hash = hashlib.sha256(encoded).hexdigest()

        try:
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, salt, first_name, last_name, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                (email, password_hash, salt, first_name, last_name, now),
            )

            user_id = cursor.lastrowid

            random_digits = secrets.randbelow(900000) + 100000
            new_iban = f"RO24HEIS{random_digits}"

            cursor.execute(
                """
                INSERT INTO accounts (iban, user_id, account_name, currency, balance, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                (new_iban, user_id, "Cont Principal", "RON", 100.0, now),
            )

            log_audit_event(
                user_id,
                "USER_REGISTERED",
                f"Utilizator creat: {email}",
                conn=conn,
            )
            log_audit_event(
                user_id,
                "ACCOUNT_CREATED",
                f"Cont initial {new_iban} (100.0 RON)",
                conn=conn,
            )

            conn.commit()
            conn.close()
            return True, "Cont creat cu succes!"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Eroare: {str(e)}"