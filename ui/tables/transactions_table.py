"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from datetime import datetime
from decimal import Decimal
from PIL import Image

from ui.components import (TextInput, IntInput, Card, DropdownInput, ImageInput,
    DoubleLabel)
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine, Colour, Style, StockMovement

class MovementsTable(ctk.CTkScrollableFrame):
    """
    Contains the components of the table with the wine purchases and sellings.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, headers: list[str], lines: int, **kwargs
        ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(
            fg_color=Colours.BG_MAIN,
            scrollbar_button_color=Colours.BG_HOVER_NAV,
            height=500
        )
        
        # Include db instances
        self.session = session

        # Table data
        self.headers = headers
        self.lines = lines

        # Add components
        self.create_components()

    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==Add Components==
        # headers
        row_header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        row_header_frame.pack(fill="x", pady=2)
        widths = [100, 200, 100, 120, 80, 80, 100]
        for i, (header, width) in enumerate(zip(self.headers, widths)):
            label = ctk.CTkLabel(
                row_header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=width,
            )
            label.grid(row=0, column=i, padx=5)

        # Movements
        for line in self.lines: 
            row_frame = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )
            row_frame.pack(fill="x", pady=2)

            # Columns
            label_datetime = ctk.CTkLabel(
                row_frame, 
                text=line.datetime.replace(microsecond=0),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
                wraplength=100,
            )
            label_wine_name = ctk.CTkLabel(
                row_frame, 
                text=line.wine.name,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=200,
                wraplength=200,
            )
            label_wine_code = ctk.CTkLabel(
                row_frame, 
                text=line.wine.code,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
            )
            label_transaction = ctk.CTkLabel(
                row_frame, 
                text=line.transaction_type.capitalize(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=120,
            )
            label_quantity = ctk.CTkLabel(
                row_frame, 
                text=line.quantity,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=80,
            )
            label_price = ctk.CTkLabel(
                row_frame, 
                text=f"€ {line.price}",
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=80,
            )
            label_subtotal = ctk.CTkLabel(
                row_frame, 
                text=f"€ {line.quantity * line.price}",
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
            )

            label_datetime.grid(row=0, column=0, padx=5)
            label_wine_name.grid(row=0, column=1, padx=5)
            label_wine_code.grid(row=0, column=2, padx=5)
            label_transaction.grid(row=0, column=3, padx=5)
            label_quantity.grid(row=0, column=4, padx=5)
            label_price.grid(row=0, column=5, padx=5)
            label_subtotal.grid(row=0, column=6, padx=5)
            
            # Remove Button
            remove_button = ctk.CTkButton(
                row_frame,
                text="X",
                fg_color=Colours.BTN_CLEAR,
                text_color=Colours.TEXT_BUTTON,
                hover_color=Colours.BG_HOVER_BTN_CLEAR,
                width=30,
                cursor="hand2",
                command=lambda f=row_frame, l=line: self.remove_line(f, l) # Pass f, l to get the current value and not last one.
            )
            remove_button.grid(row=0, column=7, padx=5)

    def remove_line(self, parent_frame, instance) -> None:
        """
        Removes the line where the button that triggered the event was clicked
        """
        # Ask user for confirmation
        confirm_dialog = messagebox.askyesno(
            "Confirm Removal",
            (f"Do you want to remove the {instance.transaction_type} for € " 
            + f"{instance.quantity * instance.price}?")
        )
        if not confirm_dialog:
            return

        # Remove line from db
        self.session.delete(instance)
        self.session.commit()
        
        # Remove line from UI
        parent_frame.destroy()

        # Notify removal
        messagebox.showinfo(
            "Transaction Removed",
            "The transaction has been removed."
        )
    

        