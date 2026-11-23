from datetime import datetime
import customtkinter as ctk
from src.backend.auth_service import User
from src.frontend.accounts_section import AccountsSection, get_user_accounts
from src.frontend.transaction_section import TransactionSection
from src.frontend.history_section import HistorySection
from src.frontend.beneficiaries_section import BeneficiariesSection
from src.frontend.profile_section import ProfileSection


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


def _normalize_accounts(raw_accounts):
    result = []
    if not raw_accounts:
        return result
    for item in raw_accounts:
        if isinstance(item, dict):
            result.append(item)
        elif isinstance(item, (tuple, list)) and len(item) >= 5:
            result.append(
                {
                    "iban": item[0],
                    "account_name": item[1],
                    "currency": item[2],
                    "balance": float(item[3] or 0),
                    "status": item[4],
                }
            )
    return result


class HomeOverviewSection(ctk.CTkFrame):
    """Pagina principala: profilul tau + conturile active."""

    def __init__(self, master, user: User, on_navigate=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.on_navigate = on_navigate

        first_name = getattr(self.user, "first_name", "") or ""
        last_name = getattr(self.user, "last_name", "") or ""
        status = getattr(self.user, "status", "ACTIVE") or "ACTIVE"
        user_id = getattr(self.user, "id", None)

        container = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=28,
            border_width=1,
            border_color="#E9DFFF",
        )
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.78)

        badge = ctk.CTkFrame(container, fg_color="#F3E8FF", corner_radius=12, height=30)
        badge.pack(pady=(20, 6), padx=24, anchor="w")
        ctk.CTkLabel(
            badge,
            text="✦ HEISTBANK DIGITAL • PAGINA PRINCIPALĂ ✦",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#7C3AED",
        ).pack(padx=12, pady=4)

        ctk.CTkLabel(
            container,
            text=f"Bine ai venit, {first_name or 'Client'}! 👋",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", padx=24)

        full_name = f"{first_name} {last_name}".strip() or "Utilizator"
        ctk.CTkLabel(
            container,
            text=f"Profil: {full_name}   •   Status: {status}",
            font=ctk.CTkFont(size=12),
            text_color="#9689A8",
        ).pack(anchor="w", padx=24, pady=(2, 10))

        accounts = _normalize_accounts(get_user_accounts(user_id) if user_id is not None else [])
        total_ron = sum(
            float(a.get("balance", 0) or 0)
            for a in accounts
            if a.get("currency") == "RON"
        )

        total_box = ctk.CTkFrame(
            container,
            fg_color="#FAF8FF",
            corner_radius=16,
            border_width=1.5,
            border_color="#E5D9FA",
        )
        total_box.pack(fill="x", padx=24, pady=(0, 10))

        ctk.CTkLabel(
            total_box,
            text="💰 Sold total disponibil (RON)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9689A8",
        ).pack(anchor="w", padx=16, pady=(10, 0))

        ctk.CTkLabel(
            total_box,
            text=f"{total_ron:,.2f} RON",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2E2345",
        ).pack(anchor="w", padx=16, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        if not accounts:
            ctk.CTkLabel(
                scroll,
                text="Nu ai conturi active momentan.",
                font=ctk.CTkFont(size=13),
                text_color="#9689A8",
            ).pack(pady=12)
            return

        for acc in accounts:
            row_card = ctk.CTkFrame(
                scroll,
                fg_color="#FAF8FF",
                corner_radius=14,
                border_width=1,
                border_color="#E5D9FA",
            )
            row_card.pack(fill="x", pady=5)

            top = ctk.CTkFrame(row_card, fg_color="transparent")
            top.pack(fill="x", padx=16, pady=(10, 2))

            ctk.CTkLabel(
                top,
                text=f"🏦 {acc.get('account_name', 'Cont')}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#2E2345",
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=f"{float(acc.get('balance', 0) or 0):,.2f} {acc.get('currency', '')}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#7C3AED",
            ).pack(side="right")

            ctk.CTkLabel(
                row_card,
                text=f"IBAN: {acc.get('iban', '-')}",
                font=ctk.CTkFont(size=12),
                text_color="#9689A8",
            ).pack(anchor="w", padx=16, pady=(0, 10))


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user: User, on_logout):
        super().__init__(master, fg_color="#FAF8FF")
        self.user = user
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.sidebar_open = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_main_layer()
        self._build_drawer_overlay()

        self._set_sidebar_open(False)
        self.show_section("home", close_menu=False)

    def _build_main_layer(self):
        self.main_layer = ctk.CTkFrame(self, fg_color="#FAF8FF", corner_radius=0)
        self.main_layer.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        self.main_layer.grid_columnconfigure(0, weight=1)
        self.main_layer.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.main_layer, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.menu_btn = ctk.CTkButton(
            top_bar,
            text="☰",
            width=44,
            height=38,
            corner_radius=12,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#FFFFFF",
            hover_color="#F3E8FF",
            text_color="#7C3AED",
            border_width=1.5,
            border_color="#E9DFFF",
            command=self.toggle_sidebar,
        )
        self.menu_btn.pack(side="left")

        self.content_frame = ctk.CTkFrame(self.main_layer, fg_color="transparent", corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _build_drawer_overlay(self):
        first_name = getattr(self.user, "first_name", "") or ""
        last_name = getattr(self.user, "last_name", "") or ""

        self.drawer = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=24,
            fg_color="#FFFFFF",
            border_width=1.5,
            border_color="#E9DFFF",
        )

        top_row = ctk.CTkFrame(self.drawer, fg_color="transparent")
        top_row.pack(fill="x", padx=18, pady=(18, 6))

        ctk.CTkLabel(
            top_row,
            text="✦ HEISTBANK",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#7C3AED",
        ).pack(side="left")

        close_btn = ctk.CTkButton(
            top_row,
            text="✕",
            width=30,
            height=30,
            corner_radius=10,
            fg_color="#F3E8FF",
            hover_color="#E9DFFF",
            text_color="#7C3AED",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self._set_sidebar_open(False),
        )
        close_btn.pack(side="right")

        ctk.CTkLabel(
            self.drawer,
            text=f"{first_name} {last_name} ✨".strip(),
            font=ctk.CTkFont(size=12),
            text_color="#9689A8",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        menu_items = [
            ("home", "🏠 Pagina principală"),
            ("accounts", "💳 Conturile mele"),
            ("transaction", "💸 Realizează o tranzacție"),
            ("history", "📜 Istoric tranzacții"),
            ("beneficiaries", "👥 Beneficiari"),
            ("profile", "👤 Profilul meu"),
        ]

        for key, label in menu_items:
            btn = ctk.CTkButton(
                self.drawer,
                text=label,
                anchor="w",
                height=38,
                corner_radius=12,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="transparent",
                text_color="#2E2345",
                hover_color="#F3E8FF",
                command=lambda k=key: self.show_section(k, close_menu=True),
            )
            btn.pack(fill="x", padx=14, pady=3)
            self.nav_buttons[key] = btn

        logout_btn = ctk.CTkButton(
            self.drawer,
            text="🚪 Deconectare",
            height=38,
            corner_radius=14,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            text_color="#FFFFFF",
            command=self.on_logout,
        )
        logout_btn.pack(side="bottom", fill="x", padx=14, pady=18)

    def _set_sidebar_open(self, is_open: bool):
        self.sidebar_open = is_open
        if is_open:
            self.drawer.place(x=18, y=62, relheight=0.86)
            self.drawer.lift()
        else:
            self.drawer.place_forget()

    def toggle_sidebar(self):
        self._set_sidebar_open(not self.sidebar_open)

    def _highlight_button(self, active_key: str):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color="#F3E8FF", text_color="#7C3AED")
            else:
                btn.configure(fg_color="transparent", text_color="#2E2345")

    def show_section(self, section_key: str, close_menu: bool = True):
        self._highlight_button(section_key)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        section_map = {
            "home": HomeOverviewSection,
            "accounts": AccountsSection,
            "transaction": TransactionSection,
            "history": HistorySection,
            "beneficiaries": BeneficiariesSection,
            "profile": ProfileSection,
        }

        section_cls = section_map.get(section_key, HomeOverviewSection)
        view = section_cls(
            self.content_frame,
            user=self.user,
            on_navigate=lambda k: self.show_section(k, close_menu=True),
        )
        view.grid(row=0, column=0, sticky="nsew")

        if close_menu:
            self._set_sidebar_open(False)