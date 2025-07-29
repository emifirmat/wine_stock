"""
Classes related with the home section
"""
import customtkinter as ctk
from PIL import Image

from ui.components import TextInput, ImageInput, Card
from ui.forms.add_sale import AddSaleForm
from ui.forms.add_purchase import AddPurchaseForm
from ui.style import Colours, Fonts, Icons

from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop

class HomeFrame(ctk.CTkFrame):
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

        # Warning Text
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

        # Place cards
        card_new_sale.grid(row=0, column=0, pady=(0, 15))
        card_new_purchase.grid(row=0, column=1, pady=(0, 15), padx=20)
    

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
