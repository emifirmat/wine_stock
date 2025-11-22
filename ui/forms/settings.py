"""
Settings form for shop configuration.

This module provides the form interface for updating shop name and logo
in the settings section.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from typing import Callable

from db.models import Shop
from helpers import load_image_from_file
from ui.components import TextInput, ImageInput
from ui.style import Colours, Fonts, Spacing, Rounding


class SettingsForm(ctk.CTkFrame):
    """
    Settings form for shop configuration.
    
    Provides input fields for shop name and logo, allowing users to
    customize the shop information displayed in the application.
    """
    def __init__(
            self, root: ctk.CTkFrame, session: Session, on_save: Callable, **kwargs
        ):
        """
        Initialize the settings form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            on_save: Callback function executed after saving changes
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color=Colours.BG_FORM, corner_radius=Rounding.FRAME)
        
        # DB instances
        self.session = session
        self.shop = session.query(Shop).first()
        
        # Callbacks
        self.on_save = on_save

        # Components
        self.input_name = None
        self.input_image = None
        self.create_components()

    def create_components(self) -> None:
        """
        Create and display settings form inputs and save button.
        """
        # Shop name input
        self.input_name = TextInput(
            self,
            label_text="Shop Name",
            placeholder=self.shop.name,
            optional=True
        )

        # Shop logo input
        self.input_image = ImageInput(
            self,
            label_text="Shop Logo",
            image_path=self.shop.logo_path,
            optional=True
        )
        
        # Configure and position inputs
        for input_widget in [self.input_name, self.input_image]:
            input_widget.set_total_width(450)
            input_widget.pack(
                padx=Spacing.SECTION_X, pady=(Spacing.SECTION_Y, 0), expand=True
            )

        # Create Save Button
        save_button = ctk.CTkButton(
            self,
            text="Save",
            text_color=Colours.BG_SECONDARY,
            fg_color=Colours.BTN_SAVE,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            font=Fonts.TEXT_MAIN,
            corner_radius=Rounding.BUTTON,
            cursor="hand2",
            command=self.save_changes
        )
        save_button.pack(
            side="bottom", padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y
        )

    def save_changes(self) -> None:
        """
        Save shop name and logo changes to database.
        
        Updates the shop record with new name (if provided) and logo path,
        then executes the callback to refresh the main window display.
        """ 
        # Update shop name if provided
        new_name = self.input_name.entry.get().strip()
        if new_name:
            self.shop.name = new_name

        # Update shop logo if new file selected
        new_logo_path = self.input_image.get_new_path()
        if new_logo_path:
            # Save logo to assets folder and get destination path
            saved_path = load_image_from_file(new_logo_path)
            self.shop.logo_path = str(saved_path)

        # If no new logo selected, keep existing or use default
        elif not self.shop.logo_path:
            self.shop.logo_path = "assets/logos/app_logo.png"

        # Save changes to DB
        self.session.commit()

        # Execute callback to refresh main window
        self.on_save()