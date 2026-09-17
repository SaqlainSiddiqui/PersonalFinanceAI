# Personal Finance AI

A Flask-based **Personal Finance Tracker with AI Budgeting and
Prediction** that helps users record income and expenses, analyze
spending patterns, view monthly financial summaries, receive
AI-generated budgeting suggestions, and forecast the next month's
income, expenses, and balance.

## Project Overview

**Personal Finance AI** is a web application built with Python and
Flask. It combines traditional personal-finance tracking with data
analysis and machine-learning features.

The application provides:

-   User registration and login
-   Secure password hashing
-   Income and expense tracking
-   Monthly transaction filtering
-   Add, edit, and delete transactions
-   Monthly recurring transactions
-   Income, expense, and balance calculations
-   Expense-category analysis
-   Doughnut chart visualization
-   AI-style financial suggestions based on recent transactions
-   Next-month financial forecasting using Linear Regression
-   A finance chatbot for transaction-related questions
-   Light and dark theme support
-   Profile and password-management functionality
-   Responsive glassmorphism-style interface

## Technology Stack

  Component              Technology
  ---------------------- ------------------------------------
  Programming Language   Python
  Web Framework          Flask
  Database               SQLite
  ORM                    Flask-SQLAlchemy
  Authentication         Flask-Login
  Password Security      Werkzeug
  Data Analysis          Pandas
  Machine Learning       Scikit-learn
  Numerical Processing   NumPy
  Frontend               HTML, CSS, JavaScript
  Charts                 Chart.js
  Styling                Glassmorphism + animated gradients

## Main Features

### 1. User Authentication

Users can create an account using:

-   Username
-   Email
-   Password

Passwords are stored as hashes rather than plain text. Registration also
validates password strength using the following requirements:

-   At least 8 characters
-   At least one uppercase letter
-   At least one number
-   At least one special character

Users can log in and log out securely through Flask-Login.

### 2. Personal Finance Dashboard

The dashboard displays the selected month's:

-   Total income
-   Total expenses
-   Remaining balance
-   Transaction count
-   Highest-spending category
-   Expense category breakdown
-   Financial suggestions
-   Forecast information

Transactions are displayed with the newest transactions first.

### 3. Transaction Management

Users can add transactions with:

-   Amount
-   Category
-   Type --- income or expense
-   Description
-   Date
-   Recurring status

Existing transactions can be edited or deleted.

The application also checks transaction ownership before allowing edit
or delete operations.

### 4. Recurring Transactions

Monthly recurring transactions can automatically generate future
entries.

The application:

1.  Finds recurring transactions.
2.  Calculates the next monthly date.
3.  Checks whether the transaction already exists.
4.  Creates the missing transaction when necessary.
5.  Updates the last generated date.

This helps users track recurring items such as monthly bills,
subscriptions, rent, or salary.

### 5. Expense Analysis

Expense data is grouped by category to calculate category-wise spending.

For example:

``` text
Food       ₹5,000
Transport  ₹2,500
Shopping   ₹3,000
Bills      ₹4,000
```

The dashboard can identify the category contributing the most to total
expenses.

### 6. AI Financial Suggestions

The application analyzes recent financial data and generates rule-based
suggestions.

The analysis includes:

-   Savings-rate analysis
-   Expense-to-income ratio
-   Highest-spending category
-   Month-to-month expense changes
-   Average income over recent months
-   Average expenses over recent months
-   Estimated next-month balance

Example suggestions include:

> Your savings rate is only 15%. Try saving at least 20%.

> Food accounts for 42% of your total expenses.

> Your expenses increased compared to last month.

These suggestions are generated from the user's transaction data rather
than from an external generative-AI API.

### 7. Financial Forecasting

The application uses **Scikit-learn Linear Regression** to estimate:

-   Next month's income
-   Next month's expenses
-   Next month's balance

The forecast is generated from historical monthly income and expense
totals.

A minimum of two months of income and expense data is required before a
forecast can be produced.

The forecast should be treated as an analytical estimate rather than a
guaranteed financial prediction.

### 8. Finance Chatbot

The dashboard includes a transaction-aware chat feature.

The chatbot can answer questions related to the user's financial
records, including:

-   Monthly balance
-   Monthly income
-   Monthly expenses
-   Category-specific spending
-   Previous-month spending
-   Two-months-ago spending

Example:

``` text
User: What was my expense last month?

Assistant: Your expenses for 2026-08 are ₹12,500.00
```

The chatbot uses the currently selected dashboard month as its reference
point.

### 9. Data Visualization

The dashboard uses a doughnut chart to visualize expense distribution by
category.

The chart includes:

-   Expense categories
-   Category amounts
-   A total-expense value in the center
-   A responsive layout

### 10. Theme Switching

Users can switch between:

-   Light mode
-   Dark mode

The selected theme is stored for the individual user.

### 11. Profile Management

The profile page displays the user's:

-   Username
-   Email

Users can also change their password by providing:

-   Current password
-   New password
-   Password confirmation

## Project Structure

``` text
PersonalFinanceAI/
│
├── app.py
├── ai_engine.py
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
├── database.db
│
├── instance/
│   └── database.db
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── profile.html
│
├── static/
│   ├── style.css
│   ├── auth.css
│   ├── script.js
│   └── auth.js
│
└── venv/
    └── Python virtual environment
```

### Important files

**`app.py`**

Contains the main Flask application, routes, authentication flow,
transaction management, recurring transaction generation, financial
analysis, chatbot logic, and forecasting.

**`models.py`**

Defines the database models:

-   `User`
-   `Transaction`

**`config.py`**

Contains Flask configuration, including the SQLite database connection
and secret key.

**`extensions.py`**

Initializes Flask-SQLAlchemy and Flask-Login.

**`templates/`**

Contains the application's HTML pages.

**`static/`**

Contains CSS and JavaScript files for styling, animations, charts, theme
switching, authentication interactions, and transaction modals.

**`requirements.txt`**

Lists the Python packages required by the application.

## Database Design

The application uses SQLite with two main tables.

### User

  Field           Description
  --------------- -----------------------
  id              Unique user ID
  username        Unique username
  email           Unique email
  password_hash   Hashed password
  theme_mode      User's selected theme

### Transaction

  Field            Description
  ---------------- ---------------------------------
  id               Unique transaction ID
  user_id          ID of transaction owner
  amount           Transaction amount
  category         Expense/income category
  type             Income or expense
  date             Transaction date
  description      Transaction description
  is_recurring     Whether the transaction repeats
  recurring_type   Recurrence type
  last_generated   Last generated recurring date

Each transaction is linked to a user through `user_id`.

## Installation

### 1. Clone or extract the project

Place the project in a convenient directory.

``` bash
cd PersonalFinanceAI
```

### 2. Create a virtual environment

Windows:

``` bash
python -m venv venv
```

Activate it:

``` bash
venv\Scripts\activate
```

macOS/Linux:

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

The main dependencies are:

``` text
Flask
Flask-SQLAlchemy
Pandas
NLTK
spaCy
Scikit-learn
Werkzeug
```

### 4. Start the application

From the project directory:

``` bash
python app.py
```

The application runs using Flask's development server.

Open the local address displayed in the terminal, normally:

``` text
http://127.0.0.1:5000/
```

## First-Time Usage

1.  Open the application.
2.  Select **Register**.
3.  Create a new account.
4.  Log in.
5.  Add income and expense transactions.
6.  Select different months to analyze historical data.
7.  Review the expense chart.
8.  Read the AI-generated financial suggestions.
9.  Use the forecast section after enough historical data has been
    collected.
10. Ask financial questions using the chatbot.
11. Use Profile Settings to change your password.
12. Switch between light and dark themes as required.

## Example Workflow

``` text
Register
   ↓
Login
   ↓
Dashboard
   ↓
Add Income / Expenses
   ↓
Monthly Analysis
   ↓
Category Breakdown
   ↓
AI Suggestions
   ↓
Machine Learning Forecast
   ↓
Chatbot Questions
```

## AI and Machine Learning Approach

The project uses two complementary approaches.

### Rule-Based Financial Analysis

The suggestion engine evaluates transaction data using predefined
financial rules.

Examples include:

``` text
Savings Rate =
(Income - Expenses) / Income × 100
```

and:

``` text
Expense Ratio =
Expenses / Income × 100
```

It also compares recent monthly expense totals.

### Linear Regression Forecasting

Historical monthly income and expense totals are converted into a
sequence of monthly observations.

A Linear Regression model is then trained separately for:

-   Income
-   Expenses

The models estimate the following month, after which:

``` text
Predicted Balance =
Predicted Income - Predicted Expenses
```

Because the model is based on historical transaction patterns,
predictions may be inaccurate when spending or income changes
unexpectedly.

## Security Considerations

The project includes several basic security measures:

-   Password hashing with Werkzeug
-   Login protection using Flask-Login
-   Authentication-required routes
-   User ownership checks for transaction modification
-   Unique usernames and email addresses
-   Password-strength validation

### Production security improvements

Before deploying publicly, consider:

-   Moving `SECRET_KEY` into an environment variable
-   Using a production WSGI server
-   Adding CSRF protection
-   Validating and sanitizing all financial input
-   Adding stronger session configuration
-   Using database migrations
-   Adding rate limiting to authentication endpoints
-   Disabling Flask debug mode
-   Adding HTTPS
-   Using PostgreSQL or another production database for larger
    deployments

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is activated and dependencies are
installed:

``` bash
pip install -r requirements.txt
```

### Database problems

The application uses SQLite and creates database tables with:

``` python
db.create_all()
```

when `app.py` is started.

If a development database becomes corrupted, back it up before replacing
or recreating it.

### Forecast is not displayed

The forecasting function requires at least two months of both income and
expense data.

Add sufficient historical transactions and reload the dashboard.

### No AI suggestions

The suggestion engine requires transaction data. Add income and/or
expense transactions and reload the dashboard.

## Current Project Notes

-   The project currently uses SQLite.
-   `ai_engine.py` exists in the project but the active AI-analysis and
    chatbot functions are implemented directly in `app.py`.
-   The current chatbot is rule/data-analysis based; it does not call an
    external large language model API.
-   `requirements.txt` includes NLTK and spaCy, although the current
    `app.py` implementation does not use them directly.
-   A virtual environment is included in the project archive, but it is
    generally better practice not to commit or distribute `venv/`;
    recreate it locally using the installation steps above.
-   The project archive contains database files. For public
    repositories, avoid committing personal or production financial
    data.

## Future Enhancements

Possible improvements include:

-   Monthly budget limits
-   Budget-versus-actual analysis
-   Savings goals
-   Recurring income support
-   More advanced forecasting models
-   Expense anomaly detection
-   Interactive financial reports
-   CSV/Excel import and export
-   PDF report generation
-   Email notifications
-   Mobile application
-   REST API using Flask/FastAPI
-   Natural-language AI assistant using an LLM
-   Improved database migrations
-   Automated unit and integration tests
-   Deployment using a production WSGI server

## Academic Project Information

**Project Title:** Personal Finance Tracker with AI Budgeting System

**Project Type:** Web-based Data Analytics / Machine Learning Project

**Core Areas:**

-   Web Development
-   Database Management
-   Data Analysis
-   Data Visualization
-   Artificial Intelligence / Rule-Based Analysis
-   Machine Learning
-   Financial Analytics

## License

This project can be adapted for academic and educational purposes. If
publishing it publicly, add a specific license such as MIT, Apache-2.0,
or another license appropriate to your intended use.

## Author

**Personal Finance AI Project**

Built using Python, Flask, SQLite, Pandas, Scikit-learn, HTML, CSS,
JavaScript, and Chart.js.
