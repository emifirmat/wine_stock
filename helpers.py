"""
Secondary functions used by the main program.
"""
import shutil
import sys
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from PIL.Image import Image as PILImage
from sqlalchemy.orm import Session


def resource_path(relative_path: str) -> Path:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = Path(sys._MEIPASS)  # Attributed created by PyInstaller 
    except AttributeError:
        base_path = Path(__file__).parent  # Dev Mode

    return base_path / relative_path


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

def get_by_id(model: type, id_: int, session: Session):
    """
    Get the instance of a model by its Id.
    """
    return session.query(model).get(id_)


def load_ctk_image(
    image_path: str, size: tuple[int,int] = (80, 80), rounded: bool = True
) -> ctk.CTkImage:
    """
    Loads a ctk image

    Parameters:
        image_path: The path of the image to load
        size: Desired size of the image
        rounded: If true, the image will have rounded borders.
    
    Returns:
        CTkImage that can be used in other components
    """
    image_path = resource_path(image_path) # Make it compatible for all OS
    image = Image.open(image_path)

    if rounded:
        round_image(image)

    return ctk.CTkImage(
        light_image=image,
        size=(size),
    )


def generate_colored_icon(
        path: str, 
        colour: type, 
        rounded: bool = False, 
        radius: int = 50,
    ) -> PILImage:
    """
    Changes the colour of an icon image (monochrome).
    Parameters:
        path: Location of the icon image
        colour: Desired colour
    """
    icon_path = resource_path(path) # Make it compatible for all OS
    icon_image = Image.open(icon_path).convert("RGBA")  # This allows a convertion with transparency

    # Get grayscale keeping transparent background
    grayscale_icon = icon_image.convert("L")
    alpha = icon_image.getchannel("A") # To keep transparency

    # Black is the draw, white is the background
    colored_icon = ImageOps.colorize(grayscale_icon, black=colour, white="white")
    colored_icon.putalpha(alpha)
    
    if not rounded:
        return colored_icon
    
    # Create a mask to have a rounded image
    if rounded:
        round_image(colored_icon, radius)

    return colored_icon

def round_image(image: PILImage, radius: int = 50):
    """
    Take an image and round its border according to the radius.
    Parameters:
        - image: The image that will have the border rounded.
        - radius: The radius of the border.
    """
    
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, image.size[0], image.size[1]),
        radius=radius,
        fill=255
    )

    # Apply mask
    image.putalpha(mask)


def generate_favicon(path: str) -> PILImage:
    """
    Converts a png file to icon file.
    Parameters:
        path: Location of the png file
    """
    favicon_path = resource_path(path) # Make it compatible for all OS
    image = Image.open(favicon_path)
    image.save("assets/favicon.ico", format="ICO", sizes=[(32, 32)])


def load_image_from_file(filepath) -> str:
    """
    Creates a copy of the user's logo in assets/user_images with the name logo_user.
    It creates the folders if they don't exist.
    It deletes any old logo file.
    
    Returns:
        destination_path: Full path of the new logo
    """
    
    # Select image
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