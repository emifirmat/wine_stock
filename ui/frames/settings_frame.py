"""
Classes related with the settings section
"""
import customtkinter as ctk
from PIL import Image

from ui.components import TextInput, ImageInput
from ui.forms.settings import SettingsForm
from ui.style import Colours, Fonts
from helpers import load_ctk_image
from db.models import Shop

class SettingsFrame(ctk.CTkFrame):
    """
    It contains all the components and logic related to settings
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
        
        # Db instances
        self.session = session

        # Callbacks
        self.on_save = on_save

        # Components
        self.create_components()

    def create_components(self) -> None:
        """
        Creates the setting option components
        """
        # Title
        title = ctk.CTkLabel(
            self,
            text="SETTINGS",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(pady=(20, 0))

        # Introduction
        introduction = ctk.CTkLabel(
            self,
            text="Set the name and logo that represent your winery within the app.",
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(pady=15)

        # == Setting Form ==
        settings_form = SettingsForm(
            self,
            self.session,
            on_save=self.on_save
        )
        settings_form.pack(pady=15)