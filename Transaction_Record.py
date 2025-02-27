import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class TransactionRecord:
    def __init__(self, root):
        self.root = root
        self.root.title("Income and Expense Management")
        self.entries = []

        # Type Selection
        tk.Label(root, text="Select Type:").grid(row=0, column=0, padx=10, pady=5)
        self.type_var = tk.StringVar(value="Income")
        self.type_combobox = ttk.Combobox(root, textvariable=self.type_var, values=["Income", "Expense"], state="readonly")
        self.type_combobox.grid(row=0, column=1, padx=10, pady=5)
        self.type_combobox.bind("<<ComboboxSelected>>", self.update_labels)

        # Particular
        tk.Label(root, text="Particular:").grid(row=1, column=0, padx=10, pady=5)
        self.particular_entry = tk.Entry(root)
        self.particular_entry.grid(row=1, column=1, padx=10, pady=5)
        self.particular_entry.bind('<Return>', lambda event: self.amount_entry.focus_set())  # Move to Amount

        # Amount Label
        self.amount_label = tk.Label(root, text="Amount:")
        self.amount_label.grid(row=2, column=0, padx=10, pady=5)

        # Amount
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5)
        self.amount_entry.bind('<Return>', lambda event: self.date_entry.focus_set())  # Move to Date

        # Date
        tk.Label(root, text="Date (DD/MM/YYYY):").grid(row=3, column=0, padx=10, pady=5)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=3, column=1, padx=10, pady=5)
        self.date_entry.bind('<Return>', lambda event: self.add_entry())  # Add entry

        # Delete Entry Button
        self.delete_button = tk.Button(root, text="Delete Entry", command=self.delete_entry)
        self.delete_button.grid(row=6, columnspan=3, pady=10)

        # Save as PDF Button
        self.save_pdf_button = tk.Button(root, text="Save as PDF", command=self.save_as_pdf)
        self.save_pdf_button.grid(row=7, columnspan=3, pady=10)

        # Treeview
        self.tree = ttk.Treeview(root, columns=("Date", "Particular", "Income", "Expenditure", "Balance"), show='headings')
        self.tree.heading("Date", text="Date")
        self.tree.heading("Particular", text="Particular")
        self.tree.heading("Income", text="Income")
        self.tree.heading("Expenditure", text="Expenditure")
        self.tree.heading("Balance", text="Balance")

        # Center the text in the columns
        for col in self.tree["columns"]:
            self.tree.column(col, anchor="center")  # Center the text in each column

        self.tree.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        self.update_labels()  # Initialize labels based on default selection

    def update_labels(self, event=None):
        """Update the labels based on the selected type."""
        if self.type_var.get() == "Income":
            self.amount_label.config(text="Amount:")
        else:
            self.amount_label.config(text="Amount:")

    def add_entry(self):
        """Add an entry to the list and update the Treeview."""
        particular = self.particular_entry.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get()
        entry_type = self.type_var.get()

        if particular and amount and date:
            try:
                amount_value = float(amount)
                # Validate date format
                date_obj = datetime.strptime(date, "%d/%m/%Y")  # Parse date for sorting
                current_date = datetime.now()
                if date_obj > current_date:
                    messagebox.showwarning("Input Error", "Please enter valid data.")
                    return
            except ValueError:
                messagebox.showwarning("Input Error", "Ensure the date is in DD/MM/YYYY format and valid.")
                return

            # Add entry to the list
            self.entries.append({'date': date_obj, 'particular': particular, 'amount': amount_value, 'type': entry_type})
            self.particular_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.update_treeview()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    def delete_entry(self):
        """Delete the selected entry from the Treeview and the list."""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, 'values')
            # Determine the entry type based on the selected item
            if item_values[2]:  # If there's a value in the Income column
                entry_type = "Income"
                amount_value = float(item_values[2])
            else:  # Otherwise, it must be an Expense
                entry_type = "Expense"
                amount_value = float(item_values[3])

            # Remove the entry from the internal list
            self.entries = [entry for entry in self.entries if not (
                entry['date'] == datetime.strptime(item_values[0], "%d/%m/%Y") and
                entry['particular'] == item_values[1] and
                entry['amount'] == amount_value and
                entry['type'] == entry_type)]
            
            self.update_treeview()
        else:
            messagebox.showwarning("Selection Error", "Please select an entry to delete.")

    def update_treeview(self):
        """Update the Treeview with current entries."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort entries by date
        sorted_entries = sorted(self.entries, key=lambda x: x['date'])

        balance = 0  # Initialize balance
        for entry in sorted_entries:
            income_value = entry['amount'] if entry['type'] == "Income" else ""
            expenditure_value = entry['amount'] if entry['type'] == "Expense" else ""
            if entry['type'] == "Income":
                balance += entry['amount']
            else:
                balance -= entry['amount']
            # Format date back to string for display
            date_str = entry['date'].strftime("%d/%m/%Y")
            self.tree.insert("", tk.END, values=(date_str, entry['particular'], income_value, expenditure_value, balance))

    def save_as_pdf(self):
        """Save the current entries as a PDF."""
        if not self.entries:
            messagebox.showwarning("No Entries", "There are no entries to save.")
            return

        filename = "transaction_record_report.pdf"
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
        balance = 0  # Initialize balance
        for entry in sorted(self.entries, key=lambda x: x['date']):
            income_value = entry['amount'] if entry['type'] == "Income" else ""
            expenditure_value = entry['amount'] if entry['type'] == "Expense" else ""
            if entry['type'] == "Income":
                balance += entry['amount']
            else:
                balance -= entry['amount']
            # Format date back to string for display
            date_str = entry['date'].strftime("%d/%m/%Y")
            c.drawString(50, y_offset, date_str)
            c.drawString(150, y_offset, entry['particular'])
            c.drawString(250, y_offset, str(income_value))
            c.drawString(350, y_offset, str(expenditure_value))
            c.drawString(450, y_offset, str(balance))
            y_offset -= 20  # Move down for the next row

        c.save()
        messagebox.showinfo("Success", f"PDF saved as {filename}")

    def log_interest_calculation(self, deposit_date, maturity_date, amount, interest_rate, time_of_maturity, maturity_amount, deposit_type):
        """Log the interest calculation as a transaction."""
        self.entries.append({
            'date': maturity_date,
            'particular': f"Interest from {deposit_type} FD",
            'amount': maturity_amount,
            'type': 'Income'  # Assuming interest is considered income
        })
        self.update_treeview()  # Update the display

def run_app():
    """Function to run the application."""
    root = tk.Tk()
    app = TransactionRecord(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()