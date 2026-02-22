import sqlite3

DB_NAME = "finance_new.db"

def init_budget_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        amount REAL,
        month TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_budget(category, amount, month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budgets (category, amount, month)
        VALUES (?, ?, ?)
    """, (category, amount, month))

    conn.commit()
    conn.close()


def get_budgets(month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, amount
        FROM budgets
        WHERE month = ?
    """, (month,))

    data = cursor.fetchall()
    conn.close()
    return data

def save_budget(category, month, budget_amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budgets (category, amount, month)
        VALUES (?, ?, ?)
    """, (category, budget_amount, month))

    conn.commit()
    conn.close()

def delete_budget(budget_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))

    conn.commit()
    conn.close()


def update_budget(budget_id, category, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE budgets
        SET category = ?, amount = ?
        WHERE id = ?
    """, (category, amount, budget_id))

    conn.commit()
    conn.close()