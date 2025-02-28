import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar

class InterestCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Interest Calculator")

        # Create and place labels and entries
        tk.Label(root, text="Date of Deposit (DD/MM/YYYY):").grid(row=0, column=0, padx=10, pady=10)
        self.date_entry = DateEntry(root, date_pattern='dd/mm/yyyy')  # Use DateEntry for calendar
        self.date_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(root, text="Amount Deposited:").grid(row=1, column=0, padx=10, pady=10)
        self.deposit_entry = tk.Entry(root)
        self.deposit_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(root, text="Annual Interest Rate (%):").grid(row=2, column=0, padx=10, pady=10)
        self.rate_entry = tk.Entry(root)
        self.rate_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(root, text="Time of Maturity:").grid(row=3, column=0, padx=10, pady=10)
        self.time_combobox = ttk.Combobox(root, values=["1 year", "2 years", "3 years", "5 years", "10 years"], state="readonly")
        self.time_combobox.grid(row=3, column=1, padx=10, pady=10)
        self.time_combobox.set("Select Time Period")

        tk.Label(root, text="Deposit Type:").grid(row=4, column=0, padx=10, pady=10)
        self.deposit_type_combobox = ttk.Combobox(root, values=["Cumulative", "Non-Cumulative"], state="readonly")
        self.deposit_type_combobox.grid(row=4, column=1, padx=10, pady=10)
        self.deposit_type_combobox.set("Select Deposit Type")

        # Bind the Enter key to calculate and move focus
        self.date_entry.bind("<Return>", lambda event: self.deposit_entry.focus_set())
        self.deposit_entry.bind("<Return>", lambda event: self.rate_entry.focus_set())
        self.rate_entry.bind("<Return>", lambda event: self.time_combobox.focus_set())
        self.time_combobox.bind("<Return>", lambda event: self.deposit_type_combobox.focus_set())
        self.deposit_type_combobox.bind("<Return>", lambda event: self.calculate())

        # Create and place the result table
        self.columns = ("Deposit Date", "Maturity Date", "Amount Deposited", "Interest Rate", "Time of Maturity", "Maturity Amount", "Deposit Type")
        self.result_table = ttk.Treeview(root, columns=self.columns, show='headings')
        self.result_table.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Define headings and center the text in the columns
        for col in self.columns:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, anchor="center")  # Center the text in each column

        # Create and place the delete button
        delete_button = tk.Button(root, text="Delete Entry", command=self.delete_entry)
        delete_button.grid(row=7, columnspan=3, pady=10)

        # Create and place the save as PDF button
        save_pdf_button = tk.Button(root, text="Save as PDF", command=self.save_as_pdf)
        save_pdf_button.grid(row=8, columnspan=3, pady=10)

        # Set focus to the first entry field
        self.date_entry.focus()

        # Store entries for sorting
        self.entries = []

    def calculate_maturity_amount(self, principal, rate, time, is_cumulative):
        # Calculate the maturity amount using the compound interest formula
        if is_cumulative:
            n = 1  # Compounding frequency (annually)
            maturity_amount = principal * (1 + rate / (100 * n)) ** (n * time)
        else:
            maturity_amount = principal + (principal * rate * time / 100)  # Simple interest for non-cumulative
        return maturity_amount

    def validate_date(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")  # Parse date for sorting
            current_date = datetime.now()
            if date_obj > current_date:
                messagebox.showwarning("Input Error", "Please enter a valid date.")
                return None
            return date_obj
        except ValueError:
            messagebox.showwarning("Input Error", "Ensure the date is in DD/MM/YYYY format and valid.")
            return None

    def validate_amount(self, amount_str):
        try:
            return float(amount_str)
        except ValueError:
            return None

    def validate_rate(self, rate_str):
        try:
            rate = float(rate_str)
            return rate  # Return the rate directly
        except ValueError:
            return None

    def calculate(self):
        # Validate each input individually
        deposit_date = self.date_entry.get()
        money_deposited = self.deposit_entry.get()
        interest_rate = self.rate_entry.get()
        time_of_maturity = self.time_combobox.get()
        deposit_type = self.deposit_type_combobox.get()

        # Validate inputs
        if not deposit_date or not money_deposited or not interest_rate or time_of_maturity == "Select Time Period" or deposit_type == "Select Deposit Type":
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        deposit_date_obj = self.validate_date(deposit_date)
        if deposit_date_obj is None:
            return

        money_deposited_value = self.validate_amount(money_deposited)
        if money_deposited_value is None:
            messagebox.showwarning("Input Error", "Please enter a valid amount deposited.")
            return

        interest_rate_value = self.validate_rate(interest_rate)
        if interest_rate_value is None:
            messagebox.showwarning("Input Error", "Please enter a valid non-negative interest rate.")
            return

        # Convert time of maturity to numeric value
        time_of_maturity_value = float(time_of_maturity.split()[0])  # Get the numeric part from the dropdown

        # Calculate maturity date
        maturity_date_obj = deposit_date_obj.replace(year=deposit_date_obj.year + int(time_of_maturity_value))

        # Store the entry for sorting later
        is_cumulative = deposit_type == "Cumulative"
        maturity_amount = self.calculate_maturity_amount(money_deposited_value, interest_rate_value, time_of_maturity_value, is_cumulative)

        self.entries.append({
            'deposit_date': deposit_date_obj,
            'maturity_date': maturity_date_obj,
            'amount': money_deposited_value,
            'interest_rate': interest_rate_value,
            'time_of_maturity': time_of_maturity_value,
            'maturity_amount': maturity_amount,
            'deposit_type': deposit_type  # Store deposit type
        })

        # Sort entries by maturity date
        self.entries.sort(key=lambda x: x['maturity_date'])

        # Clear the result table
        for item in self.result_table.get_children():
            self.result_table.delete(item)

        # Add sorted entries to the result table
        for entry in self.entries:
            self.result_table.insert("", "end", values=(
                entry['deposit_date'].strftime("%d/%m/%Y"),
                entry['maturity_date'].strftime("%d/%m/%Y"),
                entry['amount'],
                entry['interest_rate'],
                entry['time_of_maturity'],
                entry['maturity_amount'],
                entry['deposit_type']  # New column for deposit type
            ))

        # Clear the input fields
        self.clear_inputs()

    def clear_inputs(self):
        self.date_entry.set_date(datetime.now())  # Reset to today's date
        self.deposit_entry.delete(0, tk.END)
        self.rate_entry.delete(0, tk.END)
        self.time_combobox.set("Select Time Period")
        self.deposit_type_combobox.set("Select Deposit Type")

    def delete_entry(self):
        selected_item = self.result_table.selection()
        if selected_item:
            # Remove the selected entry from the internal list
            index = self.result_table.index(selected_item)
            del self.entries[index]
            self.result_table.delete(selected_item)
        else:
            messagebox.showwarning("Selection Error", "Please select an entry to delete.")

    def save_as_pdf(self):
        """Save the current entries as a PDF."""
        if not self.entries:
            messagebox.showwarning("No Entries", "There are no entries to save.")
            return

        filename = "interest_calculator_report.pdf"
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
        for entry in self.entries:
            c.drawString(50, y_offset, entry['deposit_date'].strftime("%d/%m/%Y"))
            c.drawString(150, y_offset, entry['maturity_date'].strftime("%d/%m/%Y"))
            c.drawString(250, y_offset, str(entry['amount']))
            c.drawString(350, y_offset, str(entry['interest_rate']))
            c.drawString(450, y_offset, str(entry['time_of_maturity']))
            c.drawString(550, y_offset, str(entry['maturity_amount']))
            c.drawString(650, y_offset, entry['deposit_type'])  # New column for deposit type
            y_offset -= 20  # Move down for the next row

        c.save()
        messagebox.showinfo("Success", f"PDF saved as {filename}")

def run_app():
    """Function to run the application."""
    root = tk.Tk()
    app = InterestCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()