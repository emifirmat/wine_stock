"""
Wine section frame and CRUD operations.

This module defines the wine section where users can add, edit, and manage
wines in the catalog. It provides a card-based interface for quick access
to wine management operations.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session

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
        self, root: ctk.CTkFrame, session: Session, main_window, **kwargs
    ):
        """
        Initialize the wine frame with management cards.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            main_window: Reference to MainWindow for navigation
            **kwargs: Additional keyword arguments for CTkScrollableFrame
        """
        super().__init__(root, **kwargs)
        self.inner.configure(**kwargs)
        self.canvas.configure(bg=kwargs["fg_color"])

        # DB instances
        self.session = session
        self.wine = session.query(Wine)
        
        # Widget references
        self.main_window = main_window
        self.button_go_back = None
        
        # Components
        self.create_components()
        
    def create_components(self) -> None:
        """
        Create and display wine section components (title, intro, cards).
        """
        # Create title
        title = ctk.CTkLabel(
            self.inner,
            text="WINES",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(padx=Spacing.TITLE_X, pady=Spacing.TITLE_Y)

        # Create introduction text
        text_intro = (
            "Add, edit, or remove wines from your winery's catalog to keep "
            "your selection up to date."
        )
        introduction = ctk.CTkLabel(
            self.inner,
            text=text_intro,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y)
        
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
        
    
    def show_subsection(self, text_title: str, form_class: type, **kwargs) -> None:
        """
        Clear content and display a wine form subsection.
        
        Parameters:
            text_title: Title displayed at the top of the subsection
            form_class: Form class to instantiate and display
            **kwargs: Additional keyword arguments passed to the form constructor
        """
        # Clean current content
        self.clear_content()

        # Configure grid expansion
        self.inner.grid_rowconfigure(1, weight=1)
        self.inner.grid_columnconfigure(0, weight=1)

        # Create and position go back button
        self.button_go_back = ButtonGoBack(
            self.main_window.root,
            command=self.main_window.show_wine_section
        )
        
        x = self.winfo_rootx() - self.main_window.root.winfo_rootx()
        y = self.winfo_rooty() - self.main_window.root.winfo_rooty()
        self.button_go_back.place(x=x, y=y)

        # Create and position title
        title = ctk.CTkLabel(
            self.inner,
            text=text_title,
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )
        title.grid(
            row=0, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="n"
        )

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
        Display the form for adding a new wine.
        """
        self.show_subsection(
            "ADD WINE",
            AddWineForm
        )
    
    def manage_wine_section(self) -> None:
        """
        Display the form for managing existing wines (view, edit, delete).
        """
        self.show_subsection(
            "WINE LIST",
            ManageWineForm,
        )
    
    def clear_content(self) -> None:
        """
        Remove all widgets from the wine frame.
        """
        for component in self.inner.winfo_children():
            component.destroy()

    def destroy(self) -> None:
        """
        Destroy the frame and its go back button.
        """
        if self.button_go_back:
            self.button_go_back.destroy()
        super().destroy()

        
        