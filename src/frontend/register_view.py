import customtkinter as ctk
from src.backend.auth_service import register_user

class RegisterView(ctk.CTkFrame):
    def __init__(self, master, on_back_to_login):
        super().__init__(master, fg_color="transparent")
        self.on_back_to_login = on_back_to_login

        # Card central flotant (Light Mode curat)
        card = ctk.CTkFrame(
            self, 
            fg_color="#FFFFFF", 
            corner_radius=32, 
            width=460, 
            height=540,
            border_width=1,
            border_color="#E9DFFF"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Badge brand violet pal
        brand_badge = ctk.CTkFrame(card, fg_color="#F3E8FF", corner_radius=15, height=42)
        brand_badge.pack(pady=(25, 10), padx=40, fill="x")

        brand_label = ctk.CTkLabel(
            brand_badge, 
            text="✦ HEISTBANK REGISTER ✦", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#7C3AED"
        )
        brand_label.pack(pady=8)

        title_label = ctk.CTkLabel(
            card, 
            text="Creează cont nou ✨", 
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#2E2345"
        )
        title_label.pack(pady=(2, 2))

        subtitle_label = ctk.CTkLabel(
            card, 
            text="Începe călătoria ta financiară digitală", 
            font=ctk.CTkFont(size=12),
            text_color="#9689A8"
        )
        subtitle_label.pack(pady=(0, 15))

        # Prenume și Nume pe același rând
        name_frame = ctk.CTkFrame(card, fg_color="transparent")
        name_frame.pack(padx=40, pady=(0, 8), fill="x")

        self.first_name_entry = ctk.CTkEntry(
            name_frame, placeholder_text="Prenume", width=180, height=40,
            corner_radius=12, border_width=1.5, border_color="#E5D9FA", fg_color="#FAF8FF", text_color="#2E2345"
        )
        self.first_name_entry.pack(side="left")

        self.last_name_entry = ctk.CTkEntry(
            name_frame, placeholder_text="Nume", width=180, height=40,
            corner_radius=12, border_width=1.5, border_color="#E5D9FA", fg_color="#FAF8FF", text_color="#2E2345"
        )
        self.last_name_entry.pack(side="right")

        # Email
        email_label = ctk.CTkLabel(card, text="📧 Adresă de email", font=ctk.CTkFont(size=12, weight="bold"), text_color="#334155")
        email_label.pack(anchor="w", padx=40, pady=(0, 2))

        self.email_entry = ctk.CTkEntry(
            card, placeholder_text="nume@heistbank.ro", width=380, height=42,
            corner_radius=12, border_width=1.5, border_color="#E5D9FA", fg_color="#FAF8FF", text_color="#2E2345"
        )
        self.email_entry.pack(pady=(0, 8), padx=40)

        # Parolă
        pass_label = ctk.CTkLabel(card, text="🔑 Parolă secretă", font=ctk.CTkFont(size=12, weight="bold"), text_color="#334155")
        pass_label.pack(anchor="w", padx=40, pady=(0, 2))

        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="Minim 6 caractere", show="•", width=380, height=42,
            corner_radius=12, border_width=1.5, border_color="#E5D9FA", fg_color="#FAF8FF", text_color="#2E2345"
        )
        self.password_entry.pack(pady=(0, 5), padx=40)

        # Label mesaje eroare / succes
        self.msg_label = ctk.CTkLabel(
            card, text="", text_color="#E11D48", font=ctk.CTkFont(size=11, weight="bold")
        )
        self.msg_label.pack(pady=(0, 2))

        # Buton Înregistrare (cu violetul cerut și hover)
        reg_btn = ctk.CTkButton(
            card, text="Înregistrează-te 🚀", command=self.handle_register, width=380, height=44,
            corner_radius=14, fg_color="#8B5CF6", hover_color="#7C3AED", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF"
        )
        reg_btn.pack(pady=(5, 8), padx=40)

        # Buton înapoi la login
        back_btn = ctk.CTkButton(
            card, text="Ai deja cont? Autentifică-te", command=self.on_back_to_login, width=380, height=32,
            corner_radius=10, fg_color="transparent", hover_color="#F1F5F9", text_color="#7C3AED", font=ctk.CTkFont(size=12, weight="bold")
        )
        back_btn.pack(padx=40)

    def handle_register(self):
        fn = self.first_name_entry.get().strip()
        ln = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        pwd = self.password_entry.get().strip()

        if not fn or not ln or not email or not pwd:
            self.msg_label.configure(text="⚠️ Completează toate câmpurile!", text_color="#E11D48")
            return

        success, message = register_user(fn, ln, email, pwd)
        if success:
            self.msg_label.configure(text="✅ " + message + " Te poți autentifica.", text_color="#059669")
            self.after(1800, self.on_back_to_login)
        else:
            self.msg_label.configure(text="❌ " + message, text_color="#E11D48")