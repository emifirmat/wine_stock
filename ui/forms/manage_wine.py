"""
Form that contain the inputs and methods to add a new sale
"""
import customtkinter as ctk
from datetime import datetime, timedelta
import tkinter as tk
import tkinter.messagebox as messagebox
from decimal import Decimal

from ui.components import (IntInput, DropdownInput, DoubleLabel, AutocompleteInput,
    ClearSaveButtons, DateInput)
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

        # ==Table section==
        self.wines_table = WinesTable(
            self,
            self.session,
            headers=[
                "code", "picture", "name", "vintage year", "origin", "quantity",
                "purchase price", "selling price", "actions"
            ],
            lines=Wine.all_ordered(self.session, order_by="code")
        )
        self.wines_table.grid(row=1, column=0, pady=(10, 20), sticky="nsew")

        # ==Filters section==
        # Should be after wines table as the filter needs its reference.
        self.filters_form = WineFiltersForm(
            self,
            self.session,
            filtered_table=self.wines_table
        )

        self.filters_form.grid(row=0, column=0, pady=(10, 20), sticky="we")