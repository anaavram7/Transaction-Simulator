import customtkinter as ctk
from src.backend.account_service import get_user_accounts

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.on_logout = on_logout

        # Preluăm conturile utilizatorului pentru a calcula soldul total
        accounts = get_user_accounts(user['id'])
        total_balance = sum(acc[3] for acc in accounts) if accounts else 0.0
        currency = accounts[0][2] if accounts else "RON"

        # Header superior personalizat
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16, height=75)
        header_frame.pack(fill="x", padx=25, pady=(15, 10))
        header_frame.pack_propagate(False)

        # Stânga: Logo + Salut
        left_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_box.pack(side="left", padx=20, pady=12)

        company_tag = ctk.CTkLabel(
            left_box, 
            text="HEISTBANK 🛡️", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#7C3AED"
        )
        company_tag.pack(anchor="w")

        user_name_text = f"Salut, {user['first_name']}! ✨"
        welcome_label = ctk.CTkLabel(
            left_box, 
            text=user_name_text, 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0F172A"
        )
        welcome_label.pack(anchor="w")

        # Dreapta: Buton de deconectare
        logout_btn = ctk.CTkButton(
            header_frame, 
            text="Deconectare 🚪", 
            command=self.on_logout, 
            width=110, 
            height=38,
            corner_radius=12,
            fg_color="#FEE2E2", 
            hover_color="#FECACA",
            text_color="#991B1B",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        logout_btn.pack(side="right", padx=20)

        # --- Element nou și interesant: Cardul de Sold Total (Net Worth) ---
        total_card = ctk.CTkFrame(self, fg_color="#7C3AED", corner_radius=20, height=90)
        total_card.pack(fill="x", padx=25, pady=(5, 10))
        total_card.pack_propagate(False)

        total_title = ctk.CTkLabel(
            total_card, 
            text="💎 Sold Total Disponibil", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#E9D5FF"
        )
        total_title.pack(anchor="w", padx=22, pady=(14, 0))

        total_amount = ctk.CTkLabel(
            total_card, 
            text=f"{total_balance:,.2f} {currency}", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        total_amount.pack(anchor="w", padx=22, pady=(2, 0))

        # Titlu secțiune conturi individuale
        section_label = ctk.CTkLabel(
            self, 
            text="Conturile mele active", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#64748B"
        )
        section_label.pack(anchor="w", padx=30, pady=(5, 5))

        # Listă scrollabilă pentru conturi
        scroll_frame = ctk.CTkScrollableFrame(self, width=640, height=200, fg_color="transparent")
        scroll_frame.pack(padx=20, pady=2, fill="both", expand=True)

        if not accounts:
            no_acc_label = ctk.CTkLabel(scroll_frame, text="Nu există conturi active înregistrate.", font=ctk.CTkFont(size=13))
            no_acc_label.pack(pady=30)
        else:
            for iban, name, currency, balance, status in accounts:
                acc_card = ctk.CTkFrame(
                    scroll_frame, 
                    corner_radius=18, 
                    fg_color="#FFFFFF",
                    border_width=1,
                    border_color="#E2E8F0"
                )
                acc_card.pack(fill="x", pady=6, padx=10)

                left_box_acc = ctk.CTkFrame(acc_card, fg_color="transparent")
                left_box_acc.pack(side="left", padx=20, pady=16)

                name_label = ctk.CTkLabel(
                    left_box_acc, 
                    text=f"💳 {name}", 
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#0F172A",
                    anchor="w"
                )
                name_label.pack(anchor="w")

                iban_label = ctk.CTkLabel(
                    left_box_acc, 
                    text=f"IBAN: {iban}", 
                    font=ctk.CTkFont(size=11),
                    text_color="#64748B"
                )
                iban_label.pack(anchor="w", pady=(2, 0))

                right_box_acc = ctk.CTkFrame(acc_card, fg_color="transparent")
                right_box_acc.pack(side="right", padx=20, pady=16)

                balance_text = f"{balance:,.2f} {currency}"
                balance_label = ctk.CTkLabel(
                    right_box_acc, 
                    text=balance_text, 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color="#059669"
                )
                balance_label.pack(anchor="e")