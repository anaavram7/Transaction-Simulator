from datetime import datetime
import os
import sqlite3
import customtkinter as ctk
from src.backend.auth_service import User

DB_PATH = os.path.join("data", "bank_simulator.db")


def format_eu_datetime(raw_date: str) -> str:
    if not raw_date:
        return "-"
    s = str(raw_date).strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
    ):
        try:
            return datetime.strptime(s[:26], fmt).strftime("%d.%m.%Y %H:%M")
        except ValueError:
            continue
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(s[:10], fmt).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return s


def _build_name_lookups(cursor: sqlite3.Cursor, user_id: int):
    
    real_name_by_iban = {}
    nickname_by_iban = {}

    cursor.execute(
        """
        SELECT a.iban, u.first_name, u.last_name
        FROM accounts a
        JOIN users u ON u.id = a.user_id;
        """
    )
    for iban, first_name, last_name in cursor.fetchall():
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if iban and full_name:
            real_name_by_iban[iban.upper()] = full_name

    cursor.execute(
        """
        SELECT iban, beneficiary_name
        FROM beneficiaries
        WHERE user_id = ?;
        """,
        (user_id,),
    )
    for iban, ben_name in cursor.fetchall():
        if iban and ben_name:
            nickname_by_iban[iban.upper()] = ben_name.strip()

    return real_name_by_iban, nickname_by_iban


def get_user_transactions(user_id: int):
    if not os.path.exists(DB_PATH):
        return [], set(), {}, {}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT iban FROM accounts WHERE user_id = ?;", (user_id,))
    user_ibans = {row[0].upper() for row in cursor.fetchall() if row[0]}

    if not user_ibans:
        conn.close()
        return [], user_ibans, {}, {}

    real_name_by_iban, nickname_by_iban = _build_name_lookups(cursor, user_id)

    placeholders = ",".join("?" for _ in user_ibans)
    iban_list = list(user_ibans)

    cursor.execute(
        f"""
        SELECT id, source_iban, target_iban, amount, currency, status, timestamp
        FROM transactions
        WHERE UPPER(source_iban) IN ({placeholders}) OR UPPER(target_iban) IN ({placeholders})
        ORDER BY id DESC;
        """,
        iban_list + iban_list,
    )
    rows = cursor.fetchall()
    conn.close()
    return rows, user_ibans, real_name_by_iban, nickname_by_iban


class HistorySection(ctk.CTkFrame):
    def __init__(self, master, user: User, on_navigate=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.current_user_fullname = f"{user.first_name or ''} {user.last_name or ''}".strip()

        card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=28,
            border_width=1,
            border_color="#E9DFFF",
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.84, relheight=0.90)

        ctk.CTkLabel(
            card,
            text="📜 Istoric tranzacții",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", padx=24, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        rows, user_ibans, real_name_by_iban, nickname_by_iban = get_user_transactions(self.user.id)

        if not rows:
            ctk.CTkLabel(
                scroll,
                text="Nu există tranzacții înregistrate încă.",
                font=ctk.CTkFont(size=13),
                text_color="#9689A8",
            ).pack(pady=16)
            return

        for _, src_iban, dst_iban, amount, currency, status, timestamp in rows:
            src_key = (src_iban or "").upper()
            dst_key = (dst_iban or "").upper()
            is_src_mine = src_key in user_ibans
            is_dst_mine = dst_key in user_ibans

            src_real = real_name_by_iban.get(src_key, "Cont extern")
            dst_display_for_send = (
                nickname_by_iban.get(dst_key)
                or real_name_by_iban.get(dst_key)
                or "Cont extern"
            )

            if status == "FAILED":
                title_text = f"⚠️ Tranzacție nereușită ({dst_display_for_send})"
                amount_color = "#E11D48"
                prefix = ""
            elif is_src_mine and is_dst_mine:
                title_text = f"🔄 Transfer între conturile mele ({self.current_user_fullname})"
                amount_color = "#7C3AED"
                prefix = ""
            elif is_dst_mine and not is_src_mine:
                if not src_key:
                    title_text = f"📥 Depunere ({self.current_user_fullname})"
                else:
                    title_text = f"📥 Primit de la {src_real}"
                amount_color = "#16A34A"
                prefix = "+"
            else:
                title_text = f"📤 Trimis către {dst_display_for_send}"
                amount_color = "#8B5CF6"
                prefix = "-"

            item = ctk.CTkFrame(
                scroll,
                fg_color="#FAF8FF",
                corner_radius=16,
                border_width=1,
                border_color="#E5D9FA",
            )
            item.pack(fill="x", pady=5)

            ctk.CTkLabel(
                item,
                text=title_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#2E2345",
            ).pack(anchor="w", padx=16, pady=(10, 2))

            bottom = ctk.CTkFrame(item, fg_color="transparent")
            bottom.pack(fill="x", padx=16, pady=(0, 10))

            ctk.CTkLabel(
                bottom,
                text=f"Data: {format_eu_datetime(timestamp)}",
                font=ctk.CTkFont(size=11),
                text_color="#9689A8",
            ).pack(side="left")

            ctk.CTkLabel(
                bottom,
                text=f"{prefix}{amount:,.2f} {currency} • {status}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=amount_color,
            ).pack(side="right")