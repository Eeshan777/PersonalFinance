import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image
from datetime import datetime
import matplotlib.pyplot as plt
from tkinter import messagebox

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

def save_budget_report_pdf(report_data, filename):
    """Generate a PDF report for the Budget Report."""
    pdf = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Create a pie chart for income vs expenses
    labels = ['Income', 'Expenses']
    sizes = [report_data['total_income'], report_data['total_expenses']]
    colors = ['#4CAF50', '#FF5733']
    explode = (0.1, 0)  # explode the 1st slice (Income)

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Income vs Expenses")
    plt.savefig("Income_vs_Expenses.png")  # Save the pie chart as a PNG file
    plt.close()  # Close the plot to free memory

    # Table headers for the budget report
    headers = ["Total Income", "Total Expenses", "Calculated Budget"]
    data = [[report_data['total_income'], report_data['total_expenses'], report_data['budget']]]

    # Create a Table for the budget report
    budget_table = Table([headers] + data)

    # Define the style for the budget table
    budget_style = TableStyle([
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

    # Apply the style to the budget table
    budget_table.setStyle(budget_style)

    # Add the budget table to the elements list
    elements.append(budget_table)
    elements.append(Spacer(1, 12))  # Add space between tables

    # Add the pie chart image to the PDF
    elements.append(Image("Income_vs_Expenses.png"))

    # Build the PDF
    pdf.build(elements)

    # Show success message
    messagebox.showinfo("Success", f"Budget report saved as {filename}")

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

    # Example budget report data
    budget_report_data = {
        "total_income": 5000,
        "total_expenses": 3000,
        "budget": 2000,
        "report_type": "Monthly"
    }
    budget_pdf_filename = "budget_report.pdf"
    save_budget_report_pdf(budget_report_data, budget_pdf_filename)

if __name__ == "__main__":
    main()