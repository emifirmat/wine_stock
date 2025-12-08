"""
Main application window and layout management.

This module defines the main window structure, including the top bar with shop info,
sidebar navigation menu, and main content area where different sections are displayed.
"""
import platform
import customtkinter as ctk
from sqlalchemy.orm import Session

from ui.components import NavLink, ButtonGoBack
from ui.style import Colours, Fonts, Icons, Spacing, Rounding
from ui.frames.home_frame import HomeFrame
from ui.frames.wine_frame import WineFrame
from ui.frames.report_frame import ReportFrame
from ui.frames.settings_frame import SettingsFrame
from helpers import load_ctk_image, resource_path
from db.models import Shop

class MainWindow:
    """
    Main application window and layout management.

    Manages the overall application structure including the top bar with shop information,
    sidebar navigation menu, and main content area where different sections are displayed.
    """

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 768
    
    def __init__(self, root: ctk.CTk, session: Session):
        """
        Initialize the main window with all components.
        
        Parameters:
            root: CustomTkinter root window instance
            session: SQLAlchemy database session
        """
        # Main window
        self.root = root
        self.setup_main_window()
        
        # DB
        self.session = session
        
        # Layout frames
        self.frame_top = None
        self.frame_side = None
        self.frame_body = None
        self.create_layout_containers()
        
        # Topframe components
        self.shop = None
        self.label_logo = None
        self.label_shop_name = None
        self.create_topframe_components()
        
        # Sidebar components
        self.button_home = None
        self.button_wine = None
        self.button_report = None
        self.button_settings = None
        self.create_sidebar_components()
        
        # Body frame components
        self.button_go_back = None
        self.title = None
        self.introduction = None
        
        # Initial welcome message
        self.create_welcome_message()
        
    def setup_main_window(self) -> None:
        """
        Configure main window properties including title, size, icon, and colors.
        """
        self.root.title("Wine Stock App")
        self.root.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        
        # Set icon for Windows systems only
        if platform.system() == "Windows":
            try:
                self.root.iconbitmap(resource_path("assets/favicon.ico"))
            except Exception:
                # Silently fall back to default icon if loading fails
                pass   
        
        # Configure background colour
        self.root.configure(fg_color=Colours.BG_MAIN)

    def create_layout_containers(self) -> None:
        """
        Create and position the main layout frames: top bar, sidebar, and body.
        """
        # Create frames
        self.frame_top = ctk.CTkFrame(
            self.root, 
            height=100,
            fg_color="transparent",
            corner_radius=Rounding.FRAME
        )
        self.frame_side = ctk.CTkFrame(
            self.root, 
            fg_color=Colours.BG_SECONDARY,
            corner_radius=Rounding.FRAME,
            border_width=1,
            border_color=Colours.BORDERS
        )
        self.frame_body = ctk.CTkFrame(
            self.root, 
            fg_color=Colours.BG_SECONDARY,
            corner_radius=Rounding.FRAME,
            border_width=1,
            border_color=Colours.BORDERS
        )

        # Configure grid expansion (only second row and column grow)
        self.root.grid_rowconfigure(1, weight=1) 
        self.root.grid_columnconfigure(1, weight=1)

        # Position frames in grid
        self.frame_top.grid(
            row=0, 
            column=0, 
            columnspan=2, 
            sticky="nsew", 
            padx=(Spacing.SMALL, Spacing.LARGE), pady=Spacing.MEDIUM
        )
        self.frame_side.grid(
            row=1, column=0, sticky="nsew", 
            padx=(Spacing.LARGE, Spacing.MEDIUM), pady=(0, Spacing.XLARGE)
        )
        self.frame_body.grid(
            row=1, column=1, sticky="nsew",
            padx=(0, Spacing.LARGE), pady=(0, Spacing.XLARGE)
        )

    def create_topframe_components(self) -> None:
        """
        Create and position shop logo and name in the top frame.
        
        Retrieves shop information from the database and displays it in the top bar.
        """
        # Get shop data from database
        self.shop = self.session.query(Shop).first()
  
        # Create logo label
        self.label_logo = ctk.CTkLabel(
            self.frame_top,
            image = load_ctk_image(self.shop.logo_path),
            text="",
            fg_color="transparent",
            compound="center"         
        )
        
        # Create shop name label
        self.label_shop_name = ctk.CTkLabel(
            self.frame_top,
            text=self.shop.name,
            text_color=Colours.BTN_SAVE,
            font=Fonts.SHOP_NAME,
            wraplength=800,
            justify="center"
        )
        
        # Configure grid expansion
        self.frame_top.grid_columnconfigure(0, weight=0)
        self.frame_top.grid_columnconfigure(1, weight=1)
        self.frame_top.grid_rowconfigure(0, weight=1)

        # Position labels in grid
        self.label_logo.grid(
            row=0, column=0, 
            padx=(Spacing.XLARGE + Spacing.MEDIUM), pady=Spacing.SMALL,
            sticky="nesw"
        )
        self.label_shop_name.grid(
            row=0, column=1, pady=Spacing.SMALL, sticky="nsew"
        )

    def create_sidebar_components(self):
        """
        Create and position navigation menu in the sidebar.
        """
        # Create sidebar title
        title = ctk.CTkLabel(
            self.frame_side,
            text="Menu",
            font=Fonts.TITLE,
            text_color=Colours.PRIMARY_WINE,
            fg_color="transparent"
        )
        title.pack(padx=Spacing.TITLE_X, pady=Spacing.TITLE_Y)

        # Create navigation links with icons
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

        # Position navigation buttons
        for btn in [
            self.button_home, 
            self.button_wine, 
            self.button_report, 
            self.button_settings
        ]:
            btn.pack(
                fill="x", expand=True,
                padx=Spacing.NAVLINK_X, pady=Spacing.NAVLINK_Y
            )

    def show_section(
        self, title_text: str, introduction_text: str, frame_class: ctk.CTkFrame, 
        **kwargs
    ) -> None:
        """
        Clear body frame and display a new section.
        
        Parameters:
            title_text: Title to display at the top of the section
            introduction_text: Introduction text describing the section's purpose
            frame_class: Frame class to instantiate and display as main content
            **kwargs: Additional keyword arguments passed to the frame constructor
        """
        self.clear_body()

        # Create and position header frame
        header_frame = ctk.CTkFrame(self.frame_body, fg_color="transparent")
        header_frame.grid(
            row=0, column=0, sticky="ew", 
            padx=Spacing.XSMALL + 2, pady=Spacing.XSMALL + 2
        )
        header_frame.grid_columnconfigure(1, weight=1)

        # Configure columns layout (columns 0 and 2 mantain button width)
        header_frame.columnconfigure(0, weight=0)
        header_frame.columnconfigure(1, weight=1)    
        header_frame.columnconfigure(2, weight=0)
        
        # Create and position go back button
        self.button_go_back = ButtonGoBack(
            header_frame,
            width=30,
            height=30,
        )
        self.button_go_back.grid(row=0, column=0, sticky="w")
        
        # Create and position title
        self.title = ctk.CTkLabel(
            header_frame,
            text=title_text,
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE,
        ) 
        self.title.grid(
            row=0, column=1, sticky="we", padx=0, pady=Spacing.TITLE_Y, 
        ) 

        # Create alignment_frame to keep title centered
        alignment_frame = ctk.CTkFrame(
            header_frame,
            fg_color="transparent",
            width=30,
            height=30,
        )
        alignment_frame.grid(row=0, column=2, sticky="e")

        # Create introduction text
        self.introduction = ctk.CTkLabel(
            header_frame,
            text=introduction_text,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        self.introduction.grid(
            row=1, column=0, columnspan=3,
            padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y
        )

        # Create content frame
        content_frame = frame_class(
            self.frame_body, 
            self.session,
            fg_color=Colours.BG_SECONDARY,
            **kwargs
        )

        # Padding solution for autoscroll frame with rounded borders
        content_frame.grid(
            row=1, column=0, sticky="nsew",
            padx=Spacing.XSMALL + 2, pady=Spacing.XSMALL + 2
        )

    def update_header(
        self, title: str | None = None, introduction: str | None = None, 
        back_to: str | None = None
    ) -> None:
        """
        Update header components dynamically.
        
        Parameters:
            title: New title text to display (None to keep current)
            introduction: New introduction text (empty string to hide, None to keep current)
            back_to: Navigation target for back button ("home" or "wines", None to keep current)
        """
        # Update title
        if title is not None:
            self.title.configure(text=title)
        
        # Update introduction
        if introduction is not None:
            if introduction == "":
                # Remove from grid to give more space to content_frame
                self.introduction.grid_remove()
            else:
                self.introduction.grid()
                self.introduction.configure(text=introduction)
        
        # Update back button command
        if back_to is not None:
            command_map = {
                "home": self.show_home_section,
                "wines": self.show_wine_section
            }
            command = command_map.get(back_to)

            if command:
                self.button_go_back.set_command(command)

    def show_home_section(self) -> None:
        """
        Display the home section with sales and purchases management.
        """        
        introduction_text = (
            "Add, track, and manage wine sales and purchases to stay on top of "
            "your winery's activity."
        )
        self.show_section(
            "HOME", introduction_text, HomeFrame, on_header_update=self.update_header
        )
            
    def show_wine_section(self) -> None:
        """
        Display the wine inventory management section.
        """    
        introduction_text = (
            "Add, edit, or remove wines from your winery's catalog to keep "
            "your selection up to date."
        )
        self.show_section("WINES", introduction_text, WineFrame, on_header_update=self.update_header)

    def show_report_section(self) -> None:
        """
        Display the reports section with sales, purchases, and stock analytics.
        """
        introduction_text = (
            "Generate and review reports of your sales, purchases and stock. "
            "You can export data in CSV or Excel format."
        )
        self.show_section("REPORTS", introduction_text, ReportFrame)     

    def show_settings_section(self) -> None:
        """
        Display the settings section with shop configuration.
        """
        introduction_text = "Set the name and logo that represent your winery within the app."
        self.show_section(
            "SETTINGS", introduction_text, SettingsFrame, on_save=self.refresh_shop_labels
        )

    def clear_body(self) -> None:
        """
        Remove all widgets from the body frame.
        """
        for component in self.frame_body.winfo_children():
            component.destroy()
        
    def refresh_shop_labels(self) -> None:
        """
        Refresh shop name and logo in the top frame.
        
        Callback function used after saving settings to update the displayed
        shop information with the latest database values.
        """
        self.session.refresh(self.shop) 
        
        # Update label shop name
        self.label_shop_name.configure(text=self.shop.name)

        # Update logo image
        self.label_logo.configure(image=load_ctk_image(self.shop.logo_path))

    def create_welcome_message(self) -> None:
        """
        Display welcome message in the body frame on application startup.
        """
        # Configure grid expansion for body frame
        self.frame_body.rowconfigure(1, weight=1)
        self.frame_body.columnconfigure(0, weight=1)
        
        # Create welcome frame
        frame_welcome = ctk.CTkFrame(
            self.frame_body,
            fg_color="transparent",
            corner_radius=Rounding.STRONG,
            border_color=Colours.BORDERS,
            border_width=1
        )
        frame_welcome.grid(row=1, column=0, sticky="wsen") 
        
        # Create title
        title = ctk.CTkLabel(
            frame_welcome,
            text="Welcome to WineStock",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE,
        )
        title.grid(
            row=0, column=0, padx=Spacing.TITLE_X, pady=Spacing.TITLE_Y, sticky="n"
        )

       # Create welcome text
        welcome_text = (
            "Manage your wine inventory effortlessly: add sales, record "
            "purchases, track stock levels, receive low-stock alerts, and "
            "generate detailed reports."
        )
        label_welcome = ctk.CTkLabel(
            frame_welcome,
            fg_color="transparent",
            image=load_ctk_image("assets/logos/app_logo.png", (150, 150)),
            compound="top",
            text=welcome_text,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_WELCOME,
            pady=Spacing.LARGE,
            wraplength=800,
        )
        label_welcome.grid(
            row=1, column=0, padx=2, pady=Spacing.LARGE, sticky="nwe"
        ) 

        # Create contact text
        contact_text=(
            "If you need a similar system for your business, "
            "you can reach me at emiliano.dev.contact@gmail.com"
        )
        label_contact = ctk.CTkLabel(
            frame_welcome,
            text=contact_text,
            text_color=Colours.TEXT_SECONDARY,
            font=Fonts.TEXT_SECONDARY,
            pady=Spacing.MEDIUM,
        )
        label_contact.grid(row=2, column=0, pady=Spacing.XSMALL, sticky="n")
        
        # Configure grid expansion
        frame_welcome.rowconfigure(0, weight=2)
        frame_welcome.rowconfigure(1, weight=8)
        frame_welcome.columnconfigure(0, weight=1)