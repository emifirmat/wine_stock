"""
Secondary functions used by the main program.
"""
import shutil
import uuid
from customtkinter import filedialog
from pathlib import Path
from typing import Type, TypeVar
from PIL import Image, ImageOps
from PIL.Image import Image as PILImage
from sqlalchemy.orm import Session


def populate_db_model(fields: list[str], model: type, session: Session) -> None: 
    """
    Populate model with entries if the do not already exists.

    Parameters:
        - fields: List of entry names to be added
        - model: Model class from models.py
        - session: SQLAlchemy session to perform DB operations
    """
    for field in fields:
        if not session.query(model).filter_by(name=field).first():
            session.add(model(name=field))
        session.commit()   


def generate_colored_icon(path: str, colour: type) -> PILImage:
    """
    Changes the colour of an icon image (monochrome).
    Parameters:
        path: Location of the icon image
        colour: Desired colour
    """
    icon_image = Image.open(path).convert("RGBA")  # This allows a convertion with transparency

    # Get grayscale keeping transparent background
    grayscale_icon = icon_image.convert("L")
    alpha = icon_image.getchannel("A") # To keep transparency

    # Black is the draw, white is the background
    colored_icon = ImageOps.colorize(grayscale_icon, black=colour, white="white")
    colored_icon.putalpha(alpha)
    
    return colored_icon


def generate_favicon(path: str) -> PILImage:
    """
    Converts a png file to icon file.
    Parameters:
        path: Location of the png file
    """
    image = Image.open(path)
    image.save("assets/favicon.ico", format="ICO", sizes=[(32, 32)])


def load_image_from_file() -> str:
    """
    Open a dialog for the user to pick a picture.
    Then it creates a copy of it in assets/user_images with the name logo_user/
    It creates the folders if they don't exist.
    It deletes any old logo file.
    
    Returns:
        destination_path: Full path of the new logo
    """
    
    # Select image
    filepath = filedialog.askopenfilename(
        title="Select Logo",
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )
    if filepath:
        original_path = Path(filepath)
        
        # Create folder if it doesn't exist
        save_dir = Path("assets/user_images")
        save_dir.mkdir(
            parents=True, # Creates folder assets if it doesn't exist
            exist_ok=True # Don't raise an error if folder exits
        )
        
        # Create new file name
        extension = original_path.suffix
        new_filename = f"logo_user{extension}"
        destination_path = save_dir / new_filename
        
        # Delete old logo if exits
        for file in save_dir.glob("logo_user.*"):
            file.unlink()

        # Copy new logo
        shutil.copy(original_path, destination_path)

    return destination_path