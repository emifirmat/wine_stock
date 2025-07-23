"""
Style file for the app
"""
import customtkinter as ctk
from PIL import Image

from helpers import generate_colored_icon

class Colours:
    PRIMARY_WINE = "#7B2E2E"
    BG_MAIN = "#F9F6F1"
    BG_SECONDARY = "#FDFCFB"
    BG_HOVER = "#F0E5E5"
    TEXT_MAIN = "#2E2E2E"
    BORDERS = "#CCCCCC"
    STATUS = "#556B2F"
    ICONS = "#D4AF37"

class Fonts:
    SHOP_NAME = ("Segoe UI", 40, "bold")
    TITLE = ("Segoe UI", 20, "bold")
    SUBTITLE = ("Segoe UI", 16, "bold")
    TEXT = ("Segoe UI", 15)
    BUTTON = ("Segoe UI", 15, "bold")

class Icons:
    root_path = "assets/icons"
    icon_size = (28, 28)
    
    STATISTICS = ctk.CTkImage(
        # IF in the future I set dark mode, I have to add dark image
        light_image=generate_colored_icon(f"{root_path}/statistics.png", Colours.ICONS),
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
    SETTINGS = ctk.CTkImage(
        light_image=generate_colored_icon(f"{root_path}/settings.png", Colours.ICONS),
        size=(icon_size),
    )
    