import customtkinter as ctk
from src.backend.auth_service import User
from src.backend.deposit_service import DepositService
from src.backend.transfer_service import TransferService
from src.backend.beneficiary_service import BeneficiaryService
from src.frontend.accounts_section import get_user_accounts


class TransactionSection(ctk.CTkFrame):
    NONE_OPTION = "— Alege beneficiar salvat (opțional) —"

    def __init__(self, master, user: User, on_navigate=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.on_navigate = on_navigate
        self.accounts = get_user_accounts(self.user.id)
        self.iban_options = [
            f"{a['account_name']} - {a['iban']} ({a['currency']})"
            for a in self.accounts
        ]

        self.beneficiaries = BeneficiaryService.list_by_user(self.user.id)
        self._ben_label_to_iban = {}
        ben_values = [self.NONE_OPTION]
        for b in self.beneficiaries:
            label = f"⭐ {b['nickname']} ({b['iban']})"
            ben_values.append(label)
            self._ben_label_to_iban[label] = b["iban"]

        card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=28,
            border_width=1,
            border_color="#E9DFFF",
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.80, relheight=0.90)

        body = ctk.CTkScrollableFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=26, pady=18)

        badge = ctk.CTkFrame(body, fg_color="#F3E8FF", corner_radius=12, height=28)
        badge.pack(pady=(0, 6), anchor="w")
        ctk.CTkLabel(
            badge,
            text="✦ OPERAȚIUNI BANCARE ✦",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#7C3AED",
        ).pack(padx=12, pady=3)

        ctk.CTkLabel(
            body,
            text="💸 Realizează o tranzacție",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            body,
            text="Tip operațiune",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", pady=(0, 4))

        self.op_var = ctk.StringVar(value="Transfer")
        self.op_menu = ctk.CTkSegmentedButton(
            body,
            values=["Depunere", "Transfer"],
            variable=self.op_var,
            selected_color="#8B5CF6",
            selected_hover_color="#7C3AED",
            unselected_color="#FAF8FF",
            unselected_hover_color="#F3E8FF",
            text_color="#2E2345",
            command=self._on_operation_change,
        )
        self.op_menu.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            body,
            text="Contul tău",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", pady=(0, 4))

        self.account_var = ctk.StringVar(
            value=self.iban_options[0] if self.iban_options else ""
        )
        self.account_dropdown = ctk.CTkComboBox(
            body,
            values=self.iban_options if self.iban_options else ["Niciun cont activ"],
            variable=self.account_var,
            width=380,
            height=38,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FAF8FF",
            text_color="#2E2345",
            state="readonly" if self.iban_options else "disabled",
        )
        self.account_dropdown.pack(anchor="w", pady=(0, 10))

        # Container doar pentru Transfer (ascuns complet la Depunere)
        self.target_container = ctk.CTkFrame(body, fg_color="transparent")

        ctk.CTkLabel(
            self.target_container,
            text="Beneficiar salvat (opțional)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", pady=(0, 4))

        self.ben_var = ctk.StringVar(value=ben_values[0])
        self.ben_dropdown = ctk.CTkComboBox(
            self.target_container,
            values=ben_values,
            variable=self.ben_var,
            width=380,
            height=38,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FAF8FF",
            text_color="#2E2345",
            state="readonly",
            command=self._on_beneficiary_selected,
        )
        self.ben_dropdown.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            self.target_container,
            text="IBAN destinatar",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", pady=(0, 4))

        self.target_entry = ctk.CTkEntry(
            self.target_container,
            placeholder_text="Alege un beneficiar sau scrie un IBAN manual",
            width=380,
            height=38,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FAF8FF",
            text_color="#2E2345",
        )
        self.target_entry.pack(anchor="w")

        self.bottom_container = ctk.CTkFrame(body, fg_color="transparent")
        self.bottom_container.pack(fill="x", pady=(6, 4))

        ctk.CTkLabel(
            self.bottom_container,
            text="Sumă",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", pady=(0, 4))

        self.amount_entry = ctk.CTkEntry(
            self.bottom_container,
            placeholder_text="Ex: 150.00",
            width=220,
            height=38,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FAF8FF",
            text_color="#2E2345",
        )
        self.amount_entry.pack(anchor="w", pady=(0, 8))

        self.status_label = ctk.CTkLabel(
            self.bottom_container,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E2345",
        )
        self.status_label.pack(anchor="w", pady=(0, 6))

        self.submit_btn = ctk.CTkButton(
            self.bottom_container,
            text="Confirmă tranzacția 🚀",
            height=42,
            width=240,
            corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            text_color="#FFFFFF",
            command=self._handle_submit,
        )
        self.submit_btn.pack(anchor="w", pady=(4, 12))

        self._on_operation_change("Transfer")

    def _on_beneficiary_selected(self, choice: str):
        iban = self._ben_label_to_iban.get(choice)
        if iban:
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, iban)

    def _on_operation_change(self, value: str):
        self.bottom_container.pack_forget()
        if value == "Transfer":
            self.target_container.pack(fill="x", pady=(0, 8))
        else:
            self.ben_var.set(self.NONE_OPTION)
            self.target_entry.delete(0, "end")
            self.target_container.pack_forget()
        self.bottom_container.pack(fill="x", pady=(4, 4))

    def _selected_iban(self) -> str:
        selected = self.account_var.get()
        for acc in self.accounts:
            if acc["iban"] in selected:
                return acc["iban"]
        return ""

    def _handle_submit(self):
        if not self.iban_options:
            self.status_label.configure(text="❌ Nu ai un cont activ.", text_color="#E11D48")
            return

        raw_amount = self.amount_entry.get().strip().replace(",", ".")
        try:
            amount = float(raw_amount)
        except ValueError:
            self.status_label.configure(text="❌ Introdu o sumă numerică validă.", text_color="#E11D48")
            return

        selected_iban = self._selected_iban()
        op = self.op_var.get()

        if op == "Depunere":
            ok, msg = DepositService.make_deposit(self.user.id, selected_iban, amount)
        else:
            target_iban = self.target_entry.get().strip()
            ok, msg = TransferService.make_transfer(
                self.user.id, selected_iban, target_iban, amount
            )

        if ok:
            self.submit_btn.configure(state="disabled")
            self.status_label.configure(
                text=f"⏳ {msg} Se deschide istoricul...",
                text_color="#7C3AED",
            )
            self.after(1200, self._go_to_history)
        else:
            self.status_label.configure(text=f"❌ {msg}", text_color="#E11D48")

    def _go_to_history(self):
        if self.on_navigate and self.winfo_exists():
            self.on_navigate("history")