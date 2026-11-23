from datetime import datetime
import os
import sqlite3
import customtkinter as ctk
from src.backend.auth_service import User

DB_PATH = os.path.join("data", "bank_simulator.db")


def format_eu_date(raw_date: str) -> str:
    if not raw_date:
        return "-"
    s = str(raw_date).strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",
    ):
        try:
            return datetime.strptime(s[:26], fmt).strftime("%d.%m.%Y")
        except ValueError:
            continue
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        parts = s[:10].split("-")
        if len(parts) == 3:
            return f"{parts[2]}.{parts[1]}.{parts[0]}"
    return s


class ProfileSection(ctk.CTkFrame):
    def __init__(self, master, user: User, on_navigate=None):
        super().__init__(master, fg_color="transparent")
        self.user = user

        card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=28,
            border_width=1,
            border_color="#E9DFFF",
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.78)

        badge = ctk.CTkFrame(card, fg_color="#F3E8FF", corner_radius=12, height=30)
        badge.pack(pady=(24, 6), padx=28, anchor="w")
        ctk.CTkLabel(
            badge,
            text="✦ PROFIL CLIENT ✦",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#7C3AED",
        ).pack(padx=12, pady=4)

        ctk.CTkLabel(
            card,
            text="👤 Profilul meu",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", padx=28, pady=(0, 14))

        info = self._load_user_row()
        fields = [
            ("📝 Prenume", info["first_name"]),
            ("📝 Nume", info["last_name"]),
            ("📌 Status", info["status"]),
            ("📅 Data creare", format_eu_date(info["created_at"])),
        ]

        for label_txt, val_txt in fields:
            box = ctk.CTkFrame(
                card,
                fg_color="#FAF8FF",
                corner_radius=14,
                border_width=1,
                border_color="#E5D9FA",
            )
            box.pack(fill="x", padx=28, pady=6)

            inner = ctk.CTkFrame(box, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=11)

            ctk.CTkLabel(
                inner,
                text=label_txt,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#9689A8",
            ).pack(side="left")

            ctk.CTkLabel(
                inner,
                text=val_txt,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#2E2345",
            ).pack(side="right")

        ctk.CTkLabel(
            card,
            text="🔒 Cont securizat Heistbank",
            font=ctk.CTkFont(size=11),
            text_color="#A78BFA",
        ).pack(side="bottom", pady=(8, 22))

    def _load_user_row(self):
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT first_name, last_name, status, created_at FROM users WHERE id = ?;",
                (self.user.id,),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "first_name": row[0],
                    "last_name": row[1],
                    "status": row[2],
                    "created_at": row[3],
                }

        return {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "status": self.user.status,
            "created_at": self.user.created_at,
        }