import sqlite3

DB_NAME = "finance_new.db"


# ✅ Connect Helper
def connect():
    return sqlite3.connect(DB_NAME)


# ✅ Initialize Table
def init_accounts_table():
    conn = connect()
    cursor = conn.cursor()

    # ✅ Create table with hide_amount
    cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    type TEXT,
    name TEXT,
    currency TEXT,
    balance REAL,
    description TEXT,
    hide_amount INTEGER DEFAULT 0,
    created_date TEXT
)
""")


    # ✅ Add column safely for old DB
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN hide_amount INTEGER DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN created_date TEXT")
    except:
        pass

    conn.commit()
    conn.close()


# ✅ Add Account
from datetime import datetime

def add_account(category, acc_type, name, currency, balance, description):
    conn = connect()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO accounts (category, type, name, currency, balance, description, created_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (category, acc_type, name, currency, balance, description, today))

    conn.commit()
    conn.close()

# ✅ Get Accounts
def get_accounts(selected_date=None):
    conn = connect()
    cursor = conn.cursor()

    if selected_date:
        cursor.execute(
            "SELECT * FROM accounts WHERE created_date = ?",
            (selected_date,)
        )
    else:
        cursor.execute("SELECT * FROM accounts")

    accounts = cursor.fetchall()
    conn.close()
    return accounts



# ✅ Total Assets
# ✅ Total Assets + Liabilities + Net Assets
def get_account_summary(selected_date=None):
    conn = connect()
    cursor = conn.cursor()

    if selected_date:
        cursor.execute(
            "SELECT type, balance FROM accounts WHERE created_date = ?",
            (selected_date,)
        )
    else:
        cursor.execute("SELECT type, balance FROM accounts")

    rows = cursor.fetchall()

    total_assets = 0
    total_liabilities = 0

    for acc_type, balance in rows:
        if acc_type == "liability":
            total_liabilities += balance
        else:
            total_assets += balance

    conn.close()

    net_assets = total_assets - total_liabilities
    return total_assets, total_liabilities, net_assets

from datetime import datetime

def add_account(category, acc_type, name, currency, balance, description):
    conn = connect()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO accounts 
    (category, type, name, currency, balance, description, created_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (category, acc_type, name, currency, balance, description, today))

    conn.commit()
    conn.close()


# ✅ Delete Account
def delete_account(acc_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM accounts WHERE id=?", (acc_id,))

    conn.commit()
    conn.close()


# ✅ Get Single Account
def get_account(acc_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts WHERE id=?", (acc_id,))
    account = cursor.fetchone()

    conn.close()
    return account


# ✅ Update Account
def update_account(acc_id, category, acc_type, name, currency, balance, description):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE accounts
    SET category=?, type=?, name=?, currency=?, balance=?, description=?
    WHERE id=?
    """, (category, acc_type, name, currency, balance, description, acc_id))

    conn.commit()
    conn.close()


# ✅ Hide Amount Toggle
def hide_account(acc_id):
    conn = connect()
    cursor = conn.cursor()

    # Toggle hide_amount
    cursor.execute("""
    UPDATE accounts
    SET hide_amount = CASE 
        WHEN hide_amount = 0 THEN 1
        ELSE 0
    END
    WHERE id=?
    """, (acc_id,))

    conn.commit()
    conn.close()
