import customtkinter as ctk
from src.frontend.login_view import LoginView
from src.frontend.register_view import RegisterView
from src.frontend.dashboard_view import DashboardView
from src.backend.auth_service import authenticate_user

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class BankingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Heistbank - Digital Security Banking")
        self.geometry("740x580")
        self.resizable(False, False)

        # Fundal general cald și perlat
        self.configure(fg_color="#F8FAFC")

        self.current_view = None
        self.show_login_screen()

    def switch_view(self, new_view_class, **kwargs):
        if self.current_view is not None:
            self.current_view.destroy()
        
        self.current_view = new_view_class(self, **kwargs)
        self.current_view.pack(fill="both", expand=True)

    def show_login_screen(self):
        self.switch_view(
            LoginView, 
            on_login_success=self.handle_login_attempt,
            on_go_to_register=self.show_register_screen
        )

    def show_register_screen(self):
        self.switch_view(
            RegisterView, 
            on_back_to_login=self.show_login_screen
        )

    def handle_login_attempt(self, email, password, error_label):
        user = authenticate_user(email, password)
        if user:
            self.show_dashboard(user)
        else:
            error_label.configure(text="❌ Date incorecte. Verifică emailul sau parola.")

    def show_dashboard(self, user):
        self.switch_view(DashboardView, user=user, on_logout=self.show_login_screen)