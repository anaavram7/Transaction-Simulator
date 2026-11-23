import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import init_database
from src.database.seed import seed_database
from src.frontend.app import BankingApp

def main():
    init_database()
    seed_database()

    app = BankingApp()
    app.mainloop()

if __name__ == "__main__":
    main()
    
