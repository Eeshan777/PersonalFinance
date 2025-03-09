import tkinter as tk
from tkinter import messagebox
import os

class Auth:
    def __init__(self, root):
        self.root = root
        self.root.title("Signup/Login")
        self.root.configure(bg="#F5F5F5")  # Set background color

        self.username = None
        self.password = None

        self.show_auth_window()

    def show_auth_window(self):
        tk.Label(self.root, text="Choose an option:", font=("Helvetica", 16), bg="#F5F5F5", fg="#003366").pack(pady=20)

        signup_button = tk.Button(self.root, text="Sign Up", command=self.show_signup_window, bg="#0073E6", fg="#FFFFFF")
        signup_button.pack(pady=10)
        signup_button.bind("<Enter>", lambda e: signup_button.config(bg="#005BB5"))
        signup_button.bind("<Leave>", lambda e: signup_button.config(bg="#0073E6"))

        login_button = tk.Button(self.root, text="Login", command=self.show_login_window, bg="#0073E6", fg="#FFFFFF")
        login_button.pack(pady=10)
        login_button.bind("<Enter>", lambda e: login_button.config(bg="#005BB5"))
        login_button.bind("<Leave>", lambda e: login_button.config(bg="#0073E6"))

    def show_signup_window(self):
        self.signup_window = tk.Toplevel(self.root)
        self.signup_window.title("Sign Up")
        self.signup_window.configure(bg="#F5F5F5")  # Set background color

        tk.Label(self.signup_window, text="Username:", bg="#F5F5F5", fg="#003366").grid(row=0, column=0, padx=10, pady=10)
        self.signup_username_entry = tk.Entry(self.signup_window, bg="#FFFFFF")
        self.signup_username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.signup_username_entry.bind('<Return>', lambda event: self.signup_password_entry.focus_set())

        tk.Label(self.signup_window, text="Password:", bg="#F5F5F5", fg="#003366").grid(row=1, column=0, padx=10, pady=10)
        self.signup_password_entry = tk.Entry(self.signup_window, show='*', bg="#FFFFFF")
        self.signup_password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.signup_password_entry.bind('<Return>', self.save_credentials)

        signup_button = tk.Button(self.signup_window, text="Sign Up", command=self.save_credentials, bg="#0073E6", fg="#FFFFFF")
        signup_button.grid(row=2, column=0, columnspan=2, pady=10)
        signup_button.bind("<Enter>", lambda e: signup_button.config(bg="#005BB5"))
        signup_button.bind("<Leave>", lambda e: signup_button.config(bg="#0073E6"))

    def show_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.configure(bg="#F5F5F5")  # Set background color

        tk.Label(self.login_window, text="Username:", bg="#F5F5F5", fg="#003366").grid(row=0, column=0, padx=10, pady=10)
        self.login_username_entry = tk.Entry(self.login_window, bg="#FFFFFF")
        self.login_username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.login_username_entry.bind('<Return>', lambda event: self.login_password_entry.focus_set())

        tk.Label(self.login_window, text="Password:", bg="#F5F5F5", fg="#003366").grid(row=1, column=0, padx=10, pady=10)
        self.login_password_entry = tk.Entry(self.login_window, show='*', bg="#FFFFFF")
        self.login_password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.login_password_entry.bind('<Return>', self.check_credentials)

        login_button = tk.Button(self.login_window, text="Login", command=self.check_credentials, bg="#0073E6", fg="#FFFFFF")
        login_button.grid(row=2, column=0, columnspan=2, pady=10)
        login_button.bind("<Enter>", lambda e: login_button.config(bg="#005BB5"))
        login_button.bind("<Leave>", lambda e: login_button.config(bg="#0073E6"))

    def save_credentials(self, event=None):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()

        if username and password:
            with open("credentials.txt", "w") as f:
                f.write(f"{username}\n{password}")
            messagebox.showinfo("Success", "Signup successful! Please log in.")
            self.signup_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    def check_credentials(self, event=None):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if os.path.exists("credentials.txt"):
            with open("credentials.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 2 and lines[0].strip() == username and lines[1].strip() == password:
                    self.username = username
                    self.password = password
                    self.login_window.destroy()
                    self.root.destroy()  # Close the auth window
                    self.launch_Main()
                else:
                    messagebox.showwarning("Login Error", "Invalid username or password.")
        else:
            messagebox.showwarning("Login Error", "No credentials found. Please sign up first.")

    def launch_Main(self):
        import Main  # Import the main application code
        Main.run(self.username)  # Pass the username to the main app

if __name__ == "__main__":
    root = tk.Tk()
    app = Auth(root)
    root.mainloop()