import flet as ft
import sqlite3
from Main import get_db_path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import datetime


class DownloadPDF:
    def __init__(self, page, view: ft.View):
        self.page = page
        self.view = view
        self.page.window_maximized = True
        self.page.window_full_screen = True
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.update()

        self.view.title = "Download PDF"
        self.view.bgcolor = "#E3F2FD"

        field_width = 360

        # Date Picker
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
            on_submit=lambda e: self.report_type_dropdown.focus()
        )

        # Dropdown
        self.report_type_dropdown = ft.Dropdown(
            label="Report Type",
            width=field_width,
            dense=True,
            options=[
                ft.dropdown.Option("Interest Calculator"),
                ft.dropdown.Option("Transaction Record")
            ],
            on_change=lambda e: self.generate_button.focus()
        )

        # File Picker
        self.file_picker = ft.FilePicker(on_result=self.save_path_selected)
        self.page.overlay.append(self.file_picker)

        # Button
        self.generate_button = ft.ElevatedButton(
            "Generate PDF",
            width=field_width,
            bgcolor="#1565C0",
            color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.request_file_save_location
        )

        # Header and layout
        self.header = ft.Row([
            ft.IconButton(icon="arrow_back", on_click=self.go_back),
            ft.Container(
                content=ft.Text("Download PDF", size=24, weight=ft.FontWeight.BOLD, color="#0D47A1"),
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
            self.form_column
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
            self.report_type_dropdown.focus()
            self.page.update()

    def request_file_save_location(self, e):
        # Check fields first
        if not self.date_field.value or not self.report_type_dropdown.value:
            self.show_snack_bar("Please select report type and date.", "red")
            return

        default_name = self.report_type_dropdown.value.lower().replace(" ", "_") + "_report.pdf"
        self.file_picker.save_file(dialog_title="Save PDF As", file_name=default_name)

    def save_path_selected(self, e: ft.FilePickerResultEvent):
        if not e.path:
            self.show_snack_bar("PDF save cancelled.", "red")
            return
        self.generate_pdf_file(e.path)

    def generate_pdf_file(self, file_path):
        report_type = self.report_type_dropdown.value
        date_val = datetime.datetime.strptime(self.date_field.value, "%d/%m/%Y")
        month = date_val.strftime("%m")
        year = date_val.strftime("%Y")

        pdf = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []

        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()

            if report_type == "Interest Calculator":
                headers = ["Deposit Date", "Maturity Date", "Deposit Type", "Amount", "Interest Rate", "Time", "Maturity"]
                data = [headers]
                cursor.execute("SELECT * FROM interest_calculations WHERE strftime('%m', deposit_date) = ? AND strftime('%Y', deposit_date) = ?", (month, year))
                entries = cursor.fetchall()
                for row in entries:
                    data.append([row[1], row[2], row[7], row[3], row[4], row[5], row[6]])

            elif report_type == "Transaction Record":
                headers = ["Date", "Particular", "Amount", "Type", "Classification"]
                data = [headers]
                cursor.execute("SELECT * FROM transactions WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?", (month, year))
                entries = cursor.fetchall()
                for row in entries:
                    data.append([row[1], row[2], row[3], row[4], row[5]])

            conn.close()

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0D47A1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E3F2FD")),
            ]))

            elements.append(table)
            pdf.build(elements)

            self.show_snack_bar(f"PDF saved to: {file_path}", "green")

        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", "red")

    def show_snack_bar(self, message, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(message, size=14), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()