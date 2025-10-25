import platform
import customtkinter as ctk
from sqlalchemy.orm import Session

from ui.components import NavLink
from ui.style import Colours, Fonts, Icons
from ui.frames.home_frame import HomeFrame
from ui.frames.wine_frame import WineFrame
from ui.frames.report_frame import ReportFrame
from ui.frames.settings_frame import SettingsFrame
from helpers import load_ctk_image, resource_path
from db.models import Shop

class MainWindow:
    """Main window of the app"""
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 768
    
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
        self.button_report = None
        self.button_price = None
        self.button_settings = None
        self.create_sidebar_components()
        # Welcome message
        self.create_welcome_message()

    def setup_main_window(self) -> None:
        """
        Configure main windows (title, size, etc)
        """
        self.root.title("Wine Stock App")
        self.root.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        # Ico file
        if platform.system() == "Windows":
            self.root.iconbitmap(resource_path("assets/favicon.ico"))    
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
        self.root.grid_columnconfigure(1, weight=1) # Only second col grows

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
            text_color=Colours.BTN_SAVE,
            font=Fonts.SHOP_NAME,
            wraplength=800,
            justify="center"
        )
        
        # Responsiveness
        self.frame_top.grid_columnconfigure(0, weight=0)
        self.frame_top.grid_columnconfigure(1, weight=1)

        # Place labels
        self.label_logo.grid(row=0, column=0, padx=40, pady=10)
        self.label_shop_name.grid(row=0, column=1, pady=10, sticky="nsew")

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
        self.button_home = NavLink(
            self.frame_side,
            text="Home",
            image=Icons.PAY,
            command=self.show_home_section
        )
        self.button_wine = NavLink(
            self.frame_side,
            text="Wines",
            image=Icons.WINE_GLASS,
            command=self.show_wine_section
        )
        self.button_report = NavLink(
            self.frame_side,
            text="Reports",
            image=Icons.REPORT,
            command=self.show_report_section
        )
  
        self.button_settings = NavLink(
            self.frame_side,
            text="Settings",
            image=Icons.SETTINGS,
            command=self.show_settings_section,
        )

        # Place buttons
        for btn in [
            self.button_home, 
            self.button_wine, 
            self.button_report, 
            self.button_settings
        ]:
            btn.pack(fill="x", expand=True, padx=10, pady=5)

    def show_section(self, frame_class, **kwargs):
        """
        Clears body and display a section frame.
        Parameters:
            - frame_class: Class of the frame to be displayed
            - kwargs: Additional arguments added to the frame
        """
        self.clear_body()

        frame = frame_class(
            self.frame_body, 
            self.session, 
            **kwargs
        )

        self.frame_body.grid_rowconfigure(0, weight=1)
        self.frame_body.grid_columnconfigure(0, weight=1)

        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def show_home_section(self):
        """Click event that shows the home section in the body frame"""        
        self.show_section(HomeFrame, main_window=self)
            
    def show_wine_section(self):
        """Click event that shows the wine section in the body frame"""     
        self.show_section(WineFrame, main_window=self)

    def show_report_section(self):
        """Click event that shows the report section in the body frame"""
        self.show_section(ReportFrame)     

    def show_settings_section(self):
        """Click event that shows the settings section in the body frame"""
        self.show_section(SettingsFrame, on_save=self.refresh_shop_labels)

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

    def create_welcome_message(self):
        """
        Welcome message that appears in frame_body when user starts the app
        """

        # Add title
        title = ctk.CTkLabel(
            self.frame_body,
            text="Welcome to WineStock",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE,
        )
        title.grid(row=0, column=0, pady=(20, 0), padx=150, sticky="n") # Cannot use pack for layout expansion reasons

        image = load_ctk_image("assets/logos/app_logo.png", (130, 130)) 
        label_image = ctk.CTkLabel(
            self.frame_body,
            image=image,
            text="",
            fg_color="transparent",               
        )
        
        label_image.grid(row=1, column=0, pady=(20, 0), padx=150, sticky="we") # Cannot use pack for layout expansion reasons

        # Add form
        text = ctk.CTkLabel(
                self.frame_body,
                text="Start managing your wine inventory: add sales, record purchases, remove stock movements, and generate reports easily.",
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_MAIN,
                wraplength=800
            )
        text.grid(row=2, column=0, pady=(50, 0), padx=150, sticky="we") # Cannot use pack for layout expansion reasons
