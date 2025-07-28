"""
Form that contain the inputs and methods to add a new wine
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime
from PIL import Image

from ui.components import TextInput, IntInput, Card, DropdownInput, ImageInput
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine, Colour, Style

class AddWineForm(ctk.CTkScrollableFrame):
    """
    Contains all the components and logic related to ADD Wine.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, on_save = None, **kwargs
        ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            scrollbar_button_color=Colours.BG_HOVER_NAV,
            height=500
        )
        
        self.session = session
        self.inputs_dict = self.create_components()

        #self.on_save = on_save   IDK if i will use it (it comes from settings)

    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        self.grid_columnconfigure(0, weight=1)

        # Add inputs
        name = TextInput(
            self,
            label_text="Name"
        )
        
        winery = TextInput(
            self,
            label_text="Winery",
        )
        colour = DropdownInput(
            self,
            label_text="Colour",
            values=[colour.name.capitalize() for colour in self.session.query(Colour).all()]
        )
        style = DropdownInput(
            self,
            label_text="Style",
            values=[style.name.capitalize() for style in self.session.query(Style).all()]
        )
        varietal = TextInput(
            self,
            label_text="Varietal",
            optional=True
        )
        vintage_year = IntInput(
            self,
            label_text="Vintage Year",
            from_=0,
            to=datetime.now().year
        )
        origin = TextInput(
            self,
            label_text="Origin",
            optional=True
        )
        code = TextInput(
            self,
            label_text="Code",
        )
        wine_picture = ImageInput(
            self,
            label_text="Wine Picture",
            optional=True
        )

        inputs_dict = {
            "name": name, 
            "winery": winery, 
            "colour": colour, 
            "style": style, 
            "varietal": varietal, 
            "vintage_year": vintage_year, 
            "origin": origin, 
            "code": code,
            "wine_picture": wine_picture
        }

        for index, input in enumerate(inputs_dict.values()):
            input.grid(row=index, column=0, pady=15)
        
        # Buttons
        frame_buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        button_clear = ctk.CTkButton(
            frame_buttons,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=10,
            cursor="hand2",
            command=self.clear_inputs, # Add clear function
        )
        button_save = ctk.CTkButton(
            frame_buttons,
            text="Save",
            fg_color=Colours.BTN_SAVE,
            text_color=Colours.BG_SECONDARY,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            corner_radius=10,
            cursor="hand2",
            command=None, # Add  function
        )
        frame_buttons.grid(row=len(inputs_dict), column=0, pady=20)
        button_clear.grid(row=0, column=0)
        button_save.grid(row=0, column=1, padx=20)

        return inputs_dict

    def clear_inputs(self) -> None:
        """
        Clear the text typed or selected image by the user on the inputs.
        It doesn't clear dropdowns
        """
        confirm_dialog = messagebox.askyesno(
                "Confirm",
                "Clearing the form will discard all current inputs. Continue?"
            )
        if confirm_dialog:
            for input in self.inputs_dict.values():         
                # Still dropdown doesn't have an empty value, so it makes no sense to
                # Change its value to the first item.
                if type(input) is not DropdownInput:
                    input.clear()

    def save_values(self) -> None:
        """
        Save typed values into the db
        """
        # Iterate over each input
        
        # Get the value of the input

        # Validate it
            # If not valid break iteration and roll back operation

        # Save it in the DB    
