"""
Wine section frame and CRUD operations.

This module defines the wine section where users can add, edit, and manage
wines in the catalog. It provides a card-based interface for quick access
to wine management operations.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from typing import Callable

from db.models import Wine
from ui.components import Card, ButtonGoBack, AutoScrollFrame
from ui.forms.add_edit_wine import AddWineForm
from ui.forms.manage_wine import ManageWineForm
from ui.style import Colours, Fonts, Rounding, Spacing


class WineFrame(AutoScrollFrame):
    """
    Wine section frame with CRUD interface.
    
    Displays cards for adding new wines and managing existing wine catalog.
    Provides subsection navigation for detailed wine operations.
    """
    def __init__(
        self, root: ctk.CTkFrame, session: Session, on_header_update: Callable,
        **kwargs
    ):
        """
        Initialise the wine frame with management cards.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            on_header_change: Callback to update the main window header
            **kwargs: Additional keyword arguments for AutoScrollFrame
        """
        super().__init__(root, **kwargs)
        self.inner.configure(**kwargs)
        self.canvas.configure(bg=kwargs["fg_color"])

        # DB instances
        self.session = session
        
        # Callbacks
        self.on_header_update = on_header_update
        
        # Components
        self.create_components()
        
    def create_components(self) -> None:
        """
        Create and display wine section components.
        
        Creates a card-based interface for wine management operations.
        """
        # Create cards container
        frame_cards = ctk.CTkFrame(
            self.inner,
            fg_color="transparent",
            corner_radius=Rounding.CARD,
        )
        frame_cards.pack(padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y)
        
        # Create wine management cards
        card_manage_wine = Card(
            frame_cards,
            image_path="assets/cards/wine_list.png",
            title="Manage Wine",
            on_click=self.manage_wine_section,
        )
        card_add_wine = Card(
            frame_cards,
            title="Add Wine",
            image_path="assets/cards/add_wine.png",
            on_click=self.show_add_wine_section,
        )

        # Position cards in grid
        card_manage_wine.grid(
            row=0, column=0, padx=Spacing.CARD_X, pady=Spacing.CARD_Y
        )
        card_add_wine.grid(
            row=0, column=1, padx=Spacing.CARD_X, pady=Spacing.CARD_Y
        )
    
    def show_subsection(
        self, text_title: str, form_class: ctk.CTkFrame, **kwargs
    ) -> None:
        """
        Clear content and display a wine form subsection.
        
        Parameters:
            text_title: Title displayed at the top of the subsection
            form_class: Form class to instantiate and display
            **kwargs: Additional keyword arguments passed to the form constructor
        """
        # Clear current content
        self.clear_content()

        # Update header frame
        self.on_header_update(title=text_title, introduction="", back_to="wines")

        # Configure grid expansion
        self.inner.grid_rowconfigure(1, weight=1)
        self.inner.grid_columnconfigure(0, weight=1)

        # Create and position subsection form
        form = form_class(
            self.inner,
            self.session,
            fg_color=Colours.BG_SECONDARY,
            **kwargs
        )
        form.grid(
            row=1, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="nsew"
        ) 

    def show_add_wine_section(self) -> None:
        """
        Display the form for adding a new wine to the catalog.
        """
        self.show_subsection("ADD WINE", AddWineForm)
    
    def manage_wine_section(self) -> None:
        """
        Display the form for managing existing wines (view, edit, delete).
        """
        self.show_subsection("WINE LIST", ManageWineForm)
    
    def clear_content(self) -> None:
        """
        Remove all widgets from the wine frame.
        """
        for component in self.inner.winfo_children():
            component.destroy()