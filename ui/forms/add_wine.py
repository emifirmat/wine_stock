"""
Form that contain the inputs and methods to add a new wine
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime

from ui.components import (TextInput, IntInput, DropdownInput, ImageInput,
    DecimalInput)
from ui.style import Colours, Fonts
from models import Wine, Colour, Style, Varietal

class AddWineForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to ADD Wine.
    """
    def __init__(self, root: ctk.CTkFrame, session, **kwargs):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            height=500
        )
        
        self.session = session
        self.wine_colours_dict = self.get_wine_colours_dict()
        self.wine_styles_dict = self.get_wine_style_dict()

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
            values=list(self.wine_colours_dict.keys())
        )
        style = DropdownInput(
            self,
            label_text="Style",
            values=list(self.wine_styles_dict.keys())
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

        quantity = IntInput(
            self,
            label_text="Initial Stock",
            placeholder="In bottles",
        )

        purchase_price = DecimalInput(
            self,
            label_text="Purchase Price",
        )

        selling_price = DecimalInput(
            self,
            label_text="Selling Price"
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
            "wine_picture": wine_picture,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "selling_price": selling_price
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
            command=self.on_click_clear, 
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
            command=self.save_values,
        )
        frame_buttons.grid(row=len(inputs_dict), column=0, columnspan=2, pady=20)
        button_clear.grid(row=0, column=0)
        button_save.grid(row=0, column=1, padx=20)

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
            # Still dropdown doesn't have an empty value, so it makes no sense to
            # Change its value to the first item.
            if type(input) is not DropdownInput:
                input.clear()

    def save_values(self) -> None:
        """
        Save typed values into the db
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Do you want to save this wine?"
        )
        if not confirm_dialog:
            return
            
        # Add wine in db
        wine = Wine(
            name=self.inputs_dict["name"].get(),
            winery=self.inputs_dict["winery"].get(),
            colour=self.wine_colours_dict[self.inputs_dict["colour"].get()],
            style=self.wine_styles_dict[self.inputs_dict["style"].get()],
            varietal=Varietal.get_or_create(self.session, name=self.inputs_dict["varietal"].get()),
            vintage_year=self.inputs_dict["vintage_year"].get(),
            origin=self.inputs_dict["origin"].get(),
            code=self.inputs_dict["code"].get(),
            wine_picture_path=self.inputs_dict["wine_picture"].get_new_path(),
            quantity=self.inputs_dict["quantity"].get(),
            purchase_price=self.inputs_dict["purchase_price"].get(),
            selling_price=self.inputs_dict["selling_price"].get(),
        )

        # Save it in the DB    
        self.session.add(wine)
        self.session.commit()

        # Show a message
        messagebox.showinfo(
            "Wine Saved",
            "The wine has been successfully saved."
        )

        # Clear all lines
        self.clear_inputs()
