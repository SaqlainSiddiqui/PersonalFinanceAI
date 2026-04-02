from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from config import Config
from extensions import db, login_manager
from collections import defaultdict
from models import Transaction
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash
from werkzeug.security import generate_password_hash
import pandas as pd
import nltk
import re
import calendar
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and user.check_password(request.form["password"]):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid password, please try again.", "error")

    return render_template("login.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Check current password
        if not current_user.check_password(current_password):
            flash("Current password is incorrect.")
            return redirect(url_for("profile"))

        # Check new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for("profile"))

        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Password updated successfully!")
        return redirect(url_for("profile"))

    return render_template("profile.html")


@app.route("/add_transaction", methods=["POST"])
@login_required
def add_transaction():

    amount = float(request.form["amount"])
    category = request.form["category"]
    t_type = request.form["type"]
    description = request.form["description"]

    date_str = request.form.get("date")
    transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    recurring_type = request.form["is_recurring"]

    is_recurring = True if recurring_type == "monthly" else False

    new_transaction = Transaction(
        user_id=current_user.id,
        amount=amount,
        category=category,
        type=t_type,
        description=description,
        date=transaction_date,

        # ✅ FIXED LOGIC
        is_recurring=is_recurring,
        recurring_type="monthly" if is_recurring else None,
        last_generated=transaction_date if is_recurring else None
    )

    db.session.add(new_transaction)
    db.session.commit()

    selected_month = request.form.get("month")

    return redirect(url_for("dashboard", month=selected_month))


@app.route("/toggle_theme", methods=["POST"])
@login_required
def toggle_theme():

    if current_user.theme_mode == "light":
        current_user.theme_mode = "dark"
    else:
        current_user.theme_mode = "light"

    db.session.commit()

    return {"status": "success", "theme": current_user.theme_mode}



@app.route("/delete_transaction/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)

    # Security check (important)
    if transaction.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(transaction)
    db.session.commit()

    selected_month = request.form.get("month")

    return redirect(url_for("dashboard", month=selected_month))



@app.route("/edit_transaction/<int:transaction_id>", methods=["POST"])
@login_required
def edit_transaction(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)

    # Security check
    if transaction.user_id != current_user.id:
        return "Unauthorized", 403

    transaction.amount = float(request.form["amount"])
    transaction.category = request.form["category"]
    transaction.type = request.form["type"]
    transaction.description = request.form["description"]
    transaction.date = datetime.strptime(
        request.form["date"], "%Y-%m-%d"
    ).date()

    db.session.commit()

    selected_month = request.form.get("month")

    return redirect(url_for("dashboard", month=selected_month))



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login instead.")
            return redirect(url_for("register"))

        # Check if username exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash("Username already taken.")
            return redirect(url_for("register"))
        
        password = request.form["password"]

        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$', password):
            flash("Password must be at least 8 characters and include uppercase, number, and special character.")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/chat", methods=["POST"])
@login_required
def chat():

    user_message = request.json.get("message")
    selected_month = request.json.get("month")

    transactions = current_user.transactions

    data = [{
        "amount": t.amount,
        "type": t.type,
        "category": t.category,
        "date": t.date
    } for t in transactions]

    df = pd.DataFrame(data)

    response = process_user_query(user_message, df, selected_month)

    return {"response": response}


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


def generate_recurring_transactions(user):

    today = datetime.today().date()

    recurring_transactions = Transaction.query.filter_by(
        user_id=user.id,
        is_recurring=True
    ).all()

    for t in recurring_transactions:

        if t.recurring_type == "monthly":

            # Start from last generated OR original date
            last_date = t.last_generated if t.last_generated else t.date

            while True:

                next_date = last_date + relativedelta(months=1)

                # Stop if future
                if next_date > today:
                    break

                # Check duplicate
                exists = Transaction.query.filter_by(
                    user_id=user.id,
                    date=next_date,
                    amount=t.amount,
                    category=t.category,
                    type=t.type
                ).first()

                if not exists:
                    new_entry = Transaction(
                        user_id=user.id,
                        amount=t.amount,
                        category=t.category,
                        type=t.type,
                        description=t.description,
                        date=next_date,   # ✅ SAME DAY (15th, etc.)
                        is_recurring=True,
                        recurring_type="monthly",
                        last_generated=next_date
                    )

                    db.session.add(new_entry)

                last_date = next_date

            # Update last generated
            t.last_generated = last_date

    db.session.commit()


def generate_ai_suggestions(df):

    suggestions = []

    if df.empty:
        return ["No transactions available for analysis."]

    # Ensure datetime
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")

    # Get last 3 months
    months = sorted(df["month"].unique())
    recent_months = months[-3:]
    df = df[df["month"].isin(recent_months)]

    income_df = df[df["type"] == "income"]
    expense_df = df[df["type"] == "expense"]

    total_income = income_df["amount"].sum()
    total_expense = expense_df["amount"].sum()

    # 🧠 1. Savings Analysis
    if total_income > 0:
        savings_rate = ((total_income - total_expense) / total_income) * 100

        if savings_rate < 20:
            suggestions.append(
                f"⚠ Your savings rate is only {savings_rate:.1f}%. Try saving at least 20%."
            )
        else:
            suggestions.append(
                f"✅ Good savings habit! You save {savings_rate:.1f}% of your income."
            )

    # 🧠 2. Expense Ratio Insight
    if total_income > 0:
        expense_ratio = (total_expense / total_income) * 100

        if expense_ratio > 90:
            suggestions.append("🚨 You are spending more than 90% of your income.")
        elif expense_ratio > 75:
            suggestions.append("⚠ You are spending over 75% of your income.")

    # 🧠 3. Category Analysis
    category_spend = expense_df.groupby("category")["amount"].sum()

    if not category_spend.empty:
        top_category = category_spend.idxmax()
        top_value = category_spend.max()
        percent = (top_value / total_expense) * 100

        suggestions.append(
            f"📊 {top_category} accounts for {percent:.1f}% of your total expenses."
        )

        if percent > 40:
            suggestions.append(
                f"👉 Try reducing {top_category} expenses by 10-15% to improve savings."
            )

    # 🧠 4. Monthly Trend Analysis
    monthly_expense = expense_df.groupby("month")["amount"].sum()

    if len(monthly_expense) >= 2:
        last = monthly_expense.iloc[-1]
        prev = monthly_expense.iloc[-2]

        if prev > 0:
            change = ((last - prev) / prev) * 100

            if change > 10:
                suggestions.append(
                    f"📈 Your expenses increased by {change:.1f}% compared to last month."
                )
            elif change < -10:
                suggestions.append(
                    f"📉 Good job! Expenses decreased by {abs(change):.1f}% from last month."
                )

    # 🧠 5. Smart Prediction (average of last 3 months)
    monthly_income = income_df.groupby("month")["amount"].sum()
    monthly_expense = expense_df.groupby("month")["amount"].sum()

    avg_income = monthly_income.mean() if not monthly_income.empty else 0
    avg_expense = monthly_expense.mean() if not monthly_expense.empty else 0

    predicted_balance = avg_income - avg_expense

    suggestions.append(
        f"🔮 Based on recent trends, your next month's balance may be around ₹{predicted_balance:.2f}."
    )

    return suggestions if suggestions else ["Your finances look stable."]


def process_user_query(query, df, selected_month):

    query = query.lower()

    if df.empty:
        return "No transaction data available."

    # Add month column
    df["month"] = df["date"].apply(lambda x: x.strftime("%Y-%m"))

    base_month = datetime.strptime(selected_month, "%Y-%m")

    prev_month = (base_month - relativedelta(months=1)).strftime("%Y-%m")
    prev2_month = (base_month - relativedelta(months=2)).strftime("%Y-%m")

    query = query.lower()

    # DEFAULT → current dashboard month
    target_month = selected_month

    if "last month" in query:
        target_month = prev_month

    elif "2 months ago" in query:
        target_month = prev2_month

    # Explicit month name (jan, feb, etc.)
    else:
        for i in range(1, 13):
            month_name = calendar.month_name[i].lower()
            if month_name in query:
                year = base_month.year
                target_month = f"{year}-{i:02d}"
                break

    monthly_df = df[df["month"] == target_month]

    if monthly_df.empty:
        return "No data found for that month."

    income = monthly_df[monthly_df["type"] == "income"]["amount"].sum()
    expense = monthly_df[monthly_df["type"] == "expense"]["amount"].sum()
    balance = income - expense

    # ---- Intent Detection ----

    if "balance" in query:
        return f"Your balance for {target_month} is ₹{balance:.2f}"

    if "income" in query:
        return f"Your income for {target_month} is ₹{income:.2f}"

    if "expense" in query or "spend" in query:
        return f"Your expenses for {target_month} are ₹{expense:.2f}"

    # Category specific detection
    for category in monthly_df["category"].unique():
        if category.lower() in query:
            cat_total = monthly_df[
                (monthly_df["category"].str.lower() == category.lower()) &
                (monthly_df["type"] == "expense")
            ]["amount"].sum()

            return f"You spent ₹{cat_total:.2f} on {category} in {target_month}."

    return f"For {target_month}: Income ₹{income:.2f}, Expense ₹{expense:.2f}, Balance ₹{balance:.2f}"



def forecast_next_month(df):

    if df.empty:
        return None, None, None

    df["month"] = df["date"].apply(lambda x: x.strftime("%Y-%m"))

    monthly_income = (
        df[df["type"] == "income"]
        .groupby("month")["amount"]
        .sum()
        .reset_index()
    )

    monthly_expense = (
        df[df["type"] == "expense"]
        .groupby("month")["amount"]
        .sum()
        .reset_index()
    )

    if len(monthly_income) < 2 or len(monthly_expense) < 2:
        return None, None, None

    # Add month index
    monthly_income["month_index"] = range(len(monthly_income))
    monthly_expense["month_index"] = range(len(monthly_expense))

    # Income model
    income_model = LinearRegression()
    income_model.fit(
        monthly_income[["month_index"]],
        monthly_income["amount"]
    )

    next_index = [[len(monthly_income)]]
    predicted_income = income_model.predict(next_index)[0]

    # Expense model
    expense_model = LinearRegression()
    expense_model.fit(
        monthly_expense[["month_index"]],
        monthly_expense["amount"]
    )

    predicted_expense = expense_model.predict(next_index)[0]

    predicted_balance = predicted_income - predicted_expense

    return (
        round(predicted_income, 2),
        round(predicted_expense, 2),
        round(predicted_balance, 2)
    )


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    generate_recurring_transactions(current_user)

    # ✅ ALWAYS SET MONTH FIRST
    selected_month = request.args.get("month")
    current_month = datetime.today().strftime("%Y-%m")

    if not selected_month:
        selected_month = current_month

    transactions = current_user.transactions

    # ✅ FILTER BASED ON SELECTED MONTH
    filtered_transactions = []

    for t in transactions:
        transaction_month = t.date.strftime("%Y-%m")

        if transaction_month == selected_month:
            filtered_transactions.append(t)

    # Sort latest first
    filtered_transactions = sorted(
        filtered_transactions,
        key=lambda x: x.date,
        reverse=True
    )

    # ✅ SAFE DATAFRAME CREATION
    if transactions:
        data = [{
            "amount": t.amount,
            "type": t.type,
            "category": t.category,
            "date": t.date
        } for t in transactions]

        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(columns=["amount", "type", "category", "date"])

    # ML Forecast
    predicted_income, predicted_expense, predicted_balance = forecast_next_month(df)

    # ✅ MONTH COLUMN SAFE
    if not df.empty:
        df["month"] = df["date"].apply(lambda x: x.strftime("%Y-%m"))
        monthly_df = df[df["month"] == selected_month]
    else:
        monthly_df = pd.DataFrame(columns=["amount", "type", "category", "date"])

    # ✅ SAFE CALCULATIONS
    if not monthly_df.empty and "type" in monthly_df.columns:
        total_income = monthly_df[monthly_df["type"] == "income"]["amount"].sum()
        total_expense = monthly_df[monthly_df["type"] == "expense"]["amount"].sum()
    else:
        total_income = 0
        total_expense = 0

    balance = total_income - total_expense

    ai_suggestions = generate_ai_suggestions(monthly_df)

    # Category breakdown
    expense_df = monthly_df[monthly_df["type"] == "expense"]

    category_summary = (
        expense_df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
        if not expense_df.empty else {}
    )

    top_category = list(category_summary.keys())[0] if category_summary else "N/A"

    # Chart Data
    labels = list(category_summary.keys())
    values = list(category_summary.values())


    return render_template(
        "index.html",
        transactions=filtered_transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        labels=labels,
        values=values,
        theme=current_user.theme_mode,
        selected_month=selected_month,
        top_category=top_category,
        transaction_count=len(monthly_df),
        ai_suggestions=ai_suggestions,
        predicted_income=predicted_income,
        predicted_expense=predicted_expense,
        predicted_balance=predicted_balance,
    )
    



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)