from database.db import connect_db
from datetime import datetime

def check_alert(category):

    conn = connect_db()
    cursor = conn.cursor()

    # Total spent in current month
    month = datetime.now().strftime("%Y-%m")

    cursor.execute("""
    SELECT SUM(amount) FROM transactions
    WHERE category=? AND date LIKE ?
    """, (category, month+"%"))

    spent = cursor.fetchone()[0] or 0

    # Budget limit
    cursor.execute("""
    SELECT monthly_limit FROM budgets WHERE category=?
    """, (category,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return f"No budget limit set for {category}"

    limit = row[0]

    if spent > limit:
        return f"⚠ You have spent ₹{spent} in {category} this month. Limit was ₹{limit}"

    return f"✅ Spending in {category} is within limit (₹{spent}/₹{limit})"
