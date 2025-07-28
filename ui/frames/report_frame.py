"""
Classes related with the price section
"""
import customtkinter as ctk
from PIL import Image

from ui.components import TextInput, ImageInput
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop

class ReportFrame(ctk.CTkFrame):
    """
    It contains all the components and logic related to report section
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
        Creates the report section components
        """
        # Title
        title = ctk.CTkLabel(
            self,
            text="STOCK",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(pady=(20, 0))

        # Warning Text
        introduction = ctk.CTkLabel(
            self,
            text="This section will be available in a future update.",
            text_color=Colours.TEXT_MAIN,
            justify="center",
            font=Fonts.TEXT_MAIN
        )
        introduction.pack(pady=200)