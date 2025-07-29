"""
Classes related with the wine section
"""

import customtkinter as ctk
from datetime import datetime
from PIL import Image

from ui.components import TextInput, IntInput, Card, DropdownInput, ImageInput
from ui.forms.add_wine import AddWineForm
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine, Colour, Style

class WineFrame(ctk.CTkScrollableFrame):
    """
    It contains all the components and logic related to wine CRUD
    """
    def __init__(
            self, root: ctk.CTkFrame, session, on_save, **kwargs
        ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            corner_radius=10,
            border_color=Colours.BORDERS,
            border_width=1,
        )
        self.session = session
        self.wine = session.query(Wine)
        self.create_components()
        #self.on_save = on_save   IDK if i will use it (it comes from settings)
        
    def create_components(self) -> None:
        """
        Creates the wine section components
        """
        # Title
        title = ctk.CTkLabel(
            self,
            text="WINE MANAGEMENT",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(pady=(20, 0))

        # Introduction
        text_intro = (
            "Add, edit, or remove wines from your winery's catalog to "
            + "keep your selection up to date."
        )
        introduction = ctk.CTkLabel(
            self,
            text=text_intro,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(pady=15)
        
        # Frame cards
        frame_cards = ctk.CTkFrame(
            self,
            fg_color = "transparent",
            corner_radius=10,
        )
        frame_cards.pack(pady=15)
        
        card_add = Card(
            frame_cards,
            title="Add Wine",
            image_path="assets/cards/add_wine.png",
            on_click=self.show_add_wine_section,
        )
        card_edit = Card(
            frame_cards,
            image_path="assets/cards/coming_soon.png",
            title="Edit Wine",
            on_click=None,
        )
        card_delete = Card(
            frame_cards,
            image_path="assets/cards/coming_soon.png",
            title="Remove Wine",
            on_click=None,
        )
        card_list = Card(
            frame_cards,
            image_path="assets/cards/coming_soon.png",
            title="Show Wine List",
            on_click=None,
        )
        # Place cards
        card_add.grid(row=0, column=0, pady=(0, 15))
        card_edit.grid(row=0, column=1, padx=20, pady=(0, 15))
        card_delete.grid(row=1, column=0)
        card_list.grid(row=1, column=1)
    
    def show_add_wine_section(self) -> None:
        """
        Shows the form for adding a wine.
        """
        # Clean previous menu
        self.clear_content()

        # Vertical expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add title
        title = ctk.CTkLabel(
            self,
            text="ADD WINE",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )
        title.grid(row=0, column=0, pady=(20, 0), sticky="n") # Cannot use pack for layout expansion reasons

        add_wine_form = AddWineForm(
            self,
            self.session
        )
        add_wine_form.grid(row=1, column=0, pady=(10, 0), sticky="nsew") # Cannot use pack for layout expansion reasons

    
    def clear_content(self) -> None:
        """
        Removes any content in wine frame
        """
        for component in self.winfo_children():
            component.destroy()


        

        
        