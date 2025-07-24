import os
import platform
import customtkinter as ctk
from PIL import Image
from sqlalchemy.orm import Session

from ui.style import Colours, Fonts, Icons
from ui.settings_frame import SettingsFrame
from ui.wine_frame import WineFrame
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop

class MainWindow:
    """Main window of the app"""
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 700
    
    def __init__(self, root: ctk.CTk, session: Session):
        # Main window
        self.root = root
        self.setup_main_window()
        # DB
        self.session = session
        # Layout Frames
        self.frame_top = None
        self.frame_side = None
        self.frame_body = None
        self.create_layout_containers()
        # Topframe
        self.shop = None
        self.label_logo = None
        self.label_shop_name = None
        self.create_topframe_components()
        # Sidebar
        self.button_home = None
        self.button_wine = None
        self.button_stock = None
        self.button_price = None
        self.button_settings = None
        self.create_sidebar_components()

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
        # Import data from DB
        self.shop = self.session.query(Shop).first()
  
        # Create Logo
        self.label_logo = ctk.CTkLabel(
            self.frame_top,
            image = load_ctk_image(self.shop.logo_path),
            text="",
            fg_color="transparent"  
        )
        
        # Create Name
        self.label_shop_name = ctk.CTkLabel(
            self.frame_top,
            text=self.shop.name,
            text_color=Colours.STATUS,
            font=Fonts.SHOP_NAME,
        )
        
        # Place labels
        self.label_logo.pack(side="left", padx=40, pady=10)
        self.label_shop_name.place(relx=0.6, rely=0.6, anchor="center")

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
            font=Fonts.NAVLINK,
            image=Icons.STATISTICS,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            corner_radius=10,
            cursor="hand2",
        )
        self.button_wine = ctk.CTkButton(
            self.frame_side,
            text="Wine",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.NAVLINK,
            image=Icons.WINE_GLASS,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            corner_radius=10,
            cursor="hand2",
            command=self.show_wine_section
        )
        self.button_stock = ctk.CTkButton(
            self.frame_side,
            text="Stock",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.NAVLINK,
            image=Icons.STOCK,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            corner_radius=10,
            cursor="hand2"
        )
        self.button_price = ctk.CTkButton(
            self.frame_side,
            text="Price",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.NAVLINK,
            image=Icons.PRICE,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            corner_radius=10,
            cursor="hand2"
        )
        self.button_settings =  ctk.CTkButton(
            self.frame_side,
            text="Settings",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.NAVLINK,
            image=Icons.SETTINGS,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            corner_radius=10,
            cursor="hand2",
            command=self.show_settings_section,
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

    def show_wine_section(self):
        """Click event that shows the wine section in the body frame"""
        # Add function to clear body
        self.clear_body()

        # Display settings frame
        frame_wine = WineFrame(
            self.frame_body, 
            self.session,
            on_save=None,
        )
        frame_wine.pack(padx=20, pady=20, fill="both", expand="true")


    def show_settings_section(self):
        """Click event that shows the settings section in the body frame"""
        # Add function to clear body
        self.clear_body()

        # Display settings frame
        frame_settings = SettingsFrame(
            self.frame_body, 
            self.session,
            on_save=self.refresh_shop_labels,
        )
        frame_settings.pack(padx=20, pady=20, fill="both", expand="true")

    def clear_body(self):
        """
        Clears the content of frame body removing all the components inside.
        """
        for component in self.frame_body.winfo_children():
            component.destroy()
    
    
    def refresh_shop_labels(self):
        """
        Callback function. Refresh name and logo of the shop located at the top 
        frame.

        Inputs:
            new_name =  New name of the shop typed by the user
            new_logo_path = Path of the new logo picked by the user
        """
        self.session.refresh(self.shop) 
        
        # Update label shop name
        self.label_shop_name.configure(text=self.shop.name)

        # Update image logo
        self.label_logo.configure(image=load_ctk_image(self.shop.logo_path))


    