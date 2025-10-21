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
from ui.forms.filters import TransactionFiltersForm
from ui.style import Colours, Fonts
from ui.tables.transactions_table import TransactionsTable
from db.models import Wine, StockMovement

class ManageTransactionForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to remove a transaction.
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
        self.transactions_table = None
        self.filters_form = None
        self.create_components()

    def get_wine_names_dict(self) -> dict[str:int]:
        """
        Get a list of wine names with their instances.
        Returns:
            A dict of wine names with their instance as value.
        """
        wines = Wine.all_ordered(self.session)
        return {
            f"{wine.name.title()}": wine for wine in wines
        }

    def create_components(self) -> list:
        """
        Create the filters and table.

        Returns:
            A list containing all the created filters in the form.
        """
        self.grid_columnconfigure(0, weight=1)
    
        # ==Table section==
        self.transactions_table = TransactionsTable(
            self,
            self.session,
            headers=[
                "datetime", "wine name", "wine code", "transaction", "quantity",
                "price", "subtotal", "actions"
            ],
            lines=StockMovement.all_ordered_by_datetime(self.session)
        )
        self.transactions_table.grid(row=1, column=0, pady=(10, 0), sticky="nsew")

        # ==Filters section==
        self.filters_form = TransactionFiltersForm(
            self,
            self.session,
            filtered_table=self.transactions_table
        )
        self.filters_form.grid(row=0, column=0, pady=(10, 20), sticky="we")