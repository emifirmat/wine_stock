"""
Style file for the app
"""
import customtkinter as ctk

from helpers import generate_colored_icon

class Colours:
    PRIMARY_WINE = BTN_CLEAR = "#7B2E2E"
    BG_MAIN = "#F9F6F1"
    BG_SECONDARY = TEXT_BUTTON = "#FDFCFB"
    BTN_ADD_LINE = "#88B04B"
    BG_HOVER_NAV = "#F0E5E5"
    BG_HOVER_BTN_CLEAR = "#5F2222"
    BG_HOVER_BTN_SAVE = "#688F2E"
    BG_HOVER_BTN_ADD_LINE = "#6F9A3E"
    DROPDOWN_HOVER = "#D8C4C4"
    TEXT_MAIN = "#2E2E2E"
    TEXT_SECONDARY = "#555555"
    BORDERS = "#CCCCCC"
    COMPANY_NAME = BTN_SAVE = BTN_ACTIVE = "#556B2F"
    ICONS = "#D4AF37"
    ERROR = "#C52323"

class Fonts:
    SHOP_NAME = ("Segoe UI", 40, "bold")
    TITLE = ("Segoe UI", 20, "bold")
    SUBTITLE = ("Segoe UI", 16, "bold")
    TEXT_MAIN = TEXT_BUTTON = ("Segoe UI", 15)
    NAVLINK = ("Segoe UI", 15, "bold")
    NAVLINK_ACTIVE = ("Segoe UI", 15, "bold", "underline")
    TEXT_LABEL = ("Segoe UI", 14)
    TEXT_HEADER = ("Segoe UI", 14, "bold")
    TEXT_SECONDARY = ("Segoe UI", 13, "italic")
    TEXT_ERROR = ("Segoe UI", 12)
    TEXT_AUTOCOMPLETE = ("Segoe UI", 9)

class Icons:
    root_path = "assets/icons"
    icon_size = (28, 28)
    
    STATISTICS = ctk.CTkImage(
        # IF in the future I set dark mode, I have to add dark image
        light_image=generate_colored_icon(f"{root_path}/statistics.png", Colours.ICONS),
        size=(icon_size),
    )

    PAY = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/pay.png", Colours.ICONS),
        size=(icon_size),
    )

    WINE_GLASS = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/wine_glass.png", Colours.ICONS),
        size=(icon_size),
    )
    STOCK = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/stock.png", Colours.ICONS),
        size=(icon_size),
    )
    PRICE = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/price.png", Colours.ICONS),
        size=(icon_size),
    )
    
    REPORT = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/report.png", Colours.ICONS),
        size=(icon_size),
    )

    SETTINGS = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/settings.png", Colours.ICONS),
        size=(icon_size),
    )

    GO_BACK = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/go_back.png", Colours.ICONS),
        size=(icon_size),
    )

    GO_BACK_HOVER = ctk.CTkImage(
        light_image=generate_colored_icon(
            f"{root_path}/go_back.png", Colours.TEXT_MAIN,
        ),
        size=(icon_size),
    )
    