import os
import sqlite3

DB_PATH = os.path.join("data", "bank_simulator.db")


def get_beneficiary_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn