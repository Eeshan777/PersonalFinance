import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from Save_PDF import save_budget_report_pdf

class BudgetReport:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Report Generator")

        # User input for month/year and report type
        tk.Label(root, text="Month/Year (MM/YYYY):").grid(row=0, column=0, padx=10, pady=5)
        self.month_year_entry = tk.Entry(root)
        self.month_year_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="Year (YYYY):").grid(row=1, column=0, padx=10, pady=5)
        self.year_entry = tk.Entry(root)
        self.year_entry.grid(row=1, column=1, padx=10, pady=5)

        self.report_type_var = tk.StringVar(value="Monthly")
        tk.Label(root, text="Report Type:").grid(row=2, column=0, padx=10, pady=5)
        report_type_combobox = ttk.Combobox(root, textvariable=self.report_type_var, values=["Monthly", "Yearly"], state="readonly")
        report_type_combobox.grid(row=2, column=1, padx=10, pady=5)

        generate_button = tk.Button(root, text="Generate Report", command=self.generate_report)
        generate_button.grid(row=3, columnspan=2, pady=10)

        save_pdf_button = tk.Button(root, text="Save as PDF", command=self.save_as_pdf)
        save_pdf_button.grid(row=4, columnspan=2, pady=10)

        # Text widget for displaying the report
        self.report_display = tk.Text(root, height=10, width=50)
        self.report_display.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        self.report_display.config(state=tk.DISABLED)  # Make it read-only initially

        self.report_data = None

    def fetch_data(self, month_year=None, year=None):
        """Fetch transactions and interest data from the database."""
        conn = sqlite3.connect("finance_data.db")
        cursor = conn.cursor()

        transactions = []
        if month_year:
            cursor.execute("SELECT * FROM transactions WHERE month_year=?", (month_year,))
            transactions = cursor.fetchall()
        elif year:
            cursor.execute("SELECT * FROM transactions WHERE month_year LIKE ?", ('%' + year,)) 
            transactions = cursor.fetchall()

        interest_data = []
        if year:
            cursor.execute("SELECT * FROM interest_calculations WHERE month_year LIKE ?", ('%' + year,))
            interest_data = cursor.fetchall()

        conn.close()
        return transactions, interest_data

    def calculate_budget(self, transactions, interest_data):
        """Calculate the budget based on transactions and interest data."""
        total_income = sum(t[5] for t in transactions if t[2] == "Income")
        total_expenses = sum(t[5] for t in transactions if t[2] == "Expense")
        total_interest = sum(i[8] for i in interest_data)  # Assuming maturity amount is at index 8

        budget = total_income - total_expenses + total_interest
        return total_income, total_expenses, budget

    def generate_report(self):
        """Generate the budget report."""
        month_year = self.month_year_entry.get()
        year = self.year_entry.get()
        report_type = self.report_type_var.get()

        transactions, interest_data = self.fetch_data(month_year, year)

        if not transactions and not interest_data:
            messagebox.showwarning("No Data", "No transactions or interest data found for the specified period.")
            return

        total_income, total_expenses, budget = self.calculate_budget(transactions, interest_data)
        self.report_data = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "budget": budget,
            "report_type": report_type
        }

        self.show_report()

    def show_report(self):
        """Display the report data in the text widget."""
        report_text = f"Total Income: {self.report_data['total_income']}\n"
        report_text += f"Total Expenses: {self.report_data['total_expenses']}\n"
        report_text += f"Calculated Budget: {self.report_data['budget']}\n"
        report_text += f"Report Type: {self.report_data['report_type']}\n"

        # Enable the text widget and insert the report text
        self.report_display.config(state=tk.NORMAL)
        self.report_display.delete(1.0, tk.END)  # Clear previous text
        self.report_display.insert(tk.END, report_text)
        self.report_display.config(state=tk.DISABLED)  # Make it read-only again

        # Create a pie chart for income vs expenses
        self.create_pie_chart()

    def create_pie_chart(self):
        """Create a pie chart for income vs expenses."""
        labels = ['Income', 'Expenses']
        sizes = [self.report_data['total_income'], self.report_data['total_expenses']]
        colors = ['#4CAF50', '#FF5733']
        explode = (0.1, 0)  # explode the 1st slice (Income)

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title("Income vs Expenses")
        plt.show()

    def save_as_pdf(self):
        """Save the budget report as a PDF."""
        if not self.report_data:
            messagebox.showwarning("No Report", "Please generate a report before saving.")
            return

        budget_pdf_filename = "budget_report.pdf"
        save_budget_report_pdf(self.report_data, budget_pdf_filename)

        # Reset the input fields after saving
        self.month_year_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.report_type_var.set("Monthly")  # Reset to default report type

        # Clear the report data
        self.report_data = None

        # Provide feedback to the user
        print("Report data has been cleared. Ready for new input.")
        self.month_year_entry.focus_set()  # Set focus back to the month/year entry field

def run_budget_report_app():
    """Function to run the budget report application."""
    root = tk.Tk()
    app = BudgetReport(root)
    root.mainloop()

if __name__ == "__main__":
    run_budget_report_app()