"""
Settings section frame and shop configuration.

This module defines the settings section where users can configure
shop details such as name and logo.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from typing import Callable

from ui.forms.settings import SettingsForm
from ui.style import Colours, Fonts, Spacing, Rounding


class SettingsFrame(ctk.CTkFrame):
    """
    Settings section frame with shop configuration form.
    
    Provides interface for updating shop name and logo that appear
    in the top bar of the application.
    """
    def __init__(
        self, root: ctk.CTkFrame, session: Session, on_save: Callable, **kwargs
    ):
        """
        Initialize the settings frame with configuration form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            on_save: Callback function to refresh shop labels after saving
            **kwargs: Additional keyword arguments for CTkFrame
        """
        super().__init__(root, **kwargs)
        
        # DB instances
        self.session = session

        # Callbacks
        self.on_save = on_save

        # Components
        self.create_components()

    def create_components(self) -> None:
        """
        Create and display settings section components (title, intro, form).
        """
        # Create title
        title = ctk.CTkLabel(
            self,
            text="SETTINGS",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(padx=Spacing.TITLE_X, pady=Spacing.TITLE_Y)

        # Create introduction text
        introduction = ctk.CTkLabel(
            self,
            text="Set the name and logo that represent your winery within the app.",
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY,
        )
        introduction.pack(padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y)

        # Create settings form
        settings_form = SettingsForm(
            self,
            self.session,
            on_save=self.on_save
        )
        settings_form.pack(padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y)