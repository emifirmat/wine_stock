"""
Classes related with the wine section
"""

import customtkinter as ctk
from PIL import Image

from ui.components import TextInput
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine

class WineFrame(ctk.CTkFrame):
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
            border_width=1
        )
        self.session = session
        self.wine = session.query(Wine)
        self.create_components()
        #self.on_save = on_save
        
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
        