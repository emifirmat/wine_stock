"""
Classes related with the price section
"""
import csv
import customtkinter as ctk
from PIL import Image

from ui.components import TextInput, ImageInput, Card
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, StockMovement

class ReportFrame(ctk.CTkScrollableFrame):
    """
    It contains all the components and logic related to report section
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
        self.session = session

        self.create_components()

    def create_components(self) -> None:
        """
        Creates the report section components
        """
        # Title
        title = ctk.CTkLabel(
            self,
            text="REPORTS",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(pady=(20, 0))

        # Introduction Text
        text = (
            "Generate and review sales and purchase CSV reports to maintain a clear "
            + "overview of your winery's transaction history."
        )
        introduction = ctk.CTkLabel(
            self,
            text=text,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(pady=15)

        # ==Frame cards==
        frame_cards = ctk.CTkFrame(
            self,
            fg_color = "transparent",
            corner_radius=10,
        )
        frame_cards.pack(pady=15)
        # Full report (Both sales and purchases)
        card_full_report = Card(
            frame_cards,
            image_path="assets/cards/full_report.png",
            title= "Purchases and \nSales Report",
            on_click=self.generate_csv_report,
        )
        # Sales report
        card_sales_report = Card(
            frame_cards,
            image_path="assets/cards/sales_report.png",
            title= "Sales Report",
            on_click=lambda: self.generate_csv_report("sale"),
        )
        # Purchases report
        card_purchases_report = Card(
            frame_cards,
            image_path="assets/cards/purchases_report.png",
            title= "Purchases \nReport",
            on_click=lambda: self.generate_csv_report("purchase"),
        )

        # Place cards
        card_full_report.grid(row=0, column=0, pady=(0, 15))
        card_sales_report.grid(row=0, column=1, pady=(0, 15), padx=20)
        card_purchases_report.grid(row=1, column=0, pady=(0, 15))

    def generate_csv_report(self, filter: str | None = None) -> None:
        """
        Generate a csv report with stock_movements based on the selected mode.
        
        Inputs:
            filter: Options are ""sale" and "purchase". Used to filter
            the stock movements.
        """
        # Select location of the file to write
        file_path = ctk.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title=f"Save CSV {filter or "Full"} Report"
        )
        if not file_path:
            return
        
        # Prepare headers
        fieldnames = ("datetime", "wine_name", "wine_code", "transaction",
        "quantity", "price", "subtotal")

        row = {}

        # Get stock mov list
        stock_mov_list = StockMovement.all_ordered(self.session, filter)
        
        # Write on a new file
        with open(file_path, newline="", mode="w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for movement in stock_mov_list:
                row["datetime"] = movement.datetime
                row["wine_name"] = movement.wine.name
                row["wine_code"] = movement.wine.code
                row["transaction"] = movement.transaction_type
                row["quantity"] = movement.quantity
                row["price"] = f"€ {movement.price}"
                row["subtotal"] = f"€ {movement.quantity * movement.price}"

                writer.writerow(row)
        

               

            