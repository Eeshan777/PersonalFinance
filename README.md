# 💼 Personal Finance Manager

A powerful desktop personal finance application built with [Flet](https://flet.dev) and Python. Securely manage your income, expenses, interest calculations, and budget reports with exportable PDF summaries — all from a clean, intuitive interface.

---

## ✨ Features

- 🔐 Secure Login/Signup with SHA-256 password hashing  
- 💵 Add and track Income & Expense records  
- 📆 Calendar-based entry for all modules  
- 📈 Fixed Deposit Interest Calculator (Cumulative & Non-Cumulative)  
- 📊 Monthly and Yearly Budget Report Generator  
- 📄 PDF Export of Transactions and Interest Records  
- 💾 SQLite database stored in `%LOCALAPPDATA%/PersonalFinance`  
- 🧠 Session-based auto-login for user convenience  
- 📱 Full-screen, responsive layout on launch  

---

## 🛠️ Tech Stack

| Layer       | Technology |
|-------------|------------|
| UI          | Flet       |
| Backend     | Python     |
| Database    | SQLite     |
| PDF Engine  | ReportLab  |

---

## 🚀 Getting Started

To start using the Personal Finance Manager, simply install the required dependencies by running `pip install flet reportlab` in your terminal, and then launch the application using `python Main.py`. On first launch, you can sign up for a new account, and all your credentials and financial data will be securely stored in your system's local AppData folder. The app opens in full-screen mode and provides a seamless interface to manage your transactions, interest calculations, budget reports, and PDF exports — all without needing any external setup.

---

## 📁 .gitignore

```
__pycache__/
```

---

## 📦 File Structure

```
├── Main.py                 # App entry point with login/signup and routing
├── TransactionRecord.py    # Module for tracking income and expenses
├── InterestCalculator.py   # Module to compute interest on deposits
├── BudgetReport.py         # Budget summary based on transaction data
├── DownloadPDF.py          # Export reports as PDF files
├── PFIcon.ico              # App icon (Windows)
├── PersonalFinance.exe     # Compiled app (if using PyInstaller)
└── .gitignore              # Ignored cache files
```

---

> 💡 *Best suited for Windows systems. All data is stored locally and securely. Make sure you do not delete your AppData folder to retain previous records.*

---