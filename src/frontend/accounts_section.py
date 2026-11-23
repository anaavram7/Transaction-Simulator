import sqlite3
import os
import customtkinter as ctk
from src.backend.auth_service import User

DB_PATH = os.path.join("data", "bank_simulator.db")


def get_user_accounts(user_id: int):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT iban, account_name, currency, balance, status
        FROM accounts
        WHERE user_id = ? AND status = 'ACTIVE'
        ORDER BY iban ASC;
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "iban": r[0],
            "account_name": r[1],
            "currency": r[2],
            "balance": r[3],
            "status": r[4],
        }
        for r in rows
    ]


class AccountsSection(ctk.CTkFrame):
    def __init__(self, master, user: User, on_navigate=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.on_navigate = on_navigate

        card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=28,
            border_width=1,
            border_color="#E9DFFF",
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.84)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=26, pady=(22, 10))

        ctk.CTkLabel(
            header,
            text="💳 Conturile mele",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2E2345",
        ).pack(side="left")

        if self.on_navigate:
            ctk.CTkButton(
                header,
                text="💸 Tranzacție nouă",
                height=34,
                corner_radius=12,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#8B5CF6",
                hover_color="#7C3AED",
                text_color="#FFFFFF",
                command=lambda: self.on_navigate("transaction"),
            ).pack(side="right")

        accounts = get_user_accounts(self.user.id)
        total_ron = sum(a["balance"] for a in accounts if a["currency"] == "RON")

        summary = ctk.CTkFrame(
            card,
            fg_color="#FAF8FF",
            corner_radius=18,
            border_width=1.5,
            border_color="#E5D9FA",
        )
        summary.pack(fill="x", padx=26, pady=(0, 12))

        ctk.CTkLabel(
            summary,
            text="💰 Sold total disponibil (RON)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9689A8",
        ).pack(anchor="w", padx=18, pady=(10, 0))

        ctk.CTkLabel(
            summary,
            text=f"{total_ron:,.2f} RON",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", padx=18, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=26, pady=(0, 20))

        if not accounts:
            ctk.CTkLabel(
                scroll,
                text="Nu ai conturi active momentan.",
                font=ctk.CTkFont(size=13),
                text_color="#9689A8",
            ).pack(pady=14)
            return

        for acc in accounts:
            item = ctk.CTkFrame(
                scroll,
                fg_color="#FAF8FF",
                corner_radius=16,
                border_width=1,
                border_color="#E5D9FA",
            )
            item.pack(fill="x", pady=5)

            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill="x", padx=16, pady=(10, 2))

            ctk.CTkLabel(
                top,
                text=f"🏦 {acc['account_name']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#2E2345",
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=f"{acc['balance']:,.2f} {acc['currency']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#7C3AED",
            ).pack(side="right")

            ctk.CTkLabel(
                item,
                text=f"IBAN: {acc['iban']}",
                font=ctk.CTkFont(size=12),
                text_color="#9689A8",
            ).pack(anchor="w", padx=16, pady=(0, 10))