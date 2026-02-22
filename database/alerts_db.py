import sqlite3

DB_NAME = "finance_new.db"

def init_alerts_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        message TEXT,
        month TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def add_alert(category, message, month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (category, message, month)
        VALUES (?, ?, ?)
    """, (category, message, month))

    conn.commit()
    conn.close()


def get_alerts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, category, message, created_at
        FROM alerts
        ORDER BY created_at DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data

def delete_alert(alert_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))

    conn.commit()
    conn.close()