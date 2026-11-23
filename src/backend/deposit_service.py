import os
from src.backend.transaction_helper import DB_PATH, get_connection, save_transaction_and_audit


class DepositService:
    """Clasa simpla pentru depuneri de bani intr-un cont."""

    @staticmethod
    def make_deposit(user_id: int, target_iban: str, amount: float):
        if not os.path.exists(DB_PATH):
            return False, "Baza de date nu exista."

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT user_id, currency, balance, status FROM accounts WHERE iban = ?;",
                (target_iban,),
            )
            acc = cursor.fetchone()
            amount = float(amount)

            if not acc:
                save_transaction_and_audit(
                    cursor, user_id, None, target_iban, amount, "RON",
                    "FAILED", "DEPOSIT_FAILED", f"Cont inexistent: {target_iban}"
                )
                conn.commit()
                conn.close()
                return False, "Contul nu exista."

            owner_id, currency, balance, status = acc

            if owner_id != user_id or status != "ACTIVE" or amount <= 0:
                save_transaction_and_audit(
                    cursor, user_id, None, target_iban, amount, currency,
                    "FAILED", "DEPOSIT_FAILED", f"Depunere respinsa pentru {target_iban} (suma: {amount})"
                )
                conn.commit()
                conn.close()
                return False, "Date invalide pentru depunere."

            new_balance = round(balance + amount, 2)
            cursor.execute("UPDATE accounts SET balance = ? WHERE iban = ?;", (new_balance, target_iban))

            save_transaction_and_audit(
                cursor, user_id, None, target_iban, amount, currency,
                "COMPLETED", "DEPOSIT_SUCCESS", f"Depunere {amount:.2f} {currency} in {target_iban}"
            )

            conn.commit()
            conn.close()
            return True, f"Ai depus {amount:.2f} {currency}."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Eroare: {str(e)}"