from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


from ingestion.bank_fetcher import BankTransactionFetcher
from categorization.hybrid_classifier import hybrid_predict

from database.transactions_db import delete_transaction, get_all_transactions

from categorization.category_mapper import auto_category
from datetime import date
from datetime import datetime

from fastapi.responses import StreamingResponse
import openpyxl
from io import BytesIO

from fastapi.responses import RedirectResponse
from fastapi import Form


from database.budgets_db import init_budget_table, add_budget, get_budgets,save_budget


from database.accounts_db import (
    init_accounts_table,
    add_account, 
    get_accounts,
    get_account_summary,
    
    hide_account,
    delete_account,
    get_account,
    update_account
)

from database.transactions_db import (
    init_transactions_table,
    add_transaction,
    get_transactions_by_month,
    get_transactions_summary,
    get_transactions_by_date,
    get_period_summary,
    get_monthly_income_expense_trend
    
)

from database.alerts_db import (
    init_alerts_table,
    add_alert,
    get_alerts,
    delete_alert
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

fetcher = BankTransactionFetcher()

# ✅ Initialize Accounts Table
init_accounts_table()

# ✅ Initialize Transactions Table
init_transactions_table()


init_budget_table()

init_alerts_table()

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):

    if username == "admin" and password == "1234":

        response = RedirectResponse("/", status_code=303)
        response.set_cookie(key="user", value=username)

        return response

    return RedirectResponse("/login", status_code=303)

# ============================================================
# ✅ HOME PAGE
# ============================================================

from fastapi import Query
from datetime import datetime, timedelta

@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    selected_month: str = Query(None)
):

    today = datetime.today()

    # ---------------- TODAY ----------------
    today_str = today.strftime("%Y-%m-%d")

    today_income, today_expense = get_period_summary(
        today_str,
        today_str
    )

    # ---------------- THIS WEEK ----------------
    start_week = today - timedelta(days=today.weekday())

    week_income, week_expense = get_period_summary(
        start_week.strftime("%Y-%m-%d"),
        today_str
    )

    # ---------------- MONTH ----------------
    if selected_month:
        month_start = datetime.strptime(selected_month + "-01", "%Y-%m-%d")
    else:
        selected_month = today.strftime("%Y-%m")
        month_start = today.replace(day=1)

    month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    month_income, month_expense = get_period_summary(
        month_start.strftime("%Y-%m-%d"),
        month_end.strftime("%Y-%m-%d")
    )

    # ---------------- YEAR ----------------
    year_start = month_start.replace(month=1, day=1)

    year_income, year_expense = get_period_summary(
        year_start.strftime("%Y-%m-%d"),
        month_end.strftime("%Y-%m-%d")
    )

    accounts = get_accounts()
    total_assets, total_liabilities, net_assets = get_account_summary()

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "accounts": accounts,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_assets": net_assets,
            "today_income": today_income,
            "today_expense": today_expense,
            "week_income": week_income,
            "week_expense": week_expense,
            "month_income": month_income,
            "month_expense": month_expense,
            "year_income": year_income,
            "year_expense": year_expense,
            "selected_month": selected_month
        }
    )
# ============================================================
# ✅ TRANSACTIONS PAGE
# ============================================================

from fastapi import Query
import calendar
from datetime import datetime

@app.get("/transactions", response_class=HTMLResponse)
def transactions(
    request: Request,
    selected_date: str = Query(None),
    month: int = Query(None),
    year: int = Query(None),
    txn_type: str = Query(None),
    search: str = Query(None)   # ✅ NEW
):

    today = datetime.today()

    # ---------------- MONTH SET ----------------
    if not month:
        month = today.month
    if not year:
        year = today.year

    month_name = datetime(year, month, 1).strftime("%B")

    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)

    alert_message = request.cookies.get("budget_alert")

    # ---------------- DATA ----------------
    if selected_date:
        transactions = get_transactions_by_date(selected_date)
        total_income, total_expense, net_balance = get_transactions_summary(selected_date)
    else:
        transactions = get_all_transactions()
        total_income, total_expense, net_balance = get_transactions_summary()

    # ---------------- TYPE FILTER ----------------
    if txn_type:
        transactions = [t for t in transactions if t[4] == txn_type]

    # ---------------- SEARCH FILTER ----------------
    if search:
        search_lower = search.lower()

        transactions = [
            t for t in transactions
            if search_lower in str(t[1]).lower()   # merchant
            or search_lower in str(t[5]).lower()   # category
            or search_lower in str(t[3]).lower()   # account
        ]

    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            "transactions": transactions,
            "calendar": cal,
            "month_name": month_name,
            "year": year,
            "month": month,
            "today": today.day,
            "selected_date": selected_date,
            "accounts": get_accounts(),
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "alert_message": alert_message,
            "txn_type": txn_type,
            "search": search   # ✅ PASS TO HTML
        }
    )
@app.get("/export-transactions")
def export_transactions():

    transactions = get_all_transactions()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transactions"

    # Header Row
    ws.append([
        "Merchant",
        "Amount",
        "Account",
        "Type",
        "Category",
        "Date"
    ])

    # Data Rows
    for t in transactions:
        ws.append([
            t[1],
            t[2],
            t[3],
            t[4],
            t[5],
            t[6]
        ])

    file = BytesIO()
    wb.save(file)
    file.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=transactions.xlsx"
    }

    return StreamingResponse(
        file,
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

import pandas as pd
import sqlite3
from fastapi import UploadFile, File

@app.post("/import-transactions")
async def import_transactions(file: UploadFile = File(...)):

    contents = await file.read()

    # Read Excel
    if file.filename.endswith(".xlsx"):
        df = pd.read_excel(BytesIO(contents))

    # Read CSV
    elif file.filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(contents))

    else:
        return {"error": "Unsupported file format"}

    conn = sqlite3.connect("finance_new.db")
    cursor = conn.cursor()

    for _, row in df.iterrows():

        cursor.execute("""
        INSERT INTO transactions
        (merchant, amount, account_id, txn_type, category, txn_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["Merchant"],
            row["Amount"],
            1,
            row["Type"],
            row["Category"],
            row["Date"]
        ))

    conn.commit()
    conn.close()

    return RedirectResponse("/transactions", status_code=303)
@app.get("/delete-transaction/{txn_id}")
def delete_transaction_route(txn_id: int):
    delete_transaction(txn_id)
    return RedirectResponse("/transactions", status_code=303)

@app.get("/edit-transaction/{txn_id}", response_class=HTMLResponse)
def edit_transaction_page(request: Request, txn_id: int):
    
    from database.transactions_db import get_transaction_by_id
    
    txn = get_transaction_by_id(txn_id)

    return templates.TemplateResponse(
        "edit_transaction.html",
        {
            "request": request,
            "txn": txn
        }
    )

@app.post("/save-transaction")
def save_transaction(
    request: Request,
    merchant: str = Form(...),
    amount: float = Form(...),
    account_id: int = Form(...),
    txn_type: str = Form(...),
    txn_date: str = Form(...)
):

    merchant_lower = merchant.lower()

    # ---------- CATEGORY LOGIC ----------
    if txn_type == "expense":

        if "grocery" in merchant_lower:
            category = "Groceries"
        elif "rent" in merchant_lower:
            category = "Rent"
        elif "food" in merchant_lower:
            category = "Food"
        else:
            category = "Other Expense"

    else:
        category = "Other Income"

    # ---------- SAVE TRANSACTION ----------
    add_transaction(
        merchant,
        amount,
        account_id,
        txn_type,
        category,
        txn_date
    )

    # ---------- CHECK BUDGET ----------
    alert_message = None

    if txn_type == "expense":

        month = datetime.strptime(txn_date, "%Y-%m-%d").strftime("%Y-%m")
        budgets = get_budgets(month)

        for b in budgets:
            budget_category = b[0]
            budget_amount = b[1]

            if budget_category == category:

                spent = get_spent_by_category_and_month(category, month)

                if spent > budget_amount:

                    alert_message = (
                        f"{category} budget exceeded! "
                        f"Budget: {budget_amount} | Spent: {spent}"
                    )

                    add_alert(category, alert_message, month)

    # ---------- REDIRECT (FIXED) ----------
    response = RedirectResponse("/transactions", status_code=303)

    if alert_message:
        response.set_cookie("budget_alert", alert_message)

    return response

@app.post("/update-transaction/{txn_id}")
def update_transaction_route(
    txn_id: int,
    merchant: str = Form(...),
    amount: float = Form(...),
    account_id: int = Form(...),
    txn_type: str = Form(...),
    txn_date: str = Form(...)
):

    # CATEGORY LOGIC AGAIN
    merchant_lower = merchant.lower()

    if txn_type == "expense":
        if "grocery" in merchant_lower:
            category = "Groceries"
        elif "rent" in merchant_lower:
            category = "Rent"
        elif "food" in merchant_lower:
            category = "Food"
        else:
            category = "Other Expense"
    else:
        category = "Other Income"

    from database.transactions_db import update_transaction_by_id

    update_transaction_by_id(
        txn_id,
        merchant,
        amount,
        account_id,
        txn_type,
        category,
        txn_date
    )

    return RedirectResponse("/transactions", status_code=303)
# ============================================================
# ✅ OTHER PAGES
# ============================================================

from database.transactions_db import get_spent_by_category_and_month
from database.budgets_db import get_budgets  # if you have this

@app.get("/budget", response_class=HTMLResponse)
def budget(request: Request):

    today = date.today()
    current_month = today.strftime("%Y-%m")

    budgets = get_budgets(current_month)

    updated_budgets = []
    alerts = []   # 🔥 NEW

    for b in budgets:
        category = b[0]
        budget_amount = b[1]

        spent = get_spent_by_category_and_month(category, current_month)
        remaining = budget_amount - spent

        # 🚨 If overspent → add alert
        if remaining < 0:
            alerts.append(
                f"{category} exceeded budget by ₹ {abs(remaining)}"
            )

        updated_budgets.append((
            category,
            budget_amount,
            spent,
            remaining
        ))

    return templates.TemplateResponse(
        "budget.html",
        {
            "request": request,
            "budgets": updated_budgets,
            "month": current_month,
            "alerts": alerts   # 🔥 PASS ALERTS
        }
    )
@app.post("/add-budget")
def create_budget(
    category: str = Form(...),
    amount: float = Form(...),
    month: str = Form(...)
):
    add_budget(category, amount, month)
    return RedirectResponse("/budget", status_code=303)

@app.post("/save-budget")
def save_budget_route(
    category: str = Form(...),
    budget_amount: float = Form(...)
):
    month = datetime.now().strftime("%Y-%m")

    save_budget(category, month, budget_amount)

    return RedirectResponse("/budget", status_code=303)

@app.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request):

    # ✅ Default Month = Current Month
    today = date.today()
    month = today.strftime("%Y-%m")

    transactions = get_transactions_by_month(month)

    return templates.TemplateResponse(
        "category_groups.html",
        {
            "request": request,
            "transactions": transactions,
            "month": month
        }
    )


@app.get("/categories/{group_name}", response_class=HTMLResponse)
def category_detail(request: Request, group_name: str):

    sample_categories = {
        "bills": ["Electricity", "Internet", "Rent"],
        "needs": ["Groceries", "Transport"],
        "wants": ["Dining", "Movies"]
    }

    categories = sample_categories.get(group_name.lower(), [])

    return templates.TemplateResponse(
        "category_detail.html",
        {
            "request": request,
            "group": group_name.upper(),
            "categories": categories
        }
    )


@app.get("/forecast", response_class=HTMLResponse)
def forecast(request: Request):
    return templates.TemplateResponse("forecast.html", {"request": request})

@app.get("/alerts", response_class=HTMLResponse)
def alerts(request: Request):

    alerts_data = get_alerts()

    return templates.TemplateResponse(
        "alerts.html",
        {
            "request": request,
            "alerts": alerts_data
        }
    )

@app.get("/delete-alert/{alert_id}")
def delete_alert_route(alert_id: int):
    delete_alert(alert_id)
    return RedirectResponse("/alerts", status_code=303)

from fastapi import Query
from database.transactions_db import get_category_analysis_by_date

@app.get("/analysis", response_class=HTMLResponse)
def analysis(
    request: Request,
    view: str = Query("category"),
    selected_date: str = Query(None),
    sort_by: str = Query("amount"),
    chart_type: str = Query("pie")
):

    # ================= CATEGORY =================
    if view == "category":

        data = get_category_analysis_by_date(selected_date)
        data = list(data)

        if sort_by == "amount":
            data.sort(key=lambda x: x[1], reverse=True)
        elif sort_by == "category":
            data.sort(key=lambda x: x[0].lower())

        labels = [row[0] for row in data]
        amounts = [row[1] for row in data]

        return templates.TemplateResponse(
            "analysis.html",
            {
                "request": request,
                "view": view,
                "labels": labels,
                "amounts": amounts,
                "selected_date": selected_date,
                "sort_by": sort_by,
                "chart_type": chart_type
            }
        )

    # ================= TREND =================
    elif view == "trend":

        months, income, expense = get_monthly_income_expense_trend(selected_date)

        print("Months:", months)
        print("Income:", income)
        print("Expense:", expense)

        return templates.TemplateResponse(
            "analysis.html",
            {
                "request": request,
                "view": view,
                "months": months,
                "income": income,
                "expense": expense,
                "selected_date": selected_date,
                "chart_type": chart_type
            }
        )

    # ================= ASSET =================
    elif view == "asset":

        months, income, expense = get_monthly_income_expense_trend(selected_date)

        return templates.TemplateResponse(
            "analysis.html",
            {
                "request": request,
                "view": view,
                "months": months,
                "income": income,
                "expense": expense,
                "selected_date": selected_date,
                "chart_type": chart_type
            }
        )
# ============================================================
# ✅ ACCOUNTS MODULE
# ============================================================

# ✅ ACCOUNTS PAGE
from datetime import date

from fastapi import Query

@app.get("/accounts", response_class=HTMLResponse)
def accounts_page(
    request: Request,
    selected_date: str = Query(None)
):

    accounts = get_accounts(selected_date)
    total_assets, total_liabilities, net_assets = get_account_summary(selected_date)

    return templates.TemplateResponse(
        "accounts.html",
        {
            "request": request,
            "accounts": accounts,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_assets": net_assets,
            "selected_date": selected_date
        }
    )


# ✅ ADD ACCOUNT
@app.post("/add-account")
def create_account(
    acc_category: str = Form(...),
    acc_type: str = Form(...),
    name: str = Form(...),
    currency: str = Form(...),
    balance: float = Form(...),
    description: str = Form("")
):
    add_account(acc_category, acc_type, name, currency, balance, description)
    return RedirectResponse("/accounts", status_code=303)


# ✅ DELETE ACCOUNT
@app.get("/delete-account/{acc_id}")
def delete_account_route(acc_id: int):
    delete_account(acc_id)
    return RedirectResponse("/accounts", status_code=303)


# ✅ HIDE ACCOUNT
@app.get("/hide-account/{acc_id}")
def hide_account_route(acc_id: int):
    hide_account(acc_id)
    return RedirectResponse("/accounts", status_code=303)


# ✅ EDIT ACCOUNT PAGE (FIXED ✅)
@app.get("/edit-account/{acc_id}", response_class=HTMLResponse)
def edit_account_page(request: Request, acc_id: int):

    # ✅ Correct function name
    account = get_account(acc_id)

    return templates.TemplateResponse(
        "edit_account.html",
        {"request": request, "account": account}
    )


# ✅ UPDATE ACCOUNT FORM SUBMISSION
@app.post("/update-account/{acc_id}")
def update_account_route(
    acc_id: int,
    acc_category: str = Form(...),
    acc_type: str = Form(...),
    name: str = Form(...),
    currency: str = Form(...),
    balance: float = Form(...),
    description: str = Form("")
):

    update_account(
        acc_id,
        acc_category,
        acc_type,
        name,
        currency,
        balance,
        description
    )

    return RedirectResponse("/accounts", status_code=303)


# ✅ RECONCILIATION PAGE
@app.get("/reconciliation/{acc_id}", response_class=HTMLResponse)
def reconciliation_page(request: Request, acc_id: int):

    account = get_account(acc_id)

    return templates.TemplateResponse(
        "reconciliation.html",
        {"request": request, "account": account}
    )