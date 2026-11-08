import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success, on_go_to_register):
        super().__init__(master, fg_color="transparent")
        self.on_login_success = on_login_success
        self.on_go_to_register = on_go_to_register

        # Card central flotant (Alb curat)
        card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=32,
            width=460,
            height=530,
            border_width=1,
            border_color="#E9DFFF"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Badge brand violet pal
        brand_badge = ctk.CTkFrame(card, fg_color="#F3E8FF", corner_radius=15, height=42)
        brand_badge.pack(pady=(25, 10), padx=40, fill="x")

        brand_label = ctk.CTkLabel(
            brand_badge, 
            text="✦ HEISTBANK DIGITAL ✦",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#7C3AED"
        )
        brand_label.pack(pady=8)

        # Mesaj de întâmpinare
        title_label = ctk.CTkLabel(
            card, 
            text="Bine ai revenit! 👋", 
            font=ctk.CTkFont(size=29, weight="bold"),
            text_color="#2E2345"
        )
        title_label.pack(pady=(2, 2))

        subtitle_label = ctk.CTkLabel(
            card, 
            text="Conectează-te la portofelul tău securizat", 
            font=ctk.CTkFont(size=13),
            text_color="#9689A8"
        )
        subtitle_label.pack(pady=(0, 15))

        # Email
        email_label = ctk.CTkLabel(card, text="📧 Adresă de email", font=ctk.CTkFont(size=12, weight="bold"), text_color="#334155")
        email_label.pack(anchor="w", padx=40, pady=(0, 4))

        self.email_entry = ctk.CTkEntry(
            card, 
            placeholder_text="alex.popescu@heistbank.ro", 
            width=380,
            height=44,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FAF8FF",
            text_color="#2E2345"
        )
        self.email_entry.pack(pady=(0, 10), padx=40)

        # Parolă
        pass_label = ctk.CTkLabel(card, text="🔑 Parolă secretă", font=ctk.CTkFont(size=12, weight="bold"), text_color="#334155")
        pass_label.pack(anchor="w", padx=40, pady=(0, 4))

        self.password_entry = ctk.CTkEntry(
            card, 
            placeholder_text="••••••••••••", 
            show="•", 
            width=380,
            height=44,
            corner_radius=12,
            border_width=1.5,
            border_color="#E5D9FA",
            fg_color="#FAF8FF",
            text_color="#2E2345"
        )
        self.password_entry.pack(pady=(0, 5), padx=40)

        # Label erori
        self.error_label = ctk.CTkLabel(
            card, 
            text="", 
            text_color="#E11D48", 
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.error_label.pack(pady=(0, 2))

        # Buton de conectare (Violet cu efect hover închis)
        login_btn = ctk.CTkButton(
            card, 
            text="Autentificare în siguranță 🚀", 
            command=self.handle_click, 
            width=380,
            height=46,
            corner_radius=14,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#FFFFFF"
        )
        login_btn.pack(pady=(5, 5), padx=40)
        
        # Buton navigare spre Înregistrare
        reg_nav_btn = ctk.CTkButton(
            card,
            text="Nu ai cont? Creează unul nou ✨",
            command=self.on_go_to_register,
            width=380,
            height=32,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#F1F5F9",
            text_color="#7C3AED",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        reg_nav_btn.pack(padx=40, pady=(0, 10))

        security_label = ctk.CTkLabel(
            card,
            text="🔒 Experiența ta bancară, protejată mereu.",
            font=ctk.CTkFont(size=11),
            text_color="#A78BFA"
        )
        security_label.pack(pady=(0, 10))

    def handle_click(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            self.error_label.configure(text="⚠️ Completează toate câmpurile, te rugăm.")
            return

        self.on_login_success(email, password, self.error_label)