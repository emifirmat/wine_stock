"""
Transaction management form with filtering and table display.

This module provides a form for viewing, filtering, editing, and deleting
stock movement transactions. Combines a filterable table with a collapsible
filter panel.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session

from ui.forms.filters import TransactionFiltersForm
from ui.style import Colours, Fonts, Spacing
from ui.tables.transactions_table import TransactionsTable
from db.models import StockMovement

class ManageTransactionForm(ctk.CTkFrame):
    """
     Transaction management form with filtering capabilities.
    
    Displays a table of all stock movements (sales and purchases) with
    collapsible filters for narrowing down the displayed transactions.
    """
    def __init__(self, root: ctk.CTkFrame, session: Session, **kwargs):
        """
        Initialize transaction management form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color=Colours.BG_SECONDARY, height=500)
        
        # DB instances
        self.session = session

        # Add components
        self.transactions_table = None
        self.filters_form = None
        self.create_components()

    def create_components(self) -> None:
        """
        Create and position filters form and transactions table.
        """
        # Configure grid responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
    
        # Create transactions table
        self.transactions_table = TransactionsTable(
            self,
            self.session,
            headers=[
                "datetime", "wine name", "wine code", "transaction", "quantity",
                "price", "subtotal", "actions"
            ],
            lines=StockMovement.all_ordered_by_datetime(self.session)
        )
        self.transactions_table.grid(
            row=1, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="nsew"
        )

        # Create filters form
        self.filters_form = TransactionFiltersForm(
            self,
            self.session,
            filtered_table=self.transactions_table
        )
        self.filters_form.grid(
            row=0, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="we"
        )