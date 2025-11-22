"""
Home section frame and navigation.

This module defines the home section where users can add sales, purchases,
and manage transactions. It provides a card-based interface for quick access
to transaction operations.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session

from ui.components import Card, ButtonGoBack
from ui.forms.add_edit_transaction import AddTransactionForm
from ui.forms.manage_transaction import ManageTransactionForm
from ui.style import Colours, Fonts, Spacing, Rounding

from db.models import Wine

class HomeFrame(ctk.CTkScrollableFrame):
    """
    Home section frame with transaction management interface.
    
    Displays cards for adding sales, purchases, and managing transactions.
    If no wines exist in the database, shows a prompt to add wines first.
    """
    def __init__(
        self, root: ctk.CTkFrame, session: Session, main_window, **kwargs
    ):
        """
        Initialize the home frame with transaction cards.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            main_window: Reference to MainWindow for navigation
            **kwargs: Additional keyword arguments for CTkScrollableFrame
        """
        super().__init__(root, **kwargs)
        
        # DB instances
        self.session = session
        self.wine_list = self.session.query(Wine).all()
        
        # Widget references
        self.main_window = main_window
        self.button_go_back = None
        
        # Components
        self.create_components()

    def create_components(self) -> None:
        """
        Create and display home section components (title, cards, or empty state).
        """
        # Create title
        title = ctk.CTkLabel(
            self,
            text="HOME",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(padx=Spacing.TITLE_X, pady=Spacing.TITLE_Y)
        
        # Show empty state if no wines exist
        if not self.wine_list:
            text = "Add at least one wine to enable and view this section."
            
            no_wine_text = ctk.CTkLabel(
                self,
                text=text,
                text_color=Colours.TEXT_MAIN,
                justify="center",
                font=Fonts.TEXT_MAIN
            )
            no_wine_text.pack(
                padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y,
            )
            
            # Stop generating components
            return
        
        # Create introduction text
        text = (
            "Add, track, and manage wine sales and purchases to stay on top of "
            "your winery's activity."
        )
        introduction = ctk.CTkLabel(
            self,
            text=text,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y)

        # ==Frame cards==
        # Create cards container
        frame_cards = ctk.CTkFrame(
            self,
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

    
    def show_subsection(self, text_title: str, form_class: type, **kwargs) -> None:
        """
        Clear content and display a transaction form subsection.
        
        Parameters:
            text_title: Title displayed at the top of the subsection
            form_class: Form class to instantiate and display
            **kwargs: Additional keyword arguments passed to the form constructor
        """
        # Clear current content
        self.clear_content()

        # Configure grid expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create and position go back button
        self.button_go_back = ButtonGoBack(
            self.main_window.root,
            command=self.main_window.show_home_section
        )

        # Create title
        title = ctk.CTkLabel(
            self,
            text=text_title,
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )

        # Position button and title
        x = self.winfo_rootx() - self.main_window.root.winfo_rootx()
        y = self.winfo_rooty() - self.main_window.root.winfo_rooty()
        
        self.button_go_back.place(x=x, y=y)
        title.grid(
            row=0, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y, sticky="nsew"
        ) 

        # Create and position form
        form = form_class(
            self,
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
        for component in self.winfo_children():
            component.destroy()

    def destroy(self) -> None:
        """
        Destroy the frame and its go back button.
        """
        if self.button_go_back:
            self.button_go_back.destroy()
        super().destroy()

