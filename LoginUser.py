import sys
import os
from PyQt5 import QtWidgets, QtGui
import hashlib

class Auth(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signup/Login")
        self.setStyleSheet("background-color: #F5F5F5;")
        self.username = None
        self.password = None
        self.show_auth_window()

    def show_auth_window(self):
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Choose an option:")
        label.setFont(QtGui.QFont("Helvetica", 16))
        label.setStyleSheet("color: #003366;")
        layout.addWidget(label)

        signup_button = QtWidgets.QPushButton("Sign Up")
        signup_button.setStyleSheet("background-color: #0073E6; color: #FFFFFF;")
        signup_button.clicked.connect(self.show_signup_window)
        layout.addWidget(signup_button)

        login_button = QtWidgets.QPushButton("Login")
        login_button.setStyleSheet("background-color: #0073E6; color: #FFFFFF;")
        login_button.clicked.connect(self.show_login_window)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def show_signup_window(self):
        self.signup_window = QtWidgets.QDialog(self)
        self.signup_window.setWindowTitle("Sign Up")
        self.signup_window.setStyleSheet("background-color: #F5F5F5;")
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel("Username:", self.signup_window))
        self.signup_username_entry = QtWidgets.QLineEdit(self.signup_window)
        layout.addWidget(self.signup_username_entry)

        layout.addWidget(QtWidgets.QLabel("Password:", self.signup_window))
        self.signup_password_entry = QtWidgets.QLineEdit(self.signup_window)
        self.signup_password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.signup_password_entry)

        signup_button = QtWidgets.QPushButton("Sign Up", self.signup_window)
        signup_button.clicked.connect(self.save_credentials)
        layout.addWidget(signup_button)

        self.signup_window.setLayout(layout)
        self.signup_window.exec_()

    def show_login_window(self):
        self.login_window = QtWidgets.QDialog(self)
        self.login_window.setWindowTitle("Login")
        self.login_window.setStyleSheet("background-color: #F5F5F5;")
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel("Username:", self.login_window))
        self.login_username_entry = QtWidgets.QLineEdit(self.login_window)
        layout.addWidget(self.login_username_entry)

        layout.addWidget(QtWidgets.QLabel("Password:", self.login_window))
        self.login_password_entry = QtWidgets.QLineEdit(self.login_window)
        self.login_password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.login_password_entry)

        login_button = QtWidgets.QPushButton("Login", self.login_window)
        login_button.clicked.connect(self.check_credentials)
        layout.addWidget(login_button)

        self.login_window.setLayout(layout)
        self.login_window.exec_()

    def save_credentials(self):
        username = self.signup_username_entry.text()
        password = self.signup_password_entry.text()

        if username and password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            with open("credentials.txt", "w") as f:
                f.write(f"{username}\n{hashed_password}")
            QtWidgets.QMessageBox.information(self, "Success", "Signup successful! Please log in.")
            self.signup_window.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter both username and password.")

    def check_credentials(self):
        username = self.login_username_entry.text()
        password = self.login_password_entry.text()

        if os.path.exists("credentials.txt"):
            with open("credentials.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 2 and lines[0].strip() == username and lines[1].strip() == hashlib.sha256(password.encode()).hexdigest():
                    self.username = username
                    self.password = password
                    self.login_window.close()
                    print("Login successful, launching main application...")  # Debugging line
                    self.launch_Main()
                else:
                    QtWidgets.QMessageBox.warning(self, "Login Error", "Invalid username or password.")
        else:
            QtWidgets.QMessageBox.warning(self, "Login Error", "No credentials found. Please sign up first.")

    def launch_Main(self):
        import Main  # Import the main application code
        try:
            print("Attempting to launch main application...")  # Debugging line
            if not QtWidgets.QApplication.instance():
                app = QtWidgets.QApplication(sys.argv)
            else:
                app = QtWidgets.QApplication.instance()
            Main.run(self.username)  # Pass the username to the main app
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to launch main application: {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Auth()
    window.show()
    sys.exit(app.exec_())