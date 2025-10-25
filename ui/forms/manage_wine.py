"""
Form that contain the inputs and methods to add a new sale
"""
import customtkinter as ctk
from datetime import datetime, timedelta
import tkinter as tk
import tkinter.messagebox as messagebox
from decimal import Decimal

from ui.components import (IntInput, DropdownInput, DoubleLabel, AutocompleteInput,
    ClearSaveButtons, DateInput, LabelWithBorder)
from ui.forms.filters import WineFiltersForm
from ui.style import Colours, Fonts
from ui.tables.wines_table import WinesTable
from db.models import Wine, Colour, Style, Varietal

class ManageWineForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to show wines details.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
        ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(fg_color=Colours.BG_SECONDARY, height=500)
        
        # Include db instances
        self.session = session

        # Add components
        self.wines_table = None
        self.filters_form = None
        self.create_components()

    def create_components(self) -> list:
        """
        Create the filters and table.

        Returns:
            A list containing all the created filters in the form.
        """
        self.grid_columnconfigure(0, weight=1)

        # ==Alert Label==
        self.alert_label = LabelWithBorder(
            self,
            text="",
            text_color=Colours.PRIMARY_WINE,
            fg_color=Colours.BG_ALERT,
            border_width=1,
            border_color=Colours.ERROR,
            font=Fonts.TEXT_LABEL
        )
        self.update_alert_label()

        # ==Table section==
        self.wines_table = WinesTable(
            self,
            self.session,
            headers=[
                "code", "picture", "name", "vintage year", "origin", "quantity",
                "min. stock", "purchase price", "selling price", "actions"
            ],
            lines=Wine.all_ordered(self.session, order_by="code")
        )
        self.wines_table.grid(row=2, column=0, pady=(10, 20), sticky="nsew")

        # ==Filters section==
        # Should be after wines table as the filter needs its reference.
        self.filters_form = WineFiltersForm(
            self,
            self.session,
            filtered_table=self.wines_table
        )

        self.filters_form.grid(row=0, column=0, pady=(10, 20), sticky="we")

    def update_alert_label(self):
        """
        Checks how many wines are under stock and updates the message.
        """
        # Get wines below min stock
        low_stock_wines = [
            wine for wine in self.session.query(Wine).all() 
            if wine.is_below_min_stock
        ]
        low_stock_count = len(low_stock_wines)
        
        # If no low stock, hide alert_label
        if low_stock_count == 0:
            self.alert_label.grid_forget()
        # Update message of alert
        else:
            if low_stock_count == 1:
                words = ["is", "wine"]
            else:
                words = ["are", "wines"]
        
            self.alert_label.update_text(
                text=f"There {words[0]} {low_stock_count} {words[1]} under the minimum stock.",
            )
            self.alert_label.grid(row=1, column=0, pady=(10, 20), sticky="nsew")
