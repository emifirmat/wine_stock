"""
Classes related with the home section
"""
import customtkinter as ctk

from ui.components import Card, ButtonGoBack
from ui.forms.add_transaction import AddTransactionForm
from ui.tables.transactions_table import MovementsTable
from ui.style import Colours, Fonts, Icons

from models import Wine,StockMovement

class HomeFrame(ctk.CTkScrollableFrame):
    """
    It contains all the components and logic related to home section
    """
    def __init__(
            self, root: ctk.CTkFrame, session, main_window, **kwargs
        ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            corner_radius=10,
            border_color=Colours.BORDERS,
            border_width=1,
        )
        
        self.session = session
        self.wine_list = self.session.query(Wine).all()
        self.main_window = main_window
        self.button_go_back = None

        self.create_components()

    def create_components(self) -> None:
        """
        Creates the home section components
        """
        # Title
        title = ctk.CTkLabel(
            self,
            text="HOME",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(pady=(20, 0))

        if not self.wine_list:
            # Warning Text
            text = "Add at least one wine to enable and view this section."
            
            warning_text = ctk.CTkLabel(
                self,
                text=text,
                text_color=Colours.TEXT_MAIN,
                justify="center",
                font=Fonts.TEXT_MAIN
            )
            warning_text.pack(pady=150)
            
            # Stop generating components
            return
        
        # Introduction Text
        text = (
            "Add and track wine sales and purchases to keep a clear record of "
            + "your winery's transactions."
        )
        introduction = ctk.CTkLabel(
            self,
            text=text,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(pady=15)

        # ==Frame cards==
        frame_cards = ctk.CTkFrame(
            self,
            fg_color = "transparent",
            corner_radius=10,
        )
        frame_cards.pack(pady=15)
        # New sale
        card_new_sale = Card(
            frame_cards,
            image_path="assets/cards/add_sale.png",
            title= "New Sale",
            on_click=self.show_add_sale_section,
        )
        # New purhase
        card_new_purchase = Card(
            frame_cards,
            image_path="assets/cards/add_purchase.png",
            title="New Purchase",
            on_click=self.show_add_purchase_section,
        )
        # New purhase
        card_remove_transaction = Card(
            frame_cards,
            image_path="assets/cards/remove_transaction.png",
            title= "Remove \nTransaction",
            on_click=self.show_remove_transaction_section,
        )

        # Place cards
        card_new_sale.grid(row=0, column=0, pady=(0, 15))
        card_new_purchase.grid(row=0, column=1, pady=(0, 15), padx=20)
        card_remove_transaction.grid(row=1, column=0, pady=(0, 15))
    
    def show_subsection(self, text_title: str, form_class, **kwargs):
        """
        Clears body and display a subsection.
        Parameters:
            - text_title: Title of the section
            - form_class: Form to be displayed
            - kwargs: Additional arguments from the forms
        """
        # Clear displayed section
        self.clear_content()

        # Set up window expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add Go back button
        self.button_go_back = ButtonGoBack(
            self.main_window.root,
            command=self.main_window.show_home_section
        )

        # Add title
        title = ctk.CTkLabel(
            self,
            text=text_title,
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )

        # Place button and title
        x = self.winfo_rootx() - self.main_window.root.winfo_rootx()
        y = self.winfo_rooty() - self.main_window.root.winfo_rooty()
        
        self.button_go_back.place(x=x, y=y)
        title.grid(row=0, column=0, pady=(20, 0), sticky="nsew") 

        # Add form
        form = form_class(
            self,
            self.session,
            **kwargs
        )
        form.grid(row=1, column=0, pady=(10, 0), sticky="nsew") # Cannot use pack for layout expansion reasons

    def show_add_sale_section(self) -> None:
        """
        Shows the form for adding a sale.
        """
        self.show_subsection(
            "NEW SALE", 
            AddTransactionForm, 
            transaction_type="sale"
        )

    def show_add_purchase_section(self) -> None:
        """
        Shows the form for adding a new purchase.
        """
        self.show_subsection(
            "NEW PURCHASE", 
            AddTransactionForm,
            transaction_type="purchase",
        )

    def show_remove_transaction_section(self) -> None:
        """
        Shows the form for removing a transaction.
        """
        self.show_subsection(
            "REMOVE TRANSACTION",
            MovementsTable, 
            headers=[
                "datetime", "wine name", "wine code", "transaction", "quantity",
                "price", "subtotal"
            ],
            lines=StockMovement.all_ordered(self.session)
        )

    def clear_content(self) -> None:
        """
        Removes any content in home frame
        """
        for component in self.winfo_children():
            component.destroy()

    def destroy(self) -> None:
        """
        Override function to include the destruction of the button go back.
        """
        if self.button_go_back:
            self.button_go_back.destroy()
        super().destroy()

