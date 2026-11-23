import customtkinter as ctk
from src.backend.auth_service import User
from src.backend.beneficiary_service import BeneficiaryService


class BeneficiariesSection(ctk.CTkFrame):
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
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.86)

        ctk.CTkLabel(
            card,
            text="👥 Beneficiari salvați",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", padx=24, pady=(20, 10))

        form_card = ctk.CTkFrame(
            card,
            fg_color="#FAF8FF",
            corner_radius=18,
            border_width=1.5,
            border_color="#E5D9FA",
        )
        form_card.pack(fill="x", padx=24, pady=(0, 8))

        row1 = ctk.CTkFrame(form_card, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(12, 6))

        self.name_entry = ctk.CTkEntry(
            row1,
            placeholder_text="Nickname (ex: Ana, Mama)",
            height=36,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FFFFFF",
            text_color="#2E2345",
        )
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.iban_entry = ctk.CTkEntry(
            row1,
            placeholder_text="IBAN beneficiar",
            height=36,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FFFFFF",
            text_color="#2E2345",
        )
        self.iban_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))

        row2 = ctk.CTkFrame(form_card, fg_color="transparent")
        row2.pack(fill="x", padx=14, pady=(0, 12))

        self.bank_entry = ctk.CTkEntry(
            row2,
            placeholder_text="Bancă (opțional)",
            height=36,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FFFFFF",
            text_color="#2E2345",
        )
        self.bank_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        add_btn = ctk.CTkButton(
            row2,
            text="➕ Adaugă",
            width=120,
            height=36,
            corner_radius=12,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            text_color="#FFFFFF",
            command=self._handle_add,
        )
        add_btn.pack(side="right")

        self.msg_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.msg_label.pack(anchor="w", padx=24, pady=(0, 4))

        self.list_scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        self._refresh_list()

    def _refresh_list(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()

        items = BeneficiaryService.list_by_user(self.user.id)
        if not items:
            ctk.CTkLabel(
                self.list_scroll,
                text="Nu ai beneficiari salvați încă.",
                font=ctk.CTkFont(size=13),
                text_color="#9689A8",
            ).pack(pady=14)
            return

        for item in items:
            ben_id = item["id"]
            nickname_val = item["nickname"]
            iban_val = item["iban"]
            bank_val = item["bank_name"]

            row_card = ctk.CTkFrame(
                self.list_scroll,
                fg_color="#FAF8FF",
                corner_radius=16,
                border_width=1,
                border_color="#E5D9FA",
            )
            row_card.pack(fill="x", pady=5)

            top_row = ctk.CTkFrame(row_card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(10, 2))

            ctk.CTkLabel(
                top_row,
                text=f"⭐ {nickname_val} ({bank_val})",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#2E2345",
            ).pack(side="left")

            ctk.CTkButton(
                top_row,
                text="🗑️ Șterge",
                width=84,
                height=28,
                corner_radius=10,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#E11D48",
                hover_color="#BE123C",
                text_color="#FFFFFF",
                command=lambda bid=ben_id: self._handle_delete(bid),
            ).pack(side="right")

            ctk.CTkLabel(
                row_card,
                text=f"IBAN: {iban_val}",
                font=ctk.CTkFont(size=12),
                text_color="#9689A8",
            ).pack(anchor="w", padx=16, pady=(0, 10))

    def _handle_add(self):
        ok, msg = BeneficiaryService.add_for_user(
            self.user.id,
            self.name_entry.get(),
            self.iban_entry.get(),
            self.bank_entry.get(),
        )
        if ok:
            self.msg_label.configure(text=f"✅ {msg}", text_color="#16A34A")
            self.name_entry.delete(0, "end")
            self.iban_entry.delete(0, "end")
            self.bank_entry.delete(0, "end")
            self._refresh_list()
        else:
            self.msg_label.configure(text=f"❌ {msg}", text_color="#E11D48")

    def _handle_delete(self, beneficiary_id: int):
        ok, msg = BeneficiaryService.remove_for_user(self.user.id, beneficiary_id)
        if ok:
            self.msg_label.configure(text=f"✅ {msg}", text_color="#16A34A")
            self._refresh_list()
        else:
            self.msg_label.configure(text=f"❌ {msg}", text_color="#E11D48")