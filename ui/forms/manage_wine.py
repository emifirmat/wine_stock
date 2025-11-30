"""
Wine management form with filtering and table display.

This module provides a form for viewing, filtering, editing, and managing
wines in the catalog. Includes low stock alerts, filterable table, and
collapsible filter panel.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session

from ui.components import LabelWithBorder
from ui.forms.filters import WineFiltersForm
from ui.style import Colours, Fonts, Spacing
from ui.tables.wines_table import WinesTable
from db.models import Wine


class ManageWineForm(ctk.CTkFrame):
    """
    Wine management form with filtering and alerts.
    
    Displays a table of all wines with collapsible filters and a low stock
    alert banner that shows when wines fall below minimum stock levels.
    """
    def __init__(self, root: ctk.CTkFrame, session: Session, **kwargs):
        """
        Initialize wine management form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color=Colours.BG_SECONDARY)
        
        # DB instances
        self.session = session

        # Components
        self.alert_label = None
        self.wines_table = None
        self.filters_form = None
        self.create_components()

    def create_components(self) -> None:
        """
        Create and position alert label, filters form, and wines table.
        """
        # Configure grid responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create low stock alert label (initially hidden)
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

        # Create wines table
        self.wines_table = WinesTable(
            self,
            self.session,
            headers=[
                "code", "picture", "name", "vintage year", "origin", "qty.",
                "min. stock", "purchase price", "selling price", "actions"
            ],
            lines=Wine.all_ordered(self.session, order_by="code")
        )
        self.wines_table.grid(
            row=2, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="nsew"
        )

        # Create filters form
        # Should be after wines table as the filter needs its reference.
        self.filters_form = WineFiltersForm(
            self,
            self.session,
            filtered_table=self.wines_table
        )
        self.filters_form.grid(
            row=0, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="we"
        )

    def update_alert_label(self) -> None:
        """
        Update low stock alert banner with current count.
        
        Shows alert when wines are below minimum stock, hides when all
        wines have adequate stock. Updates message to use proper grammar
        for singular/plural counts.
        """
        # Get wines below min stock
        low_stock_wines = [
            wine for wine in self.session.query(Wine).all() 
            if wine.is_below_min_stock
        ]
        low_stock_count = len(low_stock_wines)
        
        # Hide alert if no low stock wines
        if low_stock_count == 0:
            self.alert_label.grid_forget()
            return
        
        # Update alert message with proper grammar
        if low_stock_count == 1:
            verb, noun = ["is", "wine"]
        else:
            verb, noun = ["are", "wines"]
    
        self.alert_label.configure_label(
            text=f"There {verb} {low_stock_count} {noun} under the minimum stock.",
        )
        self.alert_label.grid(
            row=1, column=0, 
            padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y, sticky="nsew"
        )
