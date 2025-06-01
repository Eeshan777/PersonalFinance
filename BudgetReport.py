import flet as ft
import sqlite3
import datetime

class BudgetReport:
    def __init__(self, page, view: ft.View):
        self.page = page
        self.view = view
        self.page.window_maximized = True
        self.page.window_full_screen = True
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.update()

        self.view.title = "Budget Report"
        self.view.bgcolor = "#E3F2FD"

        field_width = 360

        self.date_picker = ft.DatePicker(
            on_change=self.date_selected,
            first_date=datetime.date(2000, 1, 1),
            last_date=datetime.date(2025, 12, 31),
        )
        self.page.overlay.append(self.date_picker)

        self.date_field = ft.TextField(
            label="Enter Date (DD/MM/YYYY)",
            width=field_width,
            text_align=ft.TextAlign.CENTER,
            read_only=True,
            dense=True,
            suffix=ft.IconButton(
                icon="calendar_month",
                on_click=lambda e: self.open_date_picker()
            ),
            on_submit=lambda e: self.type_dropdown.focus()
        )

        self.report_type_dropdown = ft.Dropdown(
            label="Report Type",
            width=field_width,
            dense=True,
            options=[ft.dropdown.Option("Monthly"), ft.dropdown.Option("Yearly")],
            on_change=lambda e: self.generate_button.focus()
        )

        self.generate_button = ft.ElevatedButton(
            "Generate Report",
            width=field_width,
            height=48,
            bgcolor="#1565C0",
            color="white",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding(10, 16, 10, 16),
                bgcolor={"": "#1565C0", "hovered": "#0D47A1"},
            ),
            on_click=self.generate_report
        )

        self.report_display = ft.Container(
            bgcolor="white",
            padding=15,
            border_radius=15,
            height=240,
            width=780,
            border=ft.border.all(1, "#90CAF9"),
            content=ft.Text("", size=14),
            alignment=ft.alignment.top_left
        )

        self.header = ft.Row([
            ft.IconButton(icon="arrow_back", on_click=self.go_back),
            ft.Container(
                content=ft.Text("Budget Report", size=24, weight=ft.FontWeight.BOLD, color="#0D47A1"),
                expand=True,
                alignment=ft.alignment.center
            )
        ], alignment=ft.MainAxisAlignment.START, spacing=5)

        self.form_column = ft.Column([
            self.date_field,
            self.report_type_dropdown,
            self.generate_button
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.main_layout = ft.Column([
            self.header,
            self.form_column,
            self.report_display
        ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.view.controls.clear()
        self.view.controls.append(self.main_layout)

    def go_back(self, e):
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.update()

    def open_date_picker(self):
        self.date_picker.open = True
        self.page.update()

    def date_selected(self, e):
        if self.date_picker.value:
            picked = self.date_picker.value
            self.date_field.value = picked.strftime("%d/%m/%Y")
            self.type_dropdown.focus()
            self.page.update()

    def fetch_data(self, selected_date, report_type):
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            if report_type == "Monthly":
                key = selected_date.strftime("%m/%Y")
                cursor.execute("SELECT * FROM transactions WHERE strftime('%m/%Y', date) = ?", (key,))
                transactions = cursor.fetchall()
                cursor.execute("SELECT * FROM interest_calculations WHERE strftime('%Y', deposit_date) = ?", (selected_date.strftime("%Y"),))
                interest = cursor.fetchall()
            else:
                key = selected_date.strftime("%Y")
                cursor.execute("SELECT * FROM transactions WHERE strftime('%Y', date) = ?", (key,))
                transactions = cursor.fetchall()
                cursor.execute("SELECT * FROM interest_calculations WHERE strftime('%Y', deposit_date) = ?", (key,))
                interest = cursor.fetchall()

            conn.close()
            return transactions, interest
        except Exception as ex:
            self.show_snack_bar(f"Database error: {str(ex)}", "red")
            return [], []

    def calculate_budget(self, transactions, interest_data):
        income = sum(t[3] for t in transactions if t[4] == "Income")
        expenses = sum(t[3] for t in transactions if t[4] == "Expense")
        interest = sum(i[6] for i in interest_data)
        return income, expenses, interest, income - expenses + interest

    def generate_report(self, e):
        if not self.date_field.value or not self.report_type_dropdown.value:
            self.show_snack_bar("Please select both date and report type.", "red")
            return

        date = datetime.datetime.strptime(self.date_field.value, "%d/%m/%Y")
        rtype = self.report_type_dropdown.value

        transactions, interest_data = self.fetch_data(date, rtype)

        if not transactions and not interest_data:
            self.show_snack_bar("No data found for this period.", "red")
            return

        income, expense, interest, net = self.calculate_budget(transactions, interest_data)

        result = (
            f"Report Type: {rtype}\n"
            f"Period: {date.strftime('%B %Y') if rtype == 'Monthly' else date.strftime('%Y')}\n\n"
            f"Total Income: ₹ {income:.2f}\n"
            f"Total Expenses: ₹ {expense:.2f}\n"
            f"Total Interest: ₹ {interest:.2f}\n"
            f"Net Budget: ₹ {net:.2f}"
        )

        self.report_display.content.value = result
        self.page.update()

    def show_snack_bar(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg, size=14), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()