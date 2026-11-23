import os
from src.backend.beneficiary_helper import DB_PATH, get_beneficiary_connection


class BeneficiaryService:
    """Clasa simpla pentru beneficiarii unui user_id."""

    @staticmethod
    def list_by_user(user_id: int):
        if not os.path.exists(DB_PATH):
            return []

        conn = get_beneficiary_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, beneficiary_name, iban, bank_name
            FROM beneficiaries
            WHERE user_id = ?
            ORDER BY id DESC;
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": r[0],
                "nickname": r[1],
                "iban": r[2],
                "bank_name": r[3],
            }
            for r in rows
        ]

    @staticmethod
    def add_for_user(user_id: int, nickname: str, iban: str, bank_name: str = "Heistbank"):
        if not os.path.exists(DB_PATH):
            return False, "Baza de date nu exista."

        clean_name = (nickname or "").strip()
        clean_iban = (iban or "").strip().upper()
        clean_bank = (bank_name or "").strip() or "Heistbank"

        if not clean_name or not clean_iban:
            return False, "Completeaza nickname-ul si IBAN-ul."

        conn = get_beneficiary_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id FROM beneficiaries
                WHERE user_id = ? AND UPPER(iban) = ?;
                """,
                (user_id, clean_iban),
            )
            if cursor.fetchone():
                conn.close()
                return False, "Ai deja acest IBAN salvat."

            cursor.execute(
                """
                INSERT INTO beneficiaries (user_id, beneficiary_name, iban, bank_name)
                VALUES (?, ?, ?, ?);
                """,
                (user_id, clean_name, clean_iban, clean_bank),
            )

            conn.commit()
            conn.close()
            return True, "Beneficiar adaugat."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Eroare: {str(e)}"

    @staticmethod
    def remove_for_user(user_id: int, beneficiary_id: int):
        if not os.path.exists(DB_PATH):
            return False, "Baza de date nu exista."

        conn = get_beneficiary_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM beneficiaries WHERE id = ? AND user_id = ?;",
                (beneficiary_id, user_id),
            )
            conn.commit()
            conn.close()
            return True, "Beneficiar sters."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Eroare: {str(e)}"