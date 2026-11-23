import os
from src.backend.transaction_helper import DB_PATH, get_connection, save_transaction_and_audit


class TransferService:
    """Clasa simpla pentru transferuri intre doua conturi pe aceeasi valuta."""

    @staticmethod
    def make_transfer(user_id: int, source_iban: str, target_iban: str, amount: float):
        if not os.path.exists(DB_PATH):
            return False, "Baza de date nu exista."

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT user_id, currency, balance, status FROM accounts WHERE iban = ?;",
                (source_iban,),
            )
            src = cursor.fetchone()

            cursor.execute(
                "SELECT user_id, currency, balance, status FROM accounts WHERE iban = ?;",
                (target_iban,),
            )
            dst = cursor.fetchone()

            amount = float(amount)
            curr = src[1] if src else "RON"

            if not src or not dst:
                save_transaction_and_audit(
                    cursor, user_id, source_iban, target_iban, amount, curr,
                    "FAILED", "TRANSFER_FAILED", f"Cont lipsa la transfer ({source_iban} -> {target_iban})"
                )
                conn.commit()
                conn.close()
                return False, "Contul sursa sau destinatie nu exista."

            src_owner, src_curr, src_bal, src_status = src
            dst_owner, dst_curr, dst_bal, dst_status = dst

            if src_owner != user_id or src_status != "ACTIVE" or dst_status != "ACTIVE":
                save_transaction_and_audit(
                    cursor, user_id, source_iban, target_iban, amount, src_curr,
                    "FAILED", "TRANSFER_FAILED", f"Cont inactiv sau neautorizat ({source_iban} -> {target_iban})"
                )
                conn.commit()
                conn.close()
                return False, "Contul nu este eligibil pentru transfer."

            if source_iban == target_iban or amount <= 0 or src_curr != dst_curr:
                save_transaction_and_audit(
                    cursor, user_id, source_iban, target_iban, amount, src_curr,
                    "FAILED", "TRANSFER_FAILED", f"Transfer invalid ({source_iban} -> {target_iban}, {amount} {src_curr})"
                )
                conn.commit()
                conn.close()
                return False, "Transferul nu este valid (verifica suma, IBAN-ul si valuta)."

            if src_bal < amount:
                save_transaction_and_audit(
                    cursor, user_id, source_iban, target_iban, amount, src_curr,
                    "FAILED", "TRANSFER_FAILED", f"Fonduri insuficiente in {source_iban} (cerut: {amount:.2f})"
                )
                conn.commit()
                conn.close()
                return False, "Fonduri insuficiente pentru transfer."

            new_src_bal = round(src_bal - amount, 2)
            new_dst_bal = round(dst_bal + amount, 2)

            cursor.execute("UPDATE accounts SET balance = ? WHERE iban = ?;", (new_src_bal, source_iban))
            cursor.execute("UPDATE accounts SET balance = ? WHERE iban = ?;", (new_dst_bal, target_iban))

            save_transaction_and_audit(
                cursor, user_id, source_iban, target_iban, amount, src_curr,
                "COMPLETED", "TRANSFER_SUCCESS", f"Transfer {amount:.2f} {src_curr} din {source_iban} in {target_iban}"
            )

            conn.commit()
            conn.close()
            return True, f"Ai transferat {amount:.2f} {src_curr} cu succes."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Eroare: {str(e)}"