import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from SavePDF import save_budget_report_pdf

class BudgetReport(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Budget Report Generator")
        self.setStyleSheet("background-color: #F5F5F5;")
        self.report_data = None
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.month_year_entry = QtWidgets.QLineEdit(self)
        self.month_year_entry.setPlaceholderText("Month/Year (MM/YYYY)")
        layout.addWidget(self.month_year_entry)

        self.report_type_var = QtWidgets.QComboBox(self)
        self.report_type_var.addItems(["Monthly", "Yearly"])
        layout.addWidget(self.report_type_var)

        generate_button = QtWidgets.QPushButton("Generate Report", self)
        generate_button.clicked.connect(self.generate_report)
        layout.addWidget(generate_button)

        save_pdf_button = QtWidgets.QPushButton("Save as PDF", self)
        save_pdf_button.clicked.connect(self.save_as_pdf)
        layout.addWidget(save_pdf_button)

        self.report_display = QtWidgets.QTextEdit(self)
        self.report_display.setReadOnly(True)
        layout.addWidget(self.report_display)

        self.setLayout(layout)

    def fetch_data(self, month_year=None):
        try:
            conn = sqlite3.connect("finance_data.db")
            cursor = conn.cursor()
            transactions = []
            if month_year:
                cursor.execute("SELECT * FROM transactions WHERE strftime('%m/%Y', date) = ?", (month_year,))
                transactions = cursor.fetchall()

            interest_data = []
            if month_year:
                cursor.execute("SELECT * FROM interest_calculations WHERE deposit_date LIKE ?", ('%' + month_year.split('/')[1],))
                interest_data = cursor.fetchall()

            conn.close()
            return transactions, interest_data
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Failed to connect: {str(e)}")
            return [], []

    def calculate_budget(self, transactions, interest_data):
        total_income = sum(t[3] for t in transactions if t[4] == "Income")
        total_expenses = sum(t[3] for t in transactions if t[4] == "Expense")
        total_interest = sum(i[6] for i in interest_data)

        budget = total_income - total_expenses + total_interest
        return total_income, total_expenses, budget

    def generate_report(self):
        month_year = self.month_year_entry.text()
        report_type = self.report_type_var.currentText()

        transactions, interest_data = self.fetch_data(month_year)

        if not transactions and not interest_data:
            QtWidgets.QMessageBox.warning(self, "No Data", "No transactions or interest data found for the specified period.")
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
        if not self.report_data:
            QtWidgets.QMessageBox.warning(self, "No Report", "Generate a report first.")
            return

        report_text = f"Total Income: {self.report_data['total_income']}\n"
        report_text += f"Total Expenses: {self.report_data['total_expenses']}\n"
        report_text += f"Calculated Budget: {self.report_data['budget']}\n"
        report_text += f"Report Type: {self.report_data['report_type']}\n"

        self.report_display.setPlainText(report_text)
        self.create_pie_chart()

    def create_pie_chart(self):
        labels = ['Income', 'Expenses']
        sizes = [self.report_data['total_income'], self.report_data['total_expenses']]

        # Check for zero values to avoid division by zero
        if self.report_data['total_income'] == 0 and self.report_data['total_expenses'] == 0:
            QtWidgets.QMessageBox.warning(self, "No Data", "Both income and expenses are zero.")
            return

        # Handle cases where one of the values is zero
        if self.report_data['total_income'] == 0:
            sizes = [1, self.report_data['total_expenses']]  # Avoid division by zero
        elif self.report_data['total_expenses'] == 0:
            sizes = [self.report_data['total_income'], 1]  # Avoid division by zero

        colors = ['#4CAF50', '#FF5733']
        explode = (0.1, 0)

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title("Income vs Expenses")
        plt.show()

    def save_as_pdf(self):
        if not self.report_data:
            QtWidgets.QMessageBox.warning(self, "No Report", "Please generate a report before saving.")
            return

        budget_pdf_filename = "budget_report.pdf"
        save_budget_report_pdf(self.report_data, budget_pdf_filename)

        self.month_year_entry.clear()
        self.report_type_var.setCurrentIndex(0)
        self.report_data = None

def run_app():
    app = QtWidgets.QApplication(sys.argv)
    window = BudgetReport(None)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()