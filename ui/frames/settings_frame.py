"""
Classes related with the settings section
"""
import customtkinter as ctk
from PIL import Image

from ui.components import TextInput, ImageInput
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
        self.session = session
        self.shop = session.query(Shop).first()
        self.shop_name = self.shop.name
        self.logo_path = self.shop.logo_path
        self.on_save = on_save
        
        self.name_input = None
        self.image_input = None
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

        # Name input
        self.name_input = TextInput(
            self,
            label_text="Shop Name",
            placeholder=self.shop_name,
            optional=True
        )
        self.name_input.pack(pady=(20, 0), expand=True)

        # Logo input
        self.image_input = ImageInput(
            self,
            label_text="Shop Logo",
            image_path=self.logo_path,
            optional=True
        )
        self.image_input.pack(expand=True)
        
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
        save_button.pack(side="bottom", pady=(0, 30), expand=True)

    def load_logo(self) -> None:
        """
        Show filedialog to user, and show a preview
        """
        self.temp_file_path = ctk.filedialog.askopenfilename(
            title="Select Logo",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )

        # Show preview
        new_image = load_ctk_image(self.temp_file_path) if self.temp_file_path else None    
        self.label_preview.configure(
            image=new_image
        )

    def save_changes(self) -> None:
        """
        Store and load logo, and update label_preview
        """ 
        # Update name
        new_name = self.name_input.entry.get().strip()
        if new_name:
            self.shop.name = new_name

        # Update logo
        new_logo_path = self.image_input.get_new_path()
        self.shop.logo_path = new_logo_path if new_logo_path else "assets/logos/app_logo.png"

        # Sabe changes in db
        self.session.commit()

        # Call back to main window
        self.on_save()