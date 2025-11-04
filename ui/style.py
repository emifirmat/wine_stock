"""
Centralized style definitions for the application.

This module provides a unified styling system for widgets, including colors, 
fonts, icons, spacing, and corner radius configurations.
"""
import customtkinter as ctk
from PIL import Image

from helpers import generate_colored_icon


class Colours:
    """
    Color palette for the application theme.
    """
    COMPANY_NAME = "#556B2F"
    PRIMARY_WINE = "#7B2E2E"
    BG_ALERT = "#F9E5E5"
    BG_FORM = "#F3EEE8"
    BG_HOVER_NAV = "#F0E5E5"
    BG_HOVER_BTN_CLEAR = "#5F2222"
    BG_HOVER_BTN_SAVE = "#688F2E"
    BG_HOVER_BTN_ADD_LINE = "#6F9A3E"
    BG_MAIN = "#F9F6F1"
    BG_SECONDARY = "#FDFCFB"
    BORDERS = "#CCCCCC"
    BTN_ADD_LINE = "#88B04B"
    BTN_ACTIVE = COMPANY_NAME
    BTN_CLEAR = PRIMARY_WINE
    BTN_SAVE = COMPANY_NAME
    DROPDOWN_HOVER = "#D8C4C4"
    ERROR = "#C52323"
    ICONS = "#D4AF37"
    TEXT_BUTTON = "#FDFCFB"
    TEXT_MAIN = "#2E2E2E"
    TEXT_SECONDARY = "#555555"
    WARNING = "#D89A2B"


class Fonts:
    """
    Font configurations for different text elements.
    """
    SHOP_NAME = ("Segoe UI", 38, "bold")
    TITLE = ("Segoe UI", 22, "bold")
    TEXT_WELCOME = ("Segoe UI", 18)
    SUBTITLE = ("Segoe UI", 17, "bold")
    TEXT_MAIN = TEXT_SECONDARY = ("Segoe UI", 16)
    TEXT_BUTTON = ("Segoe UI", 15)
    NAVLINK = ("Segoe UI", 15, "bold")
    NAVLINK_ACTIVE = ("Segoe UI", 15, "bold", "underline")
    TEXT_LABEL = ("Segoe UI", 14)
    TEXT_HEADER = ("Segoe UI", 14, "bold")
    TEXT_HEADER_CALENDAR = ("Segoe UI", 13, "bold")
    TEXT_ERROR = ("Segoe UI", 13, "bold")
    TEXT_DROPDOWN = ("Segoe UI", 13)
    TEXT_AUTOCOMPLETE = ("Segoe UI", 11)
    

class Icons:
    """
    Pre-loaded icon images for UI elements.
    """
    
    # Set up path and icons size
    root_path = "assets/icons"
    small_icon_size = (14, 14)
    medium_icon_size = (18, 18)
    large_icon_size = (28, 28)
    
    # Empty icon used when a label has to hide an icon
    EMPTY = ctk.CTkImage(light_image=Image.new('RGBA', (1, 1), (0, 0, 0, 0)))

    # == Icons ==
    # Note: If dark mode is implemented in the future, add dark_image parameter.
    COLLAPSE = ctk.CTkImage(
        light_image=generate_colored_icon( 
            f"{root_path}/collapse.png", Colours.TEXT_MAIN,
        ),
        size=medium_icon_size,
    )

    DELETE = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/delete.png", Colours.TEXT_MAIN,
        ),
        size=medium_icon_size,
    )
    
    DOTS = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/dots.png", Colours.TEXT_MAIN,
        ),
        size=large_icon_size,
    )

    EDIT = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/edit.png", Colours.TEXT_MAIN,
        ),
        size=medium_icon_size,
    )

    EXPAND = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/expand.png", Colours.TEXT_MAIN,
        ),
        size=medium_icon_size,
    )
    
    GO_BACK = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/go_back.png", Colours.ICONS),
        size=large_icon_size,
    )

    GO_BACK_HOVER = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/go_back.png", Colours.TEXT_MAIN,
        ),
        size=large_icon_size,
    )
    
    PAY = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/pay.png", Colours.ICONS),
        size=large_icon_size,
    )

    PRICE = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/price.png", Colours.ICONS),
        size=large_icon_size,
    )
    
    REPORT = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/report.png", Colours.ICONS),
        size=large_icon_size,
    )

    SETTINGS = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/settings.png", Colours.ICONS),
        size=large_icon_size,
    )

    SHOW = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/show.png", Colours.TEXT_MAIN,
        ),
        size=medium_icon_size,
    )

    STATISTICS = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/statistics.png", Colours.ICONS),
        size=large_icon_size,
    )

    STOCK = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/stock.png", Colours.ICONS),
        size=large_icon_size,
    )

    WARNING = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/warning.png", Colours.ERROR,
        ),
        size=small_icon_size,
    )

    WINE_GLASS = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/wine_glass.png", Colours.ICONS),
        size=large_icon_size,
    )


class Spacing:
    """
    Padding and margin values for layout consistency.
    """

    # Base layout spacing values
    BASE = 8
    SMALL = BASE
    MEDIUM = BASE * 2
    LARGE = BASE * 3
    XLARGE = BASE * 5

    # Widget-specific spacing (horizontal, vertical)
    BUTTONS_X, BUTTONS_Y = MEDIUM, MEDIUM # Or SMALL depeding on context
    CARDS_X, CARDS_Y = LARGE, SMALL
    LABELS_X, LABELS_Y = SMALL, SMALL
    NAVLINK_X, NAVLINK_Y = MEDIUM, SMALL
    SECTION_X, SECTION_Y = MEDIUM, MEDIUM # or LARGE depending on context
    SUBSECTION_X, SUBSECTION_Y = MEDIUM, SMALL
    TABLE_X, TABLE_Y = SMALL, LARGE
    TITLE_X, TITLE_Y = SMALL, (LARGE, SMALL) # Includes subtitle
    WINDOW_X, WINDOW_Y =  XLARGE, XLARGE


class Rounding:
    """
    Corner radius values for widget borders.
    """
    BASE = 4
    SOFT = BASE
    REGULAR = BASE * 2
    STRONG = BASE * 4
    
    BUTTON = REGULAR
    CALENDAR = STRONG
    CARD = STRONG
    CELL = SOFT
    ENTRY = SOFT
    FRAME = STRONG
    LABEL = STRONG
    TOGGLE = STRONG
