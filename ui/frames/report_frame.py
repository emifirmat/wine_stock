"""
Classes related with the report section
"""
import csv
import customtkinter as ctk
import tkinter.messagebox as messagebox
import xlsxwriter
from datetime import datetime

from helpers import deep_getattr
from ui.components import Card, ToggleInput
from ui.style import Colours, Fonts
from db.models import StockMovement, Wine

class ReportFrame(ctk.CTkScrollableFrame):
    """
    Contains all components and logic related to the report section.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
        ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            corner_radius=10,
            border_color=Colours.BORDERS,
            border_width=1
        )
        # DB
        self.session = session
        # Variables
        self.export_format = ctk.StringVar(value="csv")
        # UI
        self.create_components()

    def create_components(self) -> None:
        """
        Creates all UI components for the report section.
        """
        # Title
        title = ctk.CTkLabel(
            self,
            text="REPORTS",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(pady=(20, 0))

        # Intro Text
        text = (
            "Generate and review reports of your sales, purchases and stock. "
            + "You can export data in CSV or Excel format."
        )
        introduction = ctk.CTkLabel(
            self,
            text=text,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(pady=15)

        # == Export format toggle ==
        toggle_export = ToggleInput(
            self,
            label_text="Export Format",
            variable=self.export_format,
            item_list = [("CSV", "csv"), ("Excel", "xlsx")],
            fg_color="transparent",
            optional=True,
        )
        toggle_export.pack(pady=10)
        toggle_export.set_label_layout(60)

        # ==Cards frame==
        # Container
        frame_cards = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=10,
        )
        frame_cards.pack(pady=15)
        
        # Cards
        card_specs = [
            ("Purchases and \nSales Report", "assets/cards/full_report.png", None),
            ("Sales Report", "assets/cards/sales_report.png", "sale"),
            ("Purchases \nReport", "assets/cards/purchases_report.png", "purchase"),
            ("Wines \nReport", "assets/cards/wines_report.png", "wine"),
        ]
        for i, (title, image, filter_type) in enumerate(card_specs):
            Card(
                frame_cards,
                image_path=image,
                title=title,
                on_click=(lambda f=filter_type: self.generate_report(f))
            ).grid(row=i // 2, column=i % 2, padx=(0, 20), pady=(0, 15))

    def generate_report(self, filter_type: str | None = None) -> None:
        """
        Generate a CSV or Excel report of wine or stock movements.
        
        Inputs:
            - filter_type: One of 'wine', 'sale', or 'purchase'. No filter_type
            means a full movements report.
            
        """
        file_ext = self.export_format.get()
        file_type = "CSV" if file_ext == "csv" else "Excel"

        # Choose file destination
        file_path = ctk.filedialog.asksaveasfilename(
            defaultextension=f".{file_ext}",
            filetypes=[(f"{file_type} files", f"*.{file_ext}"), ("All files", "*.*")],
            title=f"Save {(filter_type.title() + "s") if filter_type else "Full"} Report"
        )
        if not file_path:
            return
        
        # Get data
        ws_title, field_names, attribute_names, data_list = self._get_data_config(filter_type)
      
        # Write on a new file
        if file_ext == "csv":
            self._write_csv(file_path, field_names, attribute_names, data_list)
        elif file_ext == "xlsx":
            self._write_excel(file_path, ws_title, field_names, attribute_names, data_list)
        else:
            raise ValueError("Wrong file extension.")
        
        # Show success message
        messagebox.showinfo(
            "Report Generated",
            "The report has been successfully created."
        )

        
    def _get_data_config(self, filter_type: str | None):
        """
        Returns worksheet title, headers, attributes, and queryset.
        """
        if filter_type == "wine":
            return (
                "Wine",
                (
                    "code", "name", "winery", "colour", "style",
                    "varietal", "vintage_year", "origin", "quantity",
                    "purchase_price", "selling_price"
                ),
                (
                    "code", "name", "winery", "colour.name", "style.name",
                    "varietal_display", "vintage_year", "origin_display",
                    "quantity", "purchase_price", "selling_price"
                ),
                Wine.all_ordered(self.session, order_by="code")
            )
        else: # StockMovements
            return (
                "Movements",
                (
                    "datetime", "wine_name", "wine_code", "transaction_type",
                    "quantity", "price", "subtotal"
                ),
                (
                    "datetime", "wine.name", "wine.code", "transaction_type",
                    "quantity", "price", "subtotal"
                ),
                StockMovement.all_ordered_by_datetime(self.session, filter=filter_type)
            )

    def _write_csv(
        self, file_path: str, field_names: list[str], attribute_names: list[str], 
        data_list
    ) -> None:
        """
        Write report to CSV file.
        Parameters:
            - file_path: Location of the field to write.
            - field_names: List of column names/headers.
            - attribute_names: List of attribute names used to get the field values.
            - data_list: List of a class table containing the datafield values.
        """
        with open(file_path, newline="", mode="w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()

            # Write rows
            for data_row in data_list:
                row = {}
                for field, attr_name in zip(field_names, attribute_names):
                    value = deep_getattr(data_row, attr_name)

                    if field == "subtotal":
                        value = data_row.quantity * data_row.price
                    elif field == "datetime" and isinstance(value, datetime):
                        # Remove microseconds
                        value = value.replace(microsecond=0).isoformat(sep=" ")

                    row[field] = value

                writer.writerow(row)

    def _write_excel(
        self, file_path: str, ws_title: str, field_names: list[str], 
        attribute_names: list[str], data_list
    ) -> None:
        """
        Write report to Excel file.
        Parameters:
            - file_path: Location of the field to write.
            - ws_title: Title of the excel worksheet.
            - field_names: List of column names/headers.
            - attribute_names: List of attribute names used to get the field values.
            - data_list: List of a class table containing the datafield values.
        """
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet(ws_title)

        # Formats
        header_fmt = workbook.add_format({"bold": True, "border": 1})
        date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})
        money_fmt = workbook.add_format({"num_format": "€ 0.00"})

        # Write headers
        col_widths = []
        for col, title in enumerate(field_names):
            worksheet.write(0, col, title, header_fmt)
            col_widths.append(len(title))

        # Write content
        for row_idx, data_row in enumerate(data_list, start=1):
            for col_idx, (field, attr_name) in enumerate(zip(field_names, attribute_names)):
                value = (
                    deep_getattr(data_row, attr_name) 
                    if field != "subtotal" 
                    else data_row.quantity * data_row.price
                )

                if field == "datetime":
                    worksheet.write_datetime(row_idx, col_idx, value, date_fmt)
                    display_value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif "price" in field or field == "subtotal":
                    worksheet.write_number(row_idx, col_idx, value, money_fmt)
                    display_value = f"€ {value:,.2f}"
                else:
                    worksheet.write(row_idx, col_idx, value)
                    display_value = str(value)
                
                # Track maximum width
                col_widths[col_idx] = max(col_widths[col_idx], len(display_value))

        # Adjust column widths based on content + padding
        for i, width in enumerate(col_widths):
            worksheet.set_column(i, i, width + 1)     

        workbook.close()