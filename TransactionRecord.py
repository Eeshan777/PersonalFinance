import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class TransactionRecord(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Income and Expense Management")
        self.setStyleSheet("background-color: #F5F5F5;")
        self.entries = []
        self.create_database()
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.type_var = QtWidgets.QComboBox(self)
        self.type_var.addItems(["Income", "Expense"])
        layout.addWidget(self.type_var)

        self.particular_entry = QtWidgets.QLineEdit(self)
        self.particular_entry.setPlaceholderText("Particular")
        layout.addWidget(self.particular_entry)

        self.amount_entry = QtWidgets.QLineEdit(self)
        self.amount_entry.setPlaceholderText("Amount")
        layout.addWidget(self.amount_entry)

        self.date_entry = QtWidgets.QLineEdit(self)
        self.date_entry.setPlaceholderText("Date (DD/MM/YYYY)")
        layout.addWidget(self.date_entry)

        add_button = QtWidgets.QPushButton("Add Entry", self)
        add_button.clicked.connect(self.add_entry)
        layout.addWidget(add_button)

        self.tree = QtWidgets.QTableWidget(self)
        self.tree.setColumnCount(5)
        self.tree.setHorizontalHeaderLabels(["Date", "Particular", "Income", "Expenditure", "Balance"])
        layout.addWidget(self.tree)

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
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                date TEXT,
                particular TEXT,
                amount REAL,
                type TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_entry(self):
        particular = self.particular_entry.text()
        amount = self.amount_entry.text()
        date = self.date_entry.text()
        entry_type = self.type_var.currentText()

        if particular and amount and date:
            try:
                amount_value = float(amount)
                date_obj = datetime.strptime(date, "%d/%m/%Y")
                current_date = datetime.now()
                if date_obj > current_date:
                    reply = QtWidgets.QMessageBox.question(self, "Future Date", 
                        "The date is in the future. Are you sure?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.No:
                        return
            except ValueError:
                QtWidgets.QMessageBox.warning(self, "Input Error", "Ensure the date is in DD/MM/YYYY format and valid.")
                return

            self.save_to_database(date_obj, particular, amount_value, entry_type)
            self.entries.append({'date': date_obj, 'particular': particular, 'amount': amount_value, 'type': entry_type})
            self.update_treeview()
        else:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please fill in all fields.")

    def save_to_database(self, date, particular, amount, entry_type):
        conn = sqlite3.connect("finance_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (date, particular, amount, type) VALUES (?, ?, ?, ?)",
                       (date.strftime("%d/%m/%Y"), particular, amount, entry_type))
        conn.commit()
        conn.close()

    def update_treeview(self):
        conn = sqlite3.connect("finance_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        conn.close()

        self.tree.setRowCount(0)
        balance = 0
        for row in rows:
            self.tree.insertRow(self.tree.rowCount())
            income_value = row[3] if row[4] == "Income" else ""
            expenditure_value = row[3] if row[4] == "Expense" else ""
            if row[4] == "Income":
                balance += row[3]
            else:
                balance -= row[3]
            date_str = row[1]
            self.tree.setItem(self.tree.rowCount()-1, 0, QtWidgets.QTableWidgetItem(date_str))
            self.tree.setItem(self.tree.rowCount()-1, 1, QtWidgets.QTableWidgetItem(row[2]))
            self.tree.setItem(self.tree.rowCount()-1, 2, QtWidgets.QTableWidgetItem(str(income_value)))
            self.tree.setItem(self.tree.rowCount()-1, 3, QtWidgets.QTableWidgetItem(str(expenditure_value)))
            self.tree.setItem(self.tree.rowCount()-1, 4, QtWidgets.QTableWidgetItem(str(balance)))

    def delete_entry(self):
        selected_row = self.tree.currentRow()
        if selected_row >= 0:
            self.tree.removeRow(selected_row)
        else:
            QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select an entry to delete.")

    def save_as_pdf(self):
        filename = "transaction_record_report.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 50, "Transaction Record Report")
        c.setFont("Helvetica", 12)

        headers = ["Date", "Particular", "Income", "Expenditure", "Balance"]
        x_offset = 50
        y_offset = height - 100

        for header in headers:
            c.drawString(x_offset, y_offset, header)
            x_offset += 100

        y_offset -= 20

        balance = 0
        for row in range(self.tree.rowCount()):
            date_item = self.tree.item(row, 0)
            particular_item = self.tree.item(row, 1)
            income_item = self.tree.item(row, 2)
            expenditure_item = self.tree.item(row, 3)

            c.drawString(50, y_offset, date_item.text())
            c.drawString(150, y_offset, particular_item.text())
            c.drawString(250, y_offset, income_item.text())
            c.drawString(350, y_offset, expenditure_item.text())
            balance += float(income_item.text() or 0) - float(expenditure_item.text() or 0)
            c.drawString(450, y_offset, str(balance))
            y_offset -= 20

        c.save()
        QtWidgets.QMessageBox.information(self, "Success", f"PDF saved as {filename}")

def run_app():
    app = QtWidgets.QApplication(sys.argv)
    window = TransactionRecord(None)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()