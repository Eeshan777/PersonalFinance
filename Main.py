import os
import tkinter as tk
from tkinter import messagebox
import subprocess
from BudgetReport import BudgetReport  # Ensure this matches the class name in Budget_Report.py

class PersonalFinance:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Personal Finance")
        self.username = username

        self.show_welcome_message()

    def show_welcome_message(self):
        welcome_label = tk.Label(self.root, text=f"Welcome, {self.username}!", font=("Helvetica", 24))
        welcome_label.grid(row=0, column=0, columnspan=3, padx=10, pady=20)

        # Button to launch Interest Calculator
        interest_calculator_button = tk.Button(self.root, text="Interest Calculator", command=self.launch_interest_calculator, width=30)
        interest_calculator_button.grid(row=1, column=0, padx=10, pady=10)

        # Button to launch Transaction Record
        transaction_record_button = tk.Button(self.root, text="Transaction Record", command=self.launch_transaction_record, width=30)
        transaction_record_button.grid(row=1, column=1, padx=10, pady=10)

        # Button to launch Budget Report
        budget_report_button = tk.Button(self.root, text="Generate Budget Report", command=self.launch_budget_report, width=30)
        budget_report_button.grid(row=1, column=2, padx=10, pady=10)

    def launch_interest_calculator(self):
        interest_calculator_path = os.path.join(os.path.dirname(__file__), "Interest_Calculator.py")
        try:
            subprocess.run(["python", interest_calculator_path], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to launch Interest Calculator: {e}")

    def launch_transaction_record(self):
        transaction_record_path = os.path.join(os.path.dirname(__file__), "Transaction_Record.py")
        try:
            subprocess.run(["python", transaction_record_path], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to launch Transaction Record: {e}")

    def launch_budget_report(self):
        budget_report_window = tk.Toplevel(self.root)
        BudgetReport(budget_report_window)  # Create an instance of BudgetReport

def run(username):
    root = tk.Tk()
    app = PersonalFinance(root, username)
    root.mainloop()

if __name__ == "__main__":
    pass