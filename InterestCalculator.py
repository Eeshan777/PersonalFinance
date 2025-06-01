import flet as ft
import sqlite3
from datetime import date, datetime, timedelta

class InterestCalculator:
    def __init__(self, page, view: ft.View):
        self.page = page
        self.view = view
        self.page.window_maximized = True
        self.page.window_full_screen = True
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.update()

        self.entries = []
        self.view.title = "Interest Calculator"
        self.view.bgcolor = "#E3F2FD"

        self.date_picker = ft.DatePicker(
            on_change=self.date_selected,
            first_date=date(2000, 1, 1),
            last_date=date(2025, 12, 31),
        )
        self.page.overlay.append(self.date_picker)

        field_width = 360

        self.deposit_type_dropdown = ft.Dropdown(
            label="Deposit Type",
            options=[ft.dropdown.Option("Cumulative"), ft.dropdown.Option("Non-Cumulative")],
            width=field_width,
            dense=True,
            on_change=lambda e: self.date_field.focus()
        )

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

        self.amount_field = ft.TextField(
            label="Amount",
            width=field_width,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            on_submit=lambda e: self.rate_field.focus()
        )

        self.rate_field = ft.TextField(
            label="Interest Rate (%)",
            width=field_width,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            on_submit=lambda e: self.time_dropdown.focus()
        )

        self.time_dropdown = ft.Dropdown(
            label="Time to Maturity",
            options=[ft.dropdown.Option(f"{i} year{'s' if i > 1 else ''}") for i in [1, 2, 3, 5, 10]],
            width=field_width,
            dense=True,
            on_change=lambda e: self.add_button.focus()
        )

        self.add_button = ft.ElevatedButton(
            "Add Entry", on_click=self.add_entry, width=130,
            bgcolor="#1565C0", color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        self.save_button = ft.ElevatedButton(
            "Save to DB", on_click=self.save_to_database, width=130,
            bgcolor="#0D47A1", color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        self.table = self.create_data_table()
        self.create_table_in_db()

        self.header = ft.Row([
            ft.IconButton(icon="arrow_back", on_click=self.go_back),
            ft.Container(
                content=ft.Text("Interest Calculator", size=24, weight=ft.FontWeight.BOLD, color="#0D47A1"),
                alignment=ft.alignment.center,
                expand=True
            )
        ], alignment=ft.MainAxisAlignment.START, spacing=5)

        self.form_column = ft.Column([
            self.deposit_type_dropdown,
            self.date_field,
            self.amount_field,
            self.rate_field,
            self.time_dropdown,
            ft.Row([self.add_button, self.save_button], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.display_panel = ft.Container(
            bgcolor="white",
            padding=15,
            border_radius=15,
            height=300,
            width=850,
            border=ft.border.all(1, "#90CAF9"),
            content=ft.Column([self.table], expand=True, scroll=ft.ScrollMode.AUTO)
        )

        self.main_layout = ft.Column([
            self.header,
            self.form_column,
            self.display_panel
        ], spacing=15,
           scroll=ft.ScrollMode.AUTO,
           expand=True,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.view.controls.clear()
        self.view.controls.append(self.main_layout)

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

    def create_table_in_db(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interest_calculations (
                id INTEGER PRIMARY KEY,
                deposit_date TEXT,
                maturity_date TEXT,
                amount REAL,
                interest_rate REAL,
                time_of_maturity TEXT,
                maturity_amount REAL,
                deposit_type TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def create_data_table(self):
        return ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Deposit Date", size=14)),
            ft.DataColumn(ft.Text("Maturity Date", size=14)),
            ft.DataColumn(ft.Text("Amount", size=14)),
            ft.DataColumn(ft.Text("Rate", size=14)),
            ft.DataColumn(ft.Text("Time", size=14)),
            ft.DataColumn(ft.Text("Maturity", size=14)),
            ft.DataColumn(ft.Text("Type", size=14)),
            ft.DataColumn(ft.Text("Actions", size=14)),
        ], rows=[])

    def calculate_maturity(self, amount, rate, years, is_cumulative):
        return amount * (1 + rate / 100) ** years if is_cumulative else amount + (amount * rate * years / 100)

    def add_entry(self, e):
        try:
            deposit_date_str = self.date_field.value
            deposit_date = datetime.strptime(deposit_date_str, "%d/%m/%Y")
            amount = float(self.amount_field.value)
            rate = float(self.rate_field.value)
            years = int(self.time_dropdown.value.split()[0])
            deposit_type = self.deposit_type_dropdown.value

            maturity_date = deposit_date + timedelta(days=365 * years)
            maturity_amount = self.calculate_maturity(amount, rate, years, deposit_type == "Cumulative")

            row_data = {
                "deposit_date": deposit_date_str,
                "maturity_date": maturity_date.strftime("%d/%m/%Y"),
                "amount": amount,
                "rate": rate,
                "time": f"{years} year(s)",
                "maturity_amount": maturity_amount,
                "type": deposit_type
            }

            delete_icon = ft.IconButton(
                icon="delete",
                on_click=lambda e, r=row_data: self.delete_entry(r)
            )

            self.table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(row_data["deposit_date"], size=14)),
                ft.DataCell(ft.Text(row_data["maturity_date"], size=14)),
                ft.DataCell(ft.Text(str(row_data["amount"]), size=14)),
                ft.DataCell(ft.Text(str(row_data["rate"]), size=14)),
                ft.DataCell(ft.Text(row_data["time"], size=14)),
                ft.DataCell(ft.Text(f"{row_data['maturity_amount']:.2f}", size=14)),
                ft.DataCell(ft.Text(row_data["type"], size=14)),
                ft.DataCell(delete_icon),
            ]))

            self.entries.append(row_data)
            self.clear_fields()
            self.page.update()

        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", "red")

    def clear_fields(self):
        self.date_field.value = ""
        self.amount_field.value = ""
        self.rate_field.value = ""
        self.time_dropdown.value = ""
        self.deposit_type_dropdown.value = ""
        self.deposit_type_dropdown.focus()

    def delete_entry(self, entry):
        self.table.rows = [row for row in self.table.rows if not (
            row.cells[0].content.value == entry["deposit_date"]
        )]
        self.entries = [e for e in self.entries if e["deposit_date"] != entry["deposit_date"]]
        self.page.update()

    def save_to_database(self, e):
        if not self.entries:
            self.show_snack_bar("No entries to save.", "red")
            return

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            for entry in self.entries:
                cursor.execute('''
                    INSERT INTO interest_calculations
                    (deposit_date, maturity_date, amount, interest_rate, time_of_maturity, maturity_amount, deposit_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry["deposit_date"],
                    entry["maturity_date"],
                    entry["amount"],
                    entry["rate"],
                    entry["time"],
                    entry["maturity_amount"],
                    entry["type"]
                ))
            conn.commit()
            conn.close()
            self.entries.clear()
            self.show_snack_bar("Saved successfully.", "green")
        except Exception as ex:
            self.show_snack_bar(f"Database Error: {str(ex)}", "red")

    def show_snack_bar(self, message, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(message, size=14), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()