"""
Settings section frame and shop configuration.

This module defines the settings section where users can configure
shop details such as name and logo.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from typing import Callable

from ui.components import AutoScrollFrame
from ui.forms.settings import SettingsForm
from ui.style import Colours, Fonts, Spacing


class SettingsFrame(AutoScrollFrame):
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
            **kwargs: Additional keyword arguments for AutoScrollFrame
        """
        super().__init__(root, **kwargs)
        self.inner.configure(**kwargs)
        self.canvas.configure(bg=kwargs["fg_color"])
        
        # DB instances
        self.session = session

        # Callbacks
        self.on_save = on_save

        # Components
        self.create_components()

    def create_components(self) -> None:
        """
        Create and display the settings form.
        """
        # Create settings form
        settings_form = SettingsForm(
            self.inner,
            self.session,
            on_save=self.on_save
        )
        settings_form.pack(padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y)