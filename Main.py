import sys
from PyQt5 import QtWidgets, QtGui

class PersonalFinance(QtWidgets.QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Personal Finance")
        self.username = username
        self.setStyleSheet("background-color: #F5F5F5;")
        self.show_welcome_message()

    def show_welcome_message(self):
        layout = QtWidgets.QVBoxLayout()
        welcome_label = QtWidgets.QLabel(f"Welcome, {self.username}!")
        welcome_label.setFont(QtGui.QFont("Helvetica", 24))
        welcome_label.setStyleSheet("color: #003366;")
        layout.addWidget(welcome_label)

        # Add buttons and their connections here...
        interest_calculator_button = QtWidgets.QPushButton("Interest Calculator")
        interest_calculator_button.setStyleSheet("background-color: #0073E6; color: #FFFFFF;")
        interest_calculator_button.clicked.connect(self.launch_interest_calculator)
        layout.addWidget(interest_calculator_button)

        transaction_record_button = QtWidgets.QPushButton("Transaction Record")
        transaction_record_button.setStyleSheet("background-color: #0073E6; color: #FFFFFF;")
        transaction_record_button.clicked.connect(self.launch_transaction_record)
        layout.addWidget(transaction_record_button)

        budget_report_button = QtWidgets.QPushButton("Generate Budget Report")
        budget_report_button.setStyleSheet("background-color: #0073E6; color: #FFFFFF;")
        budget_report_button.clicked.connect(self.launch_budget_report)
        layout.addWidget(budget_report_button)

        self.setLayout(layout)

    def launch_interest_calculator(self):
        from InterestCalculator import InterestCalculator
        interest_calculator_window = QtWidgets.QDialog(self)
        interest_calculator = InterestCalculator(interest_calculator_window)
        interest_calculator_window.exec_()  # Show the dialog

    def launch_transaction_record(self):
        from TransactionRecord import TransactionRecord
        transaction_record_window = QtWidgets.QDialog(self)
        transaction_record = TransactionRecord(transaction_record_window)
        transaction_record_window.exec_()  # Show the dialog

    def launch_budget_report(self):
        from BudgetReport import BudgetReport
        budget_report_window = QtWidgets.QDialog(self)
        budget_report = BudgetReport(budget_report_window)
        budget_report_window.exec_()  # Show the dialog

def run(username):
    print("Running main application...")  # Debugging line
    try:
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication(sys.argv)
        window = PersonalFinance(username)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    print("Main module executed directly.")  # Debugging line
    pass