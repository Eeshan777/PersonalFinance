import flet as ft
from LoginUser import login_ui

def main_page(page: ft.Page):
    username = load_session()
    if username:
        page.clean()
        setup_main_ui(page, username)
    else:
        page.clean()
        login_ui(page)

def load_session():
    try:
        with open("credentials.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def setup_main_ui(page: ft.Page, username: str):
    page.title = "Personal Finance"
    page.bgcolor = "#E3F2FD"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    layout = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=25
    )

    layout.controls.append(
        ft.Text("Personal Finance", size=30, weight=ft.FontWeight.BOLD, color="#0D47A1")
    )
    layout.controls.append(
        ft.Text(f"Welcome, {username}!", size=24, weight=ft.FontWeight.BOLD, color="#003366")
    )

    button_style = ft.ButtonStyle(
        bgcolor="#1565C0",
        color="white",
        shape=ft.RoundedRectangleBorder(radius=10),
        padding=ft.padding.symmetric(vertical=20, horizontal=20),
        elevation=6,
    )

    buttons = [
        ft.ElevatedButton("Transaction Record", on_click=lambda e: launch_transaction_record(page), style=button_style, width=380),
        ft.ElevatedButton("Interest Calculator", on_click=lambda e: launch_interest_calculator(page), style=button_style, width=380),
        ft.ElevatedButton("Budget Report", on_click=lambda e: launch_budget_report(page), style=button_style, width=380),
        ft.ElevatedButton("Download PDF", on_click=lambda e: launch_download_pdf(page), style=button_style, width=380)
    ]

    logout_button = ft.ElevatedButton(
        "Logout",
        on_click=lambda e: logout(page),
        style=ft.ButtonStyle(color="white"),
        width=80,
        bgcolor="#FF0000"
    )

    layout.controls.extend(buttons)
    layout.controls.append(logout_button)
    page.add(layout)

def logout(page: ft.Page):
    with open("credentials.txt", "w") as f:
        f.write("")
    page.clean()
    login_ui(page)

def launch_transaction_record(page: ft.Page):
    from TransactionRecord import TransactionRecord
    view = ft.View(route="/transaction", controls=[], bgcolor="#E3F2FD", scroll=ft.ScrollMode.AUTO)
    TransactionRecord(page, view)
    page.views.append(view)
    page.go("/transaction")

def launch_interest_calculator(page: ft.Page):
    from InterestCalculator import InterestCalculator
    view = ft.View(route="/interest-calculator", controls=[], bgcolor="#E3F2FD", scroll=ft.ScrollMode.AUTO)
    InterestCalculator(page, view)
    page.views.append(view)
    page.go("/interest-calculator")

def launch_budget_report(page: ft.Page):
    from BudgetReport import BudgetReport
    view = ft.View(route="/budget-report", controls=[], bgcolor="#E3F2FD", scroll=ft.ScrollMode.AUTO)
    BudgetReport(page, view)
    page.views.append(view)
    page.go("/budget-report")

def launch_download_pdf(page: ft.Page):
    from DownloadPDF import DownloadPDF
    view = ft.View(route="/download-pdf", controls=[], bgcolor="#E3F2FD", scroll=ft.ScrollMode.AUTO)
    DownloadPDF(page, view)
    page.views.append(view)
    page.go("/download-pdf")