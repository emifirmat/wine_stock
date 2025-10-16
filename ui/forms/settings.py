"""
File for settings form.
"""
import customtkinter as ctk

from db.models import Shop
from ui.components import (TextInput, ImageInput)
from ui.style import Colours, Fonts


class SettingsForm(ctk.CTkFrame):
    """
    It contains all the components and logic related to settings
    """
    def __init__(
            self, root: ctk.CTkFrame, session, on_save, **kwargs
        ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_FORM,
        )
        
        # Db instances
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
        Creates the setting option components
        """
        # Name input
        self.input_name = TextInput(
            self,
            label_text="Shop Name",
            placeholder=self.shop.name,
            optional=True
        )

        # Logo input
        self.input_image = ImageInput(
            self,
            label_text="Shop Logo",
            image_path=self.shop.logo_path,
            optional=True
        )
    
        
        for input in [self.input_name, self.input_image]:
            input.set_total_width(450)
            input.pack(padx= 15, pady=(20, 0), expand=True)

        # Save Button
        save_button = ctk.CTkButton(
            self,
            text="Save",
            text_color=Colours.BG_SECONDARY,
            fg_color=Colours.BTN_SAVE,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            font=Fonts.TEXT_MAIN,
            corner_radius=10,
            cursor="hand2",
            command=self.save_changes
        )
        save_button.pack(side="bottom", pady=(20, 30), expand=True)

    def save_changes(self) -> None:
        """
        Store and load logo, and update label_preview
        """ 
        # Update name
        new_name = self.input_name.entry.get().strip()
        if new_name:
            self.shop.name = new_name

        # Update logo
        new_logo_path = self.input_image.get_new_path()
        self.shop.logo_path = new_logo_path if new_logo_path else "assets/logos/app_logo.png"

        # Sabe changes in db
        self.session.commit()

        # Call back to main window
        self.on_save()