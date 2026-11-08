import sys
import os

# Adăugăm calea curentă în Python Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import init_database
from src.database.seed import seed_database
from src.frontend.app import BankingApp

def main():
    # Inspecție automată la pornire: 
    # 1. Dacă lipsește folderul sau fișierul .db, le creează de la zero.
    # 2. Dacă baza de date este goală, inserează automat datele de test.
    # 3. Dacă totul există și este populat, trece instant mai departe.
    init_database()
    seed_database()

    # Pornirea interfeței grafice Heistbank
    app = BankingApp()
    app.mainloop()

if __name__ == "__main__":
    main()