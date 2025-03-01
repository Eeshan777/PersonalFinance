import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from datetime import datetime

def save_interest_calculator_pdf(entries, filename):
    """Generate a PDF report for the Interest Calculator entries."""
    pdf = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Table headers
    headers = ["Deposit Date", "Maturity Date", "Deposit Type", "Amount Deposited", "Interest Rate", "Time of Maturity", "Maturity Amount"]
    data = [headers]  # Start with headers

    # Populate data rows
    for entry in entries:
        row = [
            entry['deposit_date'].strftime("%d/%m/%Y"),
            entry['maturity_date'].strftime("%d/%m/%Y"),
            entry['deposit_type'],
            str(entry['amount']),
            str(entry['interest_rate']),
            str(entry['time_of_maturity']),
            str(entry['maturity_amount'])
        ]
        data.append(row)

    # Create a Table
    table = Table(data)

    # Define the style for the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # Header font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Body background
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Body text color
        ('FONTSIZE', (0, 1), (-1, -1), 9),  # Body font size
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
    ])
    
    # Apply the style to the table
    table.setStyle(style)

    # Check if the table fits on one page
    max_rows_per_page = 20  # Adjust this number based on your layout
    for i in range(0, len(data), max_rows_per_page):
        chunk = data[i:i + max_rows_per_page]
        table_chunk = Table(chunk)
        table_chunk.setStyle(style)
        elements.append(table_chunk)
        elements.append(Spacer(1, 12))  # Add space between tables

    # Build the PDF
    pdf.build(elements)
    return filename

def save_transaction_record_pdf(entries, filename):
    """Generate a PDF report for the Transaction Record entries."""
    pdf = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Table headers
    headers = ["Date", "Particular", "Income", "Expenditure", "Balance"]
    data = [headers]  # Start with headers

    # Calculate balance and populate data rows
    balance = 0
    for entry in sorted(entries, key=lambda x: x['date']):
        income_value = entry['amount'] if entry['type'] == "Income" else ""
        expenditure_value = entry['amount'] if entry['type'] == "Expense" else ""
        if entry['type'] == "Income":
            balance += entry['amount']
        else:
            balance -= entry['amount']
        
        row = [
            entry['date'].strftime("%d/%m/%Y"),
            entry['particular'],
            str(income_value),
            str(expenditure_value),
            str(balance)
        ]
        data.append(row)

    # Create a Table
    table = Table(data)

    # Define the style for the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('FONTSIZE', (0, 0), (-1, 0), 12),  # Header font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Body background
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Body text color
        ('FONTSIZE', (0, 1), (-1, -1), 10),  # Body font size
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
    ])
    
    # Apply the style to the table
    table.setStyle(style)

    # Add the table to the elements list
    elements.append(table)

    # Build the PDF
    pdf.build(elements)
    return filename

def main():
    interest_entries = [
        {'deposit_date': datetime(2023, 1, 1), 'maturity_date': datetime(2024, 1, 1), 'amount': 1000, 'interest_rate': 5, 'time_of_maturity': 1, 'maturity_amount': 1050, 'deposit_type': 'Cumulative'},
        # Add more entries as needed for testing
    ]

    transaction_entries = [
        {'date': datetime(2023, 1, 1), 'particular': 'Salary', 'amount': 2000, 'type': 'Income'},
        {'date': datetime(2023, 1, 5), 'particular': 'Groceries', 'amount': 150, 'type': 'Expense'},
    ]

    # Save the interest calculator PDF
    interest_pdf_filename = "interest_calculator_report.pdf"
    save_interest_calculator_pdf(interest_entries, interest_pdf_filename)

    # Save the transaction record PDF
    transaction_pdf_filename = "transaction_record_report.pdf"
    save_transaction_record_pdf(transaction_entries, transaction_pdf_filename)

if __name__ == "__main__":
    main()