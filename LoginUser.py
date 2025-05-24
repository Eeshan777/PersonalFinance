import flet as ft
import sqlite3
import hashlib

def initialize_database():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        conn.commit()

def validate_credentials(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash the password
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = cursor.fetchone()
    return user is not None

def save_session(username, password):
    with open("credentials.txt", "w") as f:
        f.write(username)
        f.write(password)

def load_session():
    try:
        with open("credentials.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def login_ui(page: ft.Page):
    page.title = "Personal Finance - Login"
    page.bgcolor = "#E3F2FD"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    username_field = ft.TextField(label="Username", width=350, bgcolor="#FFFFFF", border_radius=8, color="black")
    password_field = ft.TextField(label="Password", width=350, password=True, bgcolor="#FFFFFF", border_radius=8, color="black")
    message_text = ft.Text("", color="red")
    
    def handle_login(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        
        if validate_credentials(username, password):
            save_session(username, password)
            page.clean()  # Clear the page
            from Main import main_page
            main_page(page)  # Call the main page function
        else:
            message_text.value = "Invalid credentials. Try again."
            page.update()
        
    def handle_enter(e):
        if e.control == username_field:
            password_field.focus()
        elif e.control == password_field and username_field.value.strip():
            handle_login(None)
        page.update()
    
    username_field.on_submit = handle_enter
    password_field.on_submit = handle_enter
    
    login_button = ft.ElevatedButton("Login", on_click=handle_login, bgcolor="#1565C0", style=ft.ButtonStyle(color="white"), width=350)
    signup_button = ft.TextButton("Create an account", on_click=lambda e: signup_ui(page), style=ft.ButtonStyle(color="#1565C0"))
    
    page.add(
        ft.Container(
            content=ft.Column([ 
                ft.Text("Personal Finance", size=30, weight=ft.FontWeight.BOLD, color="#0D47A1"),
                username_field,
                password_field,
                login_button,
                signup_button,
                message_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            width=400,
            bgcolor="white",
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=15, color="#B0BEC5")
        )
    )

def signup_ui(page: ft.Page):
    page.clean()
    page.title = "Personal Finance - Signup"
    
    username_field = ft.TextField(label="Username", width=350, bgcolor="#FFFFFF", border_radius=8, color="black")
    password_field = ft.TextField(label="Password", width=350, password=True, bgcolor="#FFFFFF", border_radius=8, color="black")
    message_text = ft.Text("", color="red")
    
    def handle_signup(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        if len(password) < 6:
            message_text.value = "Password must be at least 6 characters."
        elif check_username_exists(username):
            message_text.value = "Username already taken."
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            try:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                    conn.commit()
                message_text.value = "Signup successful! Please login."
                page.update()
                login_ui(page)  # Go back to login UI
            except sqlite3.Error as e:
                message_text.value = f"Database error: {e}"
                page.update()
        
    def handle_enter(e):
        if e.control == username_field:
            password_field.focus()
        elif e.control == password_field and username_field.value.strip():
            handle_signup(None)
        page.update()
    
    username_field.on_submit = handle_enter
    password_field.on_submit = handle_enter
    
    signup_button = ft.ElevatedButton("Signup", on_click=handle_signup, bgcolor="#2E7D32", style=ft.ButtonStyle(color="white"), width=350)
    login_button = ft.TextButton("Already have an account? Login", on_click=lambda e: login_ui(page), style=ft.ButtonStyle(color="#1565C0"))
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Create Account", size=30, weight=ft.FontWeight.BOLD, color="#1B5E20"),
                username_field,
                password_field,
                signup_button,
                login_button,
                message_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            width=400,
            bgcolor="white",
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=15, color="#B0BEC5")
        )
    )

def check_username_exists(username):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
    return user is not None

if __name__ == "__main__":
    initialize_database()
    ft.app(target=login_ui)