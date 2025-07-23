import os
import platform
import customtkinter as ctk
from PIL import Image

from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon


class MainWindow:
    """Main window of the app"""
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 700
    
    def __init__(self, root: ctk.CTk):
        # Main window
        self.root = root
        self.setup_main_window()
        # Frames
        self.frame_top = None
        self.frame_side = None
        self.frame_body = None
        self.create_layout_containers()
        # Topframe
        self.logo = None
        self.shop_name = None
        self.create_topframe_components()
        # Sidebar
        self.button_home = None
        self.button_wine = None
        self.button_stock = None
        self.button_price = None
        self.button_settings = None
        self.create_sidebar_components()
        # Settings
        self.card_settings = None

    def setup_main_window(self) -> None:
        """
        Configure main windows (title, size, etc)
        """
        self.root.title("Wine Stock App")
        self.root.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        # Ico file
        if platform.system() == "Windows":
            self.root.iconbitmap("assets/favicon.ico")    
        # Body of the window
        self.root.configure(
            fg_color=Colours.BG_MAIN
        )

    def create_layout_containers(self) -> None:
        """
        Create frames to keep content organized
        """
        # Set up frames
        self.frame_top = ctk.CTkFrame(
            self.root, 
            height=100,
            fg_color="transparent",
            corner_radius=15
        )
        self.frame_side = ctk.CTkFrame(
            self.root, 
            fg_color=Colours.BG_SECONDARY,
            corner_radius=15,
            border_width=1,
            border_color=Colours.BORDERS
        )
        self.frame_body = ctk.CTkFrame(
            self.root, 
            fg_color=Colours.BG_SECONDARY,
            corner_radius=15
        )

        # Set expansion behaviour for main window
        self.root.grid_rowconfigure(1, weight=1) # Only second row grows
        self.root.grid_columnconfigure(1, weight=1) # ONly second col grows

        # Place and show frames
        self.frame_top.grid(
            row=0, 
            column=0, 
            columnspan=2, 
            sticky="nsew", 
            padx=(10, 20),
            pady=(20, 10)
        )
        self.frame_side.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 20))
        self.frame_body.grid(row=1, column=1, sticky="nsew", padx=20, pady=(0, 20))

    def create_topframe_components(self):
        """
        Create the components located at the top of the page.
        """
        # Create Logo
        logo_image = ctk.CTkImage(
            light_image=Image.open("assets/logos/app_logo.png"),
            size=(80, 80),
        )
        self.logo = ctk.CTkLabel(
            self.frame_top,
            image = logo_image,
            text="",
            fg_color="transparent"  
        )
        
        # Create Name
        self.shop_name = ctk.CTkLabel(
            self.frame_top,
            text="WINE STOCK",
            text_color=Colours.STATUS,
            font=Fonts.SHOP_NAME,
        )
        
        
        # Place labels
        self.logo.pack(side="left", padx=40, pady=10)
        self.shop_name.place(relx=0.5, rely=0.6, anchor="center")

    def create_sidebar_components(self):
        """
        Create each component that will be located in the sidebar.
        """
        # Create sidebar's title
        title = ctk.CTkLabel(
            self.frame_side,
            text="Menu",
            font=Fonts.TITLE,
            text_color=Colours.PRIMARY_WINE,
            fg_color="transparent"
        )
        title.pack(pady=15)

        # Create links with icons
        self.button_home = ctk.CTkButton(
            self.frame_side,
            text="Home",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.BUTTON,
            image=Icons.STATISTICS,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER,
            corner_radius=10,
            cursor="hand2"
        )
        self.button_wine = ctk.CTkButton(
            self.frame_side,
            text="Wine",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.BUTTON,
            image=Icons.WINE_GLASS,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER,
            corner_radius=10,
            cursor="hand2"
        )
        self.button_stock = ctk.CTkButton(
            self.frame_side,
            text="Stock",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.BUTTON,
            image=Icons.STOCK,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER,
            corner_radius=10,
            cursor="hand2"
        )
        self.button_price = ctk.CTkButton(
            self.frame_side,
            text="Price",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.BUTTON,
            image=Icons.PRICE,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER,
            corner_radius=10,
            cursor="hand2"
        )
        self.button_settings =  ctk.CTkButton(
            self.frame_side,
            text="Settings",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.BUTTON,
            image=Icons.SETTINGS,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER,
            corner_radius=10,
            cursor="hand2",
            command=self.show_settings
        )

        # Place buttons
        for btn in [
            self.button_home, 
            self.button_wine, 
            self.button_stock, 
            self.button_price, 
            self.button_settings
        ]:
            btn.pack(fill="x", expand=True, padx=10, pady=5)
            
    def show_settings(self) -> None:
        """
        Displays the setting options in the body frame
        """
        if not self.card_settings:
            self.card_settings = ctk.CTkFrame(
                self.frame_body,
                fg_color = Colours.BG_SECONDARY,
                corner_radius=10,
                border_color=Colours.BORDERS,
                border_width=1
            )
            self.card_settings.pack(padx=20, pady=20, fill="both", expand="true")

            title = ctk.CTkLabel(
                self.card_settings,
                text="SETTINGS",
                text_color= Colours.PRIMARY_WINE,
                font=Fonts.TITLE
            )

            title.pack(pady=20)

            label_name = ctk.CTkLabel(
                self.card_settings,
                text="Shop Name",
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT
            )
           
            entry_name = ctk.CTkEntry(
                self.card_settings,
            )
            
            label_name.pack()
            entry_name.pack()

            # Add logo button
            # Logo preview
            # Cancel button
            # Save Button