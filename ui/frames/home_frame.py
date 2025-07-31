"""
Classes related with the home section
"""
import customtkinter as ctk
from PIL import Image

from ui.components import TextInput, ImageInput, Card
from ui.forms.add_sale import AddSaleForm
from ui.forms.add_purchase import AddPurchaseForm
from ui.tables.transactions_table import MovementsTable
from ui.style import Colours, Fonts, Icons

from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine,StockMovement

class HomeFrame(ctk.CTkScrollableFrame):
    """
    It contains all the components and logic related to home section
    """
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
        ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            corner_radius=10,
            border_color=Colours.BORDERS,
            border_width=1
        )
        
        self.session = session
        self.wine_list = self.session.query(Wine).all()

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
            title= "New Purchase",
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
    

    def show_add_sale_section(self) -> None:
        """
        Shows the form for adding a sale.
        """
        # Clean previous menu
        self.clear_content()

        # Vertical expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add title
        title = ctk.CTkLabel(
            self,
            text="NEW SALE",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )
        title.grid(row=0, column=0, pady=(20, 0), sticky="n") # Cannot use pack for layout expansion reasons

        # Add form
        add_sale_form = AddSaleForm(
            self,
            self.session
        )
        add_sale_form.grid(row=1, column=0, pady=(10, 0), sticky="nsew") # Cannot use pack for layout expansion reasons

    def show_add_purchase_section(self) -> None:
        """
        Shows the form for adding a new purchase.
        """
        # Clean previous menu
        self.clear_content()

        # Vertical expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add title
        title = ctk.CTkLabel(
            self,
            text="NEW PURCHASE",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )
        title.grid(row=0, column=0, pady=(20, 0), sticky="n") # Cannot use pack for layout expansion reasons

        # Add form
        add_purchase_form = AddPurchaseForm(
            self,
            self.session
        )
        add_purchase_form.grid(row=1, column=0, pady=(10, 0), sticky="nsew") # Cannot use pack for layout expansion reasons

    def clear_content(self) -> None:
        """
        Removes any content in home frame
        """
        for component in self.winfo_children():
            component.destroy()

    def show_remove_transaction_section(self) -> None:
        """
        Shows the form for removing a transaction.
        """
        # Clean previous menu
        self.clear_content()

        # Vertical expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add title
        title = ctk.CTkLabel(
            self,
            text="REMOVE TRANSACTION",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )
        title.grid(row=0, column=0, pady=(20, 0), sticky="n") # Cannot use pack for layout expansion reasons

        # Add form
        movements_table = MovementsTable(
            self,
            self.session,
            headers=[
                "datetime", "wine name", "wine code", "transaction", "quantity",
                "price", "subtotal"
            ],
            lines=StockMovement.all_ordered(self.session)
        )
        movements_table.grid(row=1, column=0, pady=(10, 0), sticky="nsew") # Cannot use pack for layout expansion reasons


