import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class InterestCalculator(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Interest Calculator")
        self.setStyleSheet("background-color: #F5F5F5;")
        self.create_database()
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.date_entry = QtWidgets.QDateEdit(self)
        self.date_entry.setDisplayFormat("dd/MM/yyyy")
        self.date_entry.setCalendarPopup(True)
        layout.addWidget(self.date_entry)

        self.deposit_entry = QtWidgets.QLineEdit(self)
        self.deposit_entry.setPlaceholderText("Amount Deposited")
        layout.addWidget(self.deposit_entry)

        self.rate_entry = QtWidgets.QLineEdit(self)
        self.rate_entry.setPlaceholderText("Annual Interest Rate (%)")
        layout.addWidget(self.rate_entry)

        self.time_combobox = QtWidgets.QComboBox(self)
        self.time_combobox.addItems(["1 year", "2 years", "3 years", "5 years", "10 years"])
        layout.addWidget(self.time_combobox)

        self.deposit_type_combobox = QtWidgets.QComboBox(self)
        self.deposit_type_combobox.addItems(["Cumulative", "Non-Cumulative"])
        layout.addWidget(self.deposit_type_combobox)

        calculate_button = QtWidgets.QPushButton("Calculate", self)
        calculate_button.clicked.connect(self.calculate)
        layout.addWidget(calculate_button)

        self.result_table = QtWidgets.QTableWidget(self)
        self.result_table.setColumnCount(7)
        self.result_table.setHorizontalHeaderLabels(["Deposit Date", "Maturity Date", "Amount Deposited", "Interest Rate", "Time of Maturity", "Maturity Amount", "Deposit Type"])
        layout.addWidget(self.result_table)

        delete_button = QtWidgets.QPushButton("Delete Entry", self)
        delete_button.clicked.connect(self.delete_entry)
        layout.addWidget(delete_button)

        save_pdf_button = QtWidgets.QPushButton("Save as PDF", self)
        save_pdf_button.clicked.connect(self.save_as_pdf)
        layout.addWidget(save_pdf_button)

        self.setLayout(layout)

    def create_database(self):
        conn = sqlite3.connect("finance_data.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interest_calculations (
                id INTEGER PRIMARY KEY,
                deposit_date TEXT,
                maturity_date TEXT,
                amount REAL,
                interest_rate REAL,
                time_of_maturity REAL,
                maturity_amount REAL,
                deposit_type TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def calculate_maturity_amount(self, principal, rate, time, is_cumulative):
        if is_cumulative:
            n = 1
            maturity_amount = principal * (1 + rate / (100 * n)) ** (n * time)
        else:
            maturity_amount = principal + (principal * rate * time / 100)
        return maturity_amount

    def validate_amount(self, amount_str):
        try:
            return float(amount_str)
        except ValueError:
            return None

    def validate_rate(self, rate_str):
        try:
            rate = float(rate_str)
            return rate
        except ValueError:
            return None

    def calculate(self):
        deposit_date = self.date_entry.date().toPyDate()
        money_deposited = self.deposit_entry.text()
        interest_rate = self.rate_entry.text()
        time_of_maturity = self.time_combobox.currentText()
        deposit_type = self.deposit_type_combobox.currentText()

        if not money_deposited or not interest_rate or deposit_type == "Select Deposit Type":
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        money_deposited_value = self.validate_amount(money_deposited)
        if money_deposited_value is None:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a valid amount deposited.")
            return

        interest_rate_value = self.validate_rate(interest_rate)
        if interest_rate_value is None:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a valid non-negative interest rate.")
            return

        time_of_maturity_value = float(time_of_maturity.split()[0])
        maturity_date_obj = deposit_date.replace(year=deposit_date.year + int(time_of_maturity_value))

        is_cumulative = deposit_type == "Cumulative"
        maturity_amount = self.calculate_maturity_amount(money_deposited_value, interest_rate_value, time_of_maturity_value, is_cumulative)

        self.save_to_database(deposit_date, maturity_date_obj, money_deposited_value, interest_rate_value, time_of_maturity_value, maturity_amount, deposit_type)

        self.update_table()

    def save_to_database(self, deposit_date, maturity_date, amount, interest_rate, time_of_maturity, maturity_amount, deposit_type):
        conn = sqlite3.connect("finance_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO interest_calculations (deposit_date, maturity_date, amount, interest_rate, time_of_maturity, maturity_amount, deposit_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (deposit_date.strftime("%d/%m/%Y"), maturity_date.strftime("%d/%m/%Y"), amount, interest_rate, time_of_maturity, maturity_amount, deposit_type))
        conn.commit()
        conn.close()

    def update_table(self):
        conn = sqlite3.connect("finance_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interest_calculations")
        rows = cursor.fetchall()
        conn.close()

        self.result_table.setRowCount(0)
        for row in rows:
            self.result_table.insertRow(self.result_table.rowCount())
            for i, item in enumerate(row[1:]):
                self.result_table.setItem(self.result_table.rowCount()-1, i, QtWidgets.QTableWidgetItem(str(item)))

    def delete_entry(self):
        selected_row = self.result_table.currentRow()
        if selected_row >= 0:
            self.result_table.removeRow(selected_row)
        else:
            QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select an entry to delete.")

    def save_as_pdf(self):
        filename = "interest_calculator_report.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 50, "Interest Calculator Report")
        c.setFont("Helvetica", 12)

        headers = ["Deposit Date", "Maturity Date", "Amount Deposited", "Interest Rate", "Time of Maturity", "Maturity Amount", "Deposit Type"]
        x_offset = 50
        y_offset = height - 100

        for header in headers:
            c.drawString(x_offset, y_offset, header)
            x_offset += 100

        y_offset -= 20

        for row in range(self.result_table.rowCount()):
            for column in range(self.result_table.columnCount()):
                item = self.result_table.item(row, column)
                if item is not None:
                    c.drawString(50 + column * 100, y_offset, item.text())
            y_offset -= 20

        c.save()
        QtWidgets.QMessageBox.information(self, "Success", f"PDF saved as {filename}")

def run_app():
    app = QtWidgets.QApplication(sys.argv)
    window = InterestCalculator(None)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()