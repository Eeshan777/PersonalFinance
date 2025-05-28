import flet as ft
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

class DownloadPDF:
    def __init__(self, page, view: ft.View):
        self.page = page
        self.view = view
        self.view.title = "Download PDF"
        self.view.bgcolor = "#E3F2FD"

        field_width = 360

        self.date_picker = ft.DatePicker(on_change=self.update_date_field)
        self.page.overlay.append(self.date_picker)

        self.date_field = ft.TextField(
            label="Select Month/Year",
            width=field_width,
            read_only=True,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            suffix=ft.IconButton(icon="calendar_month", on_click=lambda e: self.date_picker.pick_date()),
            on_submit=lambda e: self.report_type_dropdown.focus()
        )

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

        self.generate_button = ft.ElevatedButton(
            "Generate PDF",
            width=field_width,
            bgcolor="#1565C0",
            color="white",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            on_click=self.generate_pdf
        )

        self.pdf_message = ft.Container(
            bgcolor="white",
            padding=15,
            border_radius=15,
            height=240,
            width=780,
            border=ft.border.all(1, "#90CAF9"),
            content=ft.Text("PDF will be saved to the app directory.", size=14),
            alignment=ft.alignment.top_left
        )

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
        ], spacing=15)

        self.main_layout = ft.Column([
            self.header,
            ft.Column(
                [
                    self.form_column,
                    self.pdf_message
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.view.controls.clear()
        self.view.controls.append(self.main_layout)

    def go_back(self, e):
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.update()

    def update_date_field(self, e):
        if self.date_picker.value:
            self.date_field.value = self.date_picker.value.strftime("%m/%Y")
            self.report_type_dropdown.focus()
            self.page.update()

    def generate_pdf(self, e):
        report_type = self.report_type_dropdown.value
        month_year = self.date_field.value

        if not report_type or not month_year:
            self.show_snack_bar("Please select report type and date.", "red")
            return

        filename = f"{report_type.lower().replace(' ', '_')}_report.pdf"
        pdf = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            if report_type == "Interest Calculator":
                headers = ["Deposit Date", "Maturity Date", "Deposit Type", "Amount", "Interest Rate", "Time", "Maturity"]
                data = [headers]
                cursor.execute("SELECT * FROM interest_calculations WHERE strftime('%m/%Y', deposit_date) = ?", (month_year,))
                entries = cursor.fetchall()
                for row in entries:
                    data.append([row[1], row[2], row[7], row[3], row[4], row[5], row[6]])

            elif report_type == "Transaction Record":
                headers = ["Date", "Particular", "Amount", "Type", "Classification"]
                data = [headers]
                cursor.execute("SELECT * FROM transactions WHERE strftime('%m/%Y', date) = ?", (month_year,))
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

            self.show_snack_bar(f"PDF '{filename}' generated successfully.", "green")

        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", "red")

    def show_snack_bar(self, message, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(message, size=14), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()