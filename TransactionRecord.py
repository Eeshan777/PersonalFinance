import flet as ft
import sqlite3
from Main import get_db_path
import datetime

class TransactionRecord:
    def __init__(self, page, view: ft.View):
        self.page = page
        self.view = view
        self.page.window_maximized = True
        self.page.window_full_screen = True
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.update()

        self.entries = []
        self.balance = 0

        self.view.title = "Transaction Record"
        self.view.bgcolor = "#E3F2FD"

        self.date_picker = ft.DatePicker(
            on_change=self.date_selected,
            first_date=datetime.date(2000, 1, 1),
            last_date=datetime.date(2025, 12, 31),
        )
        self.page.overlay.append(self.date_picker)

        field_width = 360

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

        self.type_dropdown = ft.Dropdown(
            label="Type",
            options=[ft.dropdown.Option("Income"), ft.dropdown.Option("Expense")],
            width=field_width,
            dense=True,
            on_change=lambda e: self.particular_field.focus()
        )

        self.particular_field = ft.TextField(
            label="Particular",
            width=field_width,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            on_submit=lambda e: self.amount_field.focus()
        )

        self.amount_field = ft.TextField(
            label="Amount",
            width=field_width,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            on_submit=lambda e: self.classification_dropdown.focus()
        )

        self.classification_dropdown = ft.Dropdown(
            label="Classification",
            options=[
                ft.dropdown.Option("Food"), ft.dropdown.Option("Clothes"), ft.dropdown.Option("Bills/Rent"),
                ft.dropdown.Option("Larger Purchases"), ft.dropdown.Option("Transportation"),
                ft.dropdown.Option("Groceries"), ft.dropdown.Option("Entertainment"),
                ft.dropdown.Option("Salary"), ft.dropdown.Option("Loan/Debt")
            ],
            width=field_width,
            dense=True,
            on_change=lambda e: self.add_button.focus()
        )

        self.add_button = ft.ElevatedButton(
            "Add", on_click=self.add_entry, width=130,
            bgcolor="#1565C0", color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        self.save_button = ft.ElevatedButton(
            "Save", on_click=self.save_to_database, width=130,
            bgcolor="#0D47A1", color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        self.table = self.create_data_table()

        self.header = ft.Row([
            ft.IconButton(icon="arrow_back", on_click=self.go_back),
            ft.Container(
                content=ft.Text("Transaction Record", size=24, weight=ft.FontWeight.BOLD, color="#0D47A1"),
                alignment=ft.alignment.center,
                expand=True
            )
        ], alignment=ft.MainAxisAlignment.START, spacing=5)

        self.main_layout = ft.Column(
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self.header,
                self.type_dropdown,
                self.particular_field,
                self.amount_field,
                self.date_field,
                self.classification_dropdown,
                ft.Row([self.add_button, self.save_button], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                ft.Container(
                    bgcolor="white",
                    padding=15,
                    border_radius=15,
                    height=300,
                    width=850,
                    border=ft.border.all(1, "#90CAF9"),
                    content=ft.Column([self.table], expand=True, scroll=ft.ScrollMode.AUTO)
                )
            ]
        )

        self.view.controls.clear()
        self.view.controls.append(self.main_layout)
        self.load_balance()

    def open_date_picker(self):
        self.date_picker.open = True
        self.page.update()

    def date_selected(self, e):
        if self.date_picker.value:
            picked = self.date_picker.value
            self.date_field.value = picked.strftime("%d/%m/%Y")
            self.type_dropdown.focus()
            self.page.update()

    def go_back(self, e):
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.update()

    def create_data_table(self):
        return ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Date", size=14)),
            ft.DataColumn(ft.Text("Particular", size=14)),
            ft.DataColumn(ft.Text("Income", size=14)),
            ft.DataColumn(ft.Text("Expense", size=14)),
            ft.DataColumn(ft.Text("Balance", size=14)),
            ft.DataColumn(ft.Text("Classification", size=14)),
            ft.DataColumn(ft.Text("Actions", size=14)),
        ], rows=[])

    def add_entry(self, e):
        particular = self.particular_field.value
        amount = self.amount_field.value
        date_val = self.date_field.value
        entry_type = self.type_dropdown.value
        classification = self.classification_dropdown.value

        if not all([particular, amount, date_val, entry_type, classification]):
            self.show_snack_bar("Please fill all fields.", "red")
            return

        try:
            amount_val = float(amount)
        except ValueError:
            self.show_snack_bar("Invalid amount.", "red")
            return

        income = amount_val if entry_type == "Income" else ""
        expense = amount_val if entry_type == "Expense" else ""
        self.balance += amount_val if entry_type == "Income" else -amount_val

        delete_icon = ft.IconButton(
            icon="delete",
            on_click=lambda e, r=(date_val, particular, amount_val, entry_type, classification): self.delete_entry(r)
        )

        self.table.rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(date_val, size=14)),
            ft.DataCell(ft.Text(particular, size=14)),
            ft.DataCell(ft.Text(str(income), size=14)),
            ft.DataCell(ft.Text(str(expense), size=14)),
            ft.DataCell(ft.Text(str(self.balance), size=14)),
            ft.DataCell(ft.Text(classification, size=14)),
            ft.DataCell(delete_icon)
        ]))

        self.entries.append({
            "date": datetime.datetime.strptime(date_val, "%d/%m/%Y").strftime("%Y-%m-%d"),
            "particular": particular,
            "amount": amount_val,
            "type": entry_type,
            "classification": classification
        })


        self.clear_inputs()
        self.page.update()

    def clear_inputs(self):
        self.particular_field.value = ""
        self.amount_field.value = ""
        self.date_field.value = ""
        self.type_dropdown.value = ""
        self.classification_dropdown.value = ""
        self.particular_field.focus()

    def delete_entry(self, entry):
        self.table.rows = [r for r in self.table.rows if not (
            r.cells[0].content.value == entry[0] and
            r.cells[1].content.value == entry[1]
        )]
        self.page.update()

    def save_to_database(self, e):
        if not self.entries:
            self.show_snack_bar("No new entries to save.", "red")
            return

        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    particular TEXT,
                    amount REAL,
                    type TEXT,
                    classification TEXT
                )
            ''')
            for entry in self.entries:
                cursor.execute('''
                    INSERT INTO transactions (date, particular, amount, type, classification)
                    VALUES (?, ?, ?, ?, ?)
                ''', (entry["date"], entry["particular"], entry["amount"], entry["type"], entry["classification"]))
            conn.commit()
            conn.close()
            self.entries.clear()
            self.show_snack_bar("Saved successfully!", "green")
        except Exception as ex:
            self.show_snack_bar(f"Error saving: {str(ex)}", "red")

    def load_balance(self):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(CASE WHEN type='Income' THEN amount ELSE 0 END) -
                       SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END)
                FROM transactions
            ''')
            self.balance = cursor.fetchone()[0] or 0
            conn.close()
        except:
            self.balance = 0

    def show_snack_bar(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg, size=14), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()