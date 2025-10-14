"""
Form that contain the inputs and methods to add a new wine
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from db.models import Wine, Colour, Style, Varietal
from helpers import deep_getattr
from ui.components import (TextInput, IntInput, DropdownInput, ImageInput,
    DecimalInput, ClearSaveButtons)
from ui.style import Colours, Fonts
from validators import (validate_string, validate_dropdown, validate_year,
    validate_int, validate_decimal)


class AddWineForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to ADD Wine.
    """
    def __init__(
        self, root: ctk.CTkFrame, session, wine: Wine | None = None, 
        on_save=None, **kwargs
    ):
        super().__init__(root, **kwargs)
        
        self.session = session
        self.wine = wine
        self.on_save = on_save
        self.wine_colours_dict = self.get_wine_colours_dict()
        self.wine_styles_dict = self.get_wine_style_dict()
        self.label_error = None

        self.inputs_dict = self.create_components()

    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        self.grid_columnconfigure(0, weight=1)

        frame_background = ctk.CTkFrame(
            self,
            fg_color = Colours.BG_FORM,
        )
        frame_background.grid(row=1, column=0, pady=15)
        frame_background.grid_columnconfigure(0, weight=1)

        # Add inputs
        name = TextInput(
            frame_background,
            label_text="Name"
        )
        winery = TextInput(
            frame_background,
            label_text="Winery",
        )
        colour = DropdownInput(
            frame_background,
            label_text="Colour",
            values=[""] + list(self.wine_colours_dict.keys())
        )
        style = DropdownInput(
            frame_background,
            label_text="Style",
            values=[""] + list(self.wine_styles_dict.keys())
        )
        varietal = DropdownInput(
            frame_background,
            label_text="Varietal",
            values=[""] + [v.name.title() for v in self.session.query(Varietal).all()],
            optional=True
        )
        vintage_year = IntInput(
            frame_background,
            label_text="Vintage Year",
            from_=0,
            to=datetime.now().year
        )
        origin = TextInput(
            frame_background,
            label_text="Origin",
            optional=True
        )
        code = TextInput(
            frame_background,
            label_text="Code",
        )
        wine_picture = ImageInput(
            frame_background,
            label_text="Wine Picture",
            optional=True
        )
        quantity = IntInput(
            frame_background,
            label_text="Initial Stock",
            placeholder="In bottles",
        )

        purchase_price = DecimalInput(
            frame_background,
            label_text="Purchase Price",
        )

        selling_price = DecimalInput(
            frame_background,
            label_text="Selling Price"
        )

        inputs_dict = {
            "name": name, 
            "winery": winery, 
            "colour.name": colour, 
            "style.name": style, 
            "varietal.name": varietal, 
            "vintage_year": vintage_year, 
            "origin": origin, 
            "code": code,
            "picture_path": wine_picture,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "selling_price": selling_price
        }

        for index, input in enumerate(inputs_dict.values()):
            input.set_input_width(450)
            input.grid(row=index, column=0, padx=(25, 0), pady=15)
                   
        # Error message
        self.label_error = ctk.CTkLabel(
            frame_background,
            fg_color="transparent",
            text="",
            text_color=Colours.ERROR,
            font=Fonts.TEXT_ERROR,
            width=450,
        )
        self.label_error.grid(row=len(inputs_dict), column=0, pady=5)

        # Buttons
        frame_buttons = ClearSaveButtons(
            frame_background,
            btn_clear_function=self.on_click_clear,
            btn_save_function=self.save_values
        )
        frame_buttons.enable_save_button()
        
        frame_buttons.grid(row=len(inputs_dict) + 1, column=0, pady=20)

        # Edition mode
        if self.wine:
            self.set_edition_mode(inputs_dict)
        
        return inputs_dict
    
    def get_wine_colours_dict(self) -> dict[str:int]:
        """
        Get a list of wine colours with their instances.
        Returns:
            A dict of wine colours with their instance as value.
        """
        wine_colours = self.session.query(Colour)
        return {
            f"{colour.name.title()}": colour for colour in wine_colours
        }

    def get_wine_style_dict(self) -> dict[str:int]:
        """
        Get a list of wine colours with their instances.
        Returns:
            A dict of wine colours with their instance as value.
        """
        wine_styles = self.session.query(Style)
        return {
            f"{style.name.title()}": style for style in wine_styles
        }

    def on_click_clear(self) -> None:
        """
        Asks for a clear confirmation and if accept, it clears all the inputs but
        the dropdowns.
        """
        confirm_dialog = messagebox.askyesno(
                "Confirm",
                "Clearing the form will discard all current inputs. Continue?"
            )
        if confirm_dialog:
           self.clear_inputs()

    def clear_inputs(self) -> None: 
        """
        Clear the text typed or selected image by the user on the inputs.
        It doesn't clear dropdowns.
        """
        for input in self.inputs_dict.values():         
            if type(input) is DropdownInput:
                input.set_to_first_value()
            else:    
                input.clear()

    def save_values(self) -> None:
        """
        Save typed values into the db.
        """
        # Validate inputs
        wine_attributes = self.validate_inputs()
        if not wine_attributes:
            return
        else:
            self.label_error.configure(text="")

        # Confirm saving
        if wine_attributes["purchase_price"] > wine_attributes["selling_price"]:
            save_message = (
                f"The Purchase Price is higher than the Selling Price. " 
                f"Do you want to save this wine?"
            )
        else:
            save_message = "Do you want to save this wine?"
        
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            save_message
        )
        if not confirm_dialog:
            return

        # Add wine in db
        wine_attributes["colour"] = Colour.get_name(
            self.session, name=wine_attributes["colour"]
        )
        wine_attributes["style"] = Style.get_name(
            self.session, name=wine_attributes["style"]
        )
        wine_attributes["varietal"] = Varietal.get_name(
            self.session, name=wine_attributes["varietal"]
        ) if wine_attributes["varietal"] else None
        
        try:
            # Edit wine
            if self.wine:
                for attr, val in wine_attributes.items():
                    setattr(self.wine, attr, val)
            # Create new wine
            else:
                new_wine = Wine(**wine_attributes)
                self.session.add(new_wine)
        except TypeError:
            messagebox.showinfo(
                "Error Saving",
                "Couldn't save the wine, please contact the admin. (code=1)"
            )
            return

        # Save it in the DB
        try:
            self.session.commit()
        except IntegrityError as e:
            # Rollback session
            self.session.rollback()

            # Get error message and display it to the user
            error_msg = str(e.orig)
            if "UNIQUE constraint failed" in error_msg:
                self.label_error.configure(
                    text="The code already exists. Please choose another one."
                )
            else:
                messagebox.showinfo(
                    "Error Saving",
                    "Couldn't save the wine, please contact the admin. (code=2)"
                )
            # Stop function            
            return

        # Show a success message
        messagebox.showinfo(
            "Wine Saved",
            "The wine has been successfully saved."
        )

        if self.wine:
            edit_window = self.winfo_toplevel()
            # Refresh table
            self.on_save(self.wine)
            # Close top level
            edit_window.destroy()
        else:
            # Clear all lines
            self.clear_inputs()

    
    def validate_inputs(self) -> dict | None:
        """
        Check every input and returns True if they are all validated.
        Returns:
            - True: All inputs passed the validations.
            - False: There is an input that couldn't pass the validations.
        """
        # Validate inputs
        try:
            return {
                "name": validate_string("name", self.inputs_dict["name"].get()),
                "winery": validate_string("winery", self.inputs_dict["winery"].get()),
                "colour": validate_dropdown("colour", self.inputs_dict["colour.name"].get()),
                "style": validate_dropdown("style", self.inputs_dict["style.name"].get()),
                "varietal": self.inputs_dict["varietal.name"].get().lower(), # It's optional           
                "vintage_year": validate_year("vintage year", self.inputs_dict["vintage_year"].get()),
                "origin": self.inputs_dict["origin"].get().strip(), # Optional
                "code": validate_string("code", self.inputs_dict["code"].get()),
                "picture_path": self.inputs_dict["picture_path"].get_new_path(), # Optional
                "quantity": validate_int(
                    "initial stock", self.inputs_dict["quantity"].get(), 
                    allowed_signs="positive"
                ),
                "purchase_price": validate_decimal(
                    "purchase price", self.inputs_dict["purchase_price"].get()
                ),
                "selling_price": validate_decimal(
                    "selling price", self.inputs_dict["selling_price"].get()
                )
            }
        
        # Return error message if there is no validation
        except ValueError as ve:
            self.label_error.configure(text=str(ve))
            return None
        
    def set_edition_mode(self, inputs_dict):
        """
        """
        for input_name, input in inputs_dict.items():
            # Get value
            value = deep_getattr(self.wine, input_name)
            
            if isinstance(input, DropdownInput):
                input.set_to_value(value)
            elif isinstance(input, ImageInput):
                input.set_file_path(value)
            else:
                # Text inputs
                input.update_text_value(
                    text=value
                )