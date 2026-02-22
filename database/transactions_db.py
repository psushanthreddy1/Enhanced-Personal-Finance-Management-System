import sqlite3
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float
from database.db import Base



class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    merchant = Column(String)
    amount = Column(Float)
    account_id = Column(Integer)
    txn_type = Column(String)
    category = Column(String)
    txn_date = Column(String)
DB_NAME = "finance_new.db"

def connect():
    return sqlite3.connect(DB_NAME)


# ✅ Initialize Table
def init_transactions_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant TEXT,
        amount REAL,
        account_id INTEGER,
        txn_type TEXT,
        category TEXT,
        txn_date TEXT
    )
    """)

    conn.commit()
    conn.close()


# ✅ Add Transaction
def add_transaction(merchant, amount, account_id, txn_type, category, txn_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert transaction
    cursor.execute("""
        INSERT INTO transactions
        (merchant, amount, account_id, txn_type, category, txn_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (merchant, amount, account_id, txn_type, category, txn_date))

    # Update account balance
    if txn_type == "expense":
        cursor.execute("""
            UPDATE accounts
            SET balance = balance - ?
            WHERE id = ?
        """, (amount, account_id))
    else:
        cursor.execute("""
            UPDATE accounts
            SET balance = balance + ?
            WHERE id = ?
        """, (amount, account_id))

    conn.commit()
    conn.close()


# ✅ Get All Transactions
def get_all_transactions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            t.id,              -- ✅ ADD THIS
            t.merchant,
            t.amount,
            a.name,
            t.txn_type,
            t.category,
            t.txn_date
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        ORDER BY t.txn_date DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data



# ✅ Monthly Summary
def get_transactions_summary(selected_date=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if selected_date:
        cursor.execute("""
            SELECT txn_type, SUM(amount)
            FROM transactions
            WHERE txn_date = ?
            GROUP BY txn_type
        """, (selected_date,))
    else:
        cursor.execute("""
            SELECT txn_type, SUM(amount)
            FROM transactions
            GROUP BY txn_type
        """)

    rows = cursor.fetchall()
    conn.close()

    total_income = 0
    total_expense = 0

    for txn_type, total in rows:
        if txn_type == "income":
            total_income = total or 0
        elif txn_type == "expense":
            total_expense = total or 0

    net_balance = total_income - total_expense

    return total_income, total_expense, net_balance



def get_transactions_by_month(month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT merchant, amount, category, txn_date
        FROM transactions
        WHERE txn_date LIKE ?
    """, (month + "%",))

    data = cursor.fetchall()
    conn.close()
    return data

# ✅ Delete Transaction
def delete_transaction(txn_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get transaction first
    cursor.execute("""
        SELECT amount, account_id, txn_type
        FROM transactions
        WHERE id = ?
    """, (txn_id,))
    
    row = cursor.fetchone()

    if row:
        amount, account_id, txn_type = row

        # Reverse balance
        if txn_type == "expense":
            cursor.execute("""
                UPDATE accounts
                SET balance = balance + ?
                WHERE id = ?
            """, (amount, account_id))
        else:
            cursor.execute("""
                UPDATE accounts
                SET balance = balance - ?
                WHERE id = ?
            """, (amount, account_id))

        # Delete transaction
        cursor.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))

    conn.commit()
    conn.close()

def get_transaction_by_id(txn_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, merchant, amount, account_id, txn_type, category, txn_date
        FROM transactions
        WHERE id = ?
    """, (txn_id,))

    data = cursor.fetchone()
    conn.close()
    return data


def update_transaction_by_id(
    txn_id,
    merchant,
    amount,
    account_id,
    txn_type,
    category,
    txn_date
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transactions
        SET merchant = ?,
            amount = ?,
            account_id = ?,
            txn_type = ?,
            category = ?,
            txn_date = ?
        WHERE id = ?
    """, (merchant, amount, account_id, txn_type, category, txn_date, txn_id))

    conn.commit()
    conn.close()



def get_transactions_by_date(selected_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            t.id,
            t.merchant,
            t.amount,
            
            a.name,
            t.txn_type,
            t.category,
            t.txn_date
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.txn_date = ?
        ORDER BY t.txn_date DESC
    """, (selected_date,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_monthly_analysis():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            substr(txn_date, 1, 7) as month,
            txn_type,
            SUM(amount)
        FROM transactions
        GROUP BY month, txn_type
        ORDER BY month
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

def get_category_analysis_by_date(selected_date=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if selected_date:
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE txn_date = ?
            GROUP BY category
        """, (selected_date,))
    else:
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            GROUP BY category
        """)

    data = cursor.fetchall()
    conn.close()
    return data

def get_spent_by_category_and_month(category, month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE category = ?
        AND txn_type = 'expense'
        AND txn_date LIKE ?
    """, (category, month + "%"))

    result = cursor.fetchone()[0]
    conn.close()

    return result if result else 0

def get_period_summary(start_date, end_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT txn_type, SUM(amount)
        FROM transactions
        WHERE txn_date BETWEEN ? AND ?
        GROUP BY txn_type
    """, (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    income = 0
    expense = 0

    for txn_type, total in rows:
        if txn_type == "income":
            income = total or 0
        elif txn_type == "expense":
            expense = total or 0

    return income, expense

def get_monthly_income_expense_trend(selected_date=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 🔹 If specific date selected → show only that date
    if selected_date:
        cursor.execute("""
            SELECT 
                txn_date,
                SUM(CASE WHEN txn_type='income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN txn_type='expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE txn_date = ?
            GROUP BY txn_date
        """, (selected_date,))
    else:
        # 🔹 If no date → show monthly trend
        cursor.execute("""
            SELECT 
                substr(txn_date,1,7) as month,
                SUM(CASE WHEN txn_type='income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN txn_type='expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            GROUP BY month
            ORDER BY month
        """)

    rows = cursor.fetchall()
    conn.close()

    labels = []
    income = []
    expense = []

    for row in rows:
        labels.append(row[0])
        income.append(row[1] if row[1] else 0)
        expense.append(row[2] if row[2] else 0)

    return labels, income, expense