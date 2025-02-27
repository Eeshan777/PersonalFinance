import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

def save_interest_calculator_pdf(entries, filename="interest_calculator_report.pdf"):
    """Generate a PDF report for the Interest Calculator entries."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Interest Calculator Report")
    c.setFont("Helvetica", 12)

    # Table headers
    headers = ["Deposit Date", "Maturity Date", "Amount Deposited", "Interest Rate", "Time of Maturity", "Maturity Amount", "Deposit Type"]
    x_offset = 50
    y_offset = height - 100

    for header in headers:
        c.drawString(x_offset, y_offset, header)
        x_offset += 100  # Adjust spacing as needed

    y_offset -= 20  # Move down for the data rows

    # Data rows
    for entry in entries:
        c.drawString(50, y_offset, entry['deposit_date'].strftime("%d/%m/%Y"))
        c.drawString(150, y_offset, entry['maturity_date'].strftime("%d/%m/%Y"))
        c.drawString(250, y_offset, str(entry['amount']))
        c.drawString(350, y_offset, str(entry['interest_rate']))
        c.drawString(450, y_offset, str(entry['time_of_maturity']))
        c.drawString(550, y_offset, str(entry['maturity_amount']))
        c.drawString(650, y_offset, entry['deposit_type'])  # New column for deposit type
        y_offset -= 20  # Move down for the next row

    c.save()
    return filename

def save_transaction_record_pdf(entries, filename="transaction_record_report.pdf"):
    """Generate a PDF report for the Transaction Record entries."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Transaction Record Report")
    c.setFont("Helvetica", 12)

    # Table headers
    headers = ["Date", "Particular", "Income", "Expenditure", "Balance"]
    x_offset = 50
    y_offset = height - 100

    for header in headers:
        c.drawString(x_offset, y_offset, header)
        x_offset += 100  # Adjust spacing as needed

    y_offset -= 20  # Move down for the data rows

    # Data rows
    balance = 0
    for entry in sorted(entries, key=lambda x: x['date']):
        income_value = entry['amount'] if entry['type'] == "Income" else ""
        expenditure_value = entry['amount'] if entry['type'] == "Expense" else ""
        if entry['type'] == "Income":
            balance += entry['amount']
        else:
            balance -= entry['amount']
        
        c.drawString(50, y_offset, entry['date'].strftime("%d/%m/%Y"))
        c.drawString(150, y_offset, entry['particular'])
        c.drawString(250, y_offset, str(income_value))
        c.drawString(350, y_offset, str(expenditure_value))
        c.drawString(450, y_offset, str(balance))
        y_offset -= 20  # Move down for the next row

    c.save()
    return filename

def main():
    # Example usage
    interest_entries = [
        {'deposit_date': datetime(2023, 1, 1), 'maturity_date': datetime(2024, 1, 1), 'amount': 1000, 'interest_rate': 5, 'time_of_maturity': 1, 'maturity_amount': 1050, 'deposit_type': 'Cumulative'},
        # Add more entries as needed
    ]

    transaction_entries = [
        {'date': datetime(2023, 1, 1), 'particular': 'Salary', 'amount': 2000, 'type': 'Income'},
        {'date': datetime(2023, 1, 5), 'particular': 'Groceries', 'amount': 150, 'type': 'Expense'},
        # Add more entries as needed
    ]

    save_interest_calculator_pdf(interest_entries)
    save_transaction_record_pdf(transaction_entries)

if __name__ == "__main__":
    main()