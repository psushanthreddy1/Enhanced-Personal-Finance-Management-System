from fpdf import FPDF
from database.db import connect_db
from datetime import datetime

def generate_pdf():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT category, monthly_limit FROM budgets")
    budgets = cursor.fetchall()

    month = datetime.now().strftime("%B %Y")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200,10,txt=f"Monthly Expense Report - {month}",ln=True,align="C")
    pdf.ln(10)

    pdf.cell(60,10,"Category",1)
    pdf.cell(60,10,"Limit",1)
    pdf.cell(60,10,"Spent",1)
    pdf.ln()

    for cat, limit in budgets:

        cursor.execute("""
        SELECT SUM(amount) FROM transactions
        WHERE category=?
        """, (cat,))

        spent = cursor.fetchone()[0] or 0

        pdf.cell(60,10,cat,1)
        pdf.cell(60,10,str(limit),1)
        pdf.cell(60,10,str(spent),1)
        pdf.ln()

    conn.close()

    pdf.output("Monthly_Report.pdf")

    return "Monthly_Report.pdf"
