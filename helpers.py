"""
Helper utilities for the application.

This module provides secondary functions used throughout the program,
including resource path handling, database utilities, image processing,
and UI helper functions.
"""
import shutil
import sys
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from PIL.Image import Image as PILImage
from sqlalchemy.orm import Session
from typing import Any


def resource_path(relative_path: str) -> Path:
    """ 
    Get absolute path to resource, works for dev and for PyInstaller.
    
    Parameters:
        relative_path: Path relative to the base directory
        
    Returns:
        Absolute path to the resource
    """
    try:
        base_path = Path(sys._MEIPASS)  # Attributed created by PyInstaller 
    except AttributeError:
        base_path = Path(__file__).parent  # Dev Mode

    return base_path / relative_path


def populate_db_model(fields: list[str], model: type, session: Session) -> None: 
    """
    Populate model with entries if the do not already exists.

    Parameters:
        fields: List of entry names to be added
        model: Model class from models.py
        session: SQLAlchemy session to perform DB operations
    """
    for field in fields:
        if not session.query(model).filter_by(name=field).first():
            session.add(model(name=field))
            session.commit()  

def get_by_id(model: type, id_: int, session: Session) -> Any | None:
    """
    Get the instance of a model by its ID.

    Parameters:
        model: Model class from models.py
        id_: Primary key ID of the instance
        session: SQLAlchemy session to perform DB operations
        
    Returns:
        Model instance if found, None otherwise

    """
    return session.query(model).get(id_)


def load_ctk_image(
    image_path: str, size: tuple[int,int] = (100, 100), rounded: bool = True,
    radius: int = 16
) -> ctk.CTkImage:
    """
    Load an image and convert it to CTkImage format.

    Parameters:
        image_path: Path to the image file
        size: Desired dimensions (width, height) of the image
        rounded: Whether to apply rounded corners to the image
        radius: Corner radius in pixels (only used if rounded is True)
    
    Returns:
        CTkImage that can be used in CustomTkinter widgets
    """
    image_path = resource_path(image_path) # Make it compatible for all OS
    image = Image.open(image_path)

    # Resize image in high quality.
    # Note: For compatibility, it's better to resize with PIL than CTk.
    image = image.resize(size, Image.LANCZOS)

    if rounded:
        image = round_image(image, radius)

    return ctk.CTkImage(light_image=image, size=size)


def round_image(image: PILImage, radius: int) -> PILImage:
    """
    Apply rounded corners to an image.
    
    Parameters:
        image: Image to be processed
        radius: Corner radius in pixels
        
    Returns:
        New image with rounded corners and transparent background
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    width, height = image.size

    # Create rounded mask
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, width, height),
        radius=radius,
        fill=255
    )

    # Create a transparent image
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))

    # Paste original image using the mask
    result.paste(image, (0, 0), mask)

    return result


def generate_colored_icon(
        path: str, colour: str, rounded: bool = False, radius: int = 50,
    ) -> PILImage:
    """
    Changes the colour of a monochrome icon image.
    
    Parameters:
        path: Location of the icon image file
        colour: Desired color in hex format (e.g., "#FF0000")
        rounded: Whether to apply rounded corners
        radius: Corner radius in pixels (only used if rounded is True)
    
    Returns:
        Colored icon image with transparency preserved
    """
    icon_path = resource_path(path) # Make it compatible for all OS
    icon_image = Image.open(icon_path).convert("RGBA")  # This allows a convertion with transparency

    # Get grayscale while keeping transparent background
    grayscale_icon = icon_image.convert("L")
    alpha = icon_image.getchannel("A") # Preserve transparency

    # Black is the drawing, white is the background
    colored_icon = ImageOps.colorize(grayscale_icon, black=colour, white="white")
    colored_icon.putalpha(alpha)
    
    # Create a mask to have a rounded image
    if rounded:
        round_image(colored_icon, radius)

    return colored_icon


def generate_favicon(path: str) -> None:
    """
    Convert a PNG file to ICO favicon format.
    
    Parameters:
        path: Location of the PNG file
    """
    favicon_path = resource_path(path) # Make it compatible for all OS
    image = Image.open(favicon_path)
    image.save("assets/favicon.ico", format="ICO", sizes=[(32, 32)])


def load_image_from_file(filepath: str | Path) -> Path:
    """
    Create a copy of the user's logo in assets/user_images with the name logo_user.
    Creates folders if they don't exist and deletes any old logo file.
    
    Parameters:
        filepath: Path to the original image file
        
    Returns:
        Full path of the newly saved logo
    """
    
    # Select image
    original_path = Path(filepath)
    
    # Create folder if it doesn't exist
    save_dir = Path("assets/user_images")
    save_dir.mkdir(
        parents=True, # Create parent folders if they don't exist
        exist_ok=True # Don't raise an error if folder exits
    )
    
    # Create new file name
    extension = original_path.suffix
    new_filename = f"logo_user{extension}"
    destination_path = save_dir / new_filename
    
    # Delete old logo if it exits
    for file in save_dir.glob("logo_user.*"):
        file.unlink()

    # Copy new logo
    shutil.copy(original_path, destination_path)

    return destination_path

def deep_getattr(obj: Any, attr_path: str) -> Any | None:
    """
    Get nested attributes using dot notation.
    
    Example: deep_getattr(wine, "colour.name") is equivalent to wine.colour.name
    
    Parameters:
        obj: Object to get the attribute from
        attr_path: Attribute path using dot notation (e.g., "colour.name")
        
    Returns:
        Attribute value if found, None if any intermediate attribute is None
    """
    for attr in attr_path.split('.'):
        obj = getattr(obj, attr, None)
        if obj is None:
            return None
    return obj

def get_coords_center(widget: ctk.CTkBaseClass) -> tuple[int, int]:
    """
    Get the coordinates of the screen center.
    
    Parameters:
        widget: CTk widget used to access screen dimensions
        
    Returns:
        Tuple with (x, y) coordinates of the screen center
    """
    x = widget.winfo_screenwidth() // 2
    y = widget.winfo_screenheight() // 2
    return (x, y)
