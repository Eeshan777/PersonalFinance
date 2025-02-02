import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class PersonalFinance:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance")

        # Welcome message
        welcome_label = tk.Label(root, text="Welcome, User!", font=("Helvetica", 24))
        welcome_label.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        # Button to launch Interest Calculator
        interest_calculator_button = tk.Button(root, text="Interest Calculator", command=self.launch_interest_calculator, width=30)
        interest_calculator_button.grid(row=1, column=0, padx=10, pady=10)

        # Button to launch Transaction Record
        transaction_record_button = tk.Button(root, text="Transaction Record", command=self.launch_transaction_record, width=30)
        transaction_record_button.grid(row=1, column=1, padx=10, pady=10)

    def launch_interest_calculator(self):
        interest_calculator_path = os.path.join(os.path.dirname(__file__), "Interest Calculator.py")  # Ensure the filename matches
        try:
            subprocess.run(["python", interest_calculator_path], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to launch Interest Calculator: {e}")

    def launch_transaction_record(self):
        transaction_record_path = os.path.join(os.path.dirname(__file__), "Transaction Record.py")  # Ensure the filename matches
        try:
            subprocess.run(["python", transaction_record_path], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to launch Transaction Record: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonalFinance(root)
    root.mainloop()