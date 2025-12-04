"""
Home section frame and navigation.

This module defines the home section where users can add sales, purchases,
and manage transactions. It provides a card-based interface for quick access
to transaction operations.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from typing import Callable

from helpers import get_system_scale
from ui.components import Card, ButtonGoBack, AutoScrollFrame
from ui.forms.add_edit_transaction import AddTransactionForm
from ui.forms.manage_transaction import ManageTransactionForm
from ui.style import Colours, Fonts, Spacing, Rounding

from db.models import Wine


class HomeFrame(AutoScrollFrame):
    """
    Home section frame with transaction management interface.
    
    Displays cards for adding sales, purchases, and managing transactions.
    Shows a prompt to add wines first if the database is empty.
    """
    def __init__(
        self, root: ctk.CTkFrame, session: Session, on_header_update: Callable, **kwargs
    ):
        """
        Initialise the home frame with transaction cards.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            on_header_update: Callback to update the main window header
            **kwargs: Additional keyword arguments for AutoScrollFrame
        """
        super().__init__(root, **kwargs)
        self.inner.configure(**kwargs)
        self.canvas.configure(bg=kwargs["fg_color"])
        
        # DB instances
        self.session = session
        self.wine_list = self.session.query(Wine).all()
        
        # Callbacks
        self.on_header_update = on_header_update
        
        # Components
        self.create_components()

    def create_components(self) -> None:
        """
        Create and display home section components.
        
        Shows either an empty state message if no wines exist, or the
        transaction management cards if wines are available.
        """
        # Show empty state if no wines exist
        if not self.wine_list:
            text = "Add at least one wine to enable and view this section."
            
            no_wine_text = ctk.CTkLabel(
                self.inner,
                text=text,
                text_color=Colours.TEXT_MAIN,
                justify="center",
                font=Fonts.TEXT_MAIN
            )
            no_wine_text.pack(
                padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y,
            )
            
            return
        
        # Create cards container
        frame_cards = ctk.CTkFrame(
            self.inner,
            fg_color="transparent",
            corner_radius=Rounding.CARD,
        )
        frame_cards.pack(padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y)

        # Create transaction cards
        card_new_sale = Card(
            frame_cards,
            image_path="assets/cards/add_sale.png",
            title= "New Sale",
            on_click=self.show_add_sale_section,
        )
        card_new_purchase = Card(
            frame_cards,
            image_path="assets/cards/add_purchase.png",
            title="New Purchase",
            on_click=self.show_add_purchase_section,
        )
        card_manage_transaction = Card(
            frame_cards,
            image_path="assets/cards/manage_transaction.png",
            title= "Manage \nTransaction",
            on_click=self.show_manage_transaction_section,
        )

        # Position cards in grid
        card_new_sale.grid(
            row=0, column=0, padx=Spacing.CARD_X, pady=Spacing.CARD_Y
        )
        card_new_purchase.grid(
            row=0, column=1, padx=Spacing.CARD_X, pady=Spacing.CARD_Y
        )
        card_manage_transaction.grid(
            row=1, column=0, padx=Spacing.CARD_X, pady=Spacing.CARD_Y
        )

        # Note: ScrollableFrames can't expand vertically due to internal design.
        # Horizontal expansion for cards doesn't look aesthetically pleasing.

    
    def show_subsection(
        self, text_title: str, form_class: ctk.CTkFrame, **kwargs
    ) -> None:
        """
        Clear content and display a transaction form subsection.
        
        Parameters:
            text_title: Title displayed at the top of the subsection
            form_class: Form class to instantiate and display
            **kwargs: Additional keyword arguments passed to the form constructor
        """
        # Clear current content
        self.clear_content()
        
        # Update header frame
        self.on_header_update(title=text_title, introduction="", back_to="home")

        # Configure grid expansion
        self.inner.grid_rowconfigure(1, weight=1)
        self.inner.grid_columnconfigure(0, weight=1)

        # Create and position form
        form = form_class(
            self.inner,
            session=self.session,
            **kwargs
        )
        form.grid(
            row=1, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="nsew"
        ) 

    def show_add_sale_section(self) -> None:
        """
        Display the form for adding a new sale transaction.
        """
        self.show_subsection(
            "NEW SALE", 
            AddTransactionForm, 
            transaction_type="sale"
        )

    def show_add_purchase_section(self) -> None:
        """
        Display the form for adding a new purchase transaction.
        """
        self.show_subsection(
            "NEW PURCHASE", 
            AddTransactionForm,
            transaction_type="purchase",
        )

    def show_manage_transaction_section(self) -> None:
        """
        Display the form for viewing and removing transactions.
        """
        self.show_subsection(
            "MANAGE TRANSACTION",
            ManageTransactionForm, 
        )

    def clear_content(self) -> None:
        """
        Remove all widgets from the home frame.
        """
        for component in self.inner.winfo_children():
            component.destroy()