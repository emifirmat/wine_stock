"""
Form that contain the inputs and methods to add a new sale
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from datetime import datetime
from PIL import Image

from ui.components import (TextInput, IntInput, Card, DropdownInput, ImageInput,
    DoubleLabel)
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine, Colour, Style

class AddSaleForm(ctk.CTkScrollableFrame):
    """
    Contains all the components and logic related to ADD Wine.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
        ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            scrollbar_button_color=Colours.BG_HOVER_NAV,
            height=500
        )
        
        # Include db
        self.session = session
        self.wine_names = self.get_wine_names()
        
        # Inputs variables
        self.wine_name_var = tk.StringVar(value=self.wine_names[0])
        self.quantity_var = tk.IntVar(value=1)
        # Listen to any change on their values
        self.quantity_var.trace_add("write", self.on_entry_change)

        # Add components
        self.inputs_dict = self.create_components()

    def get_wine_names(self) -> list[str]:
        return [wine.name.title() for wine in Wine.all_ordered(self.session)]

    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==Add Components==
        # =Inputs section=
        wine = DropdownInput(
            self,
            label_text="Wine",
            values=self.wine_names,
            variable=self.wine_name_var,
            command=self.on_entry_change, # It doesn't need variable trace
        )
        
        quantity = IntInput(
            self,
            label_text="Quantity (Bottles)",
            from_=0,
            textvariable=self.quantity_var
        )
        subtotal = DoubleLabel(
            self,
            label_title_text="Subtotal",
            label_value_text=None
        )
        
        button_add_line = ctk.CTkButton(
            self,
            text="Add Line",
            fg_color="#88B04B",
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            corner_radius=10,
            cursor="hand2",
            command=None # Has to Save the lien and clear input fields
        )
        # Save inputs for later
        inputs_dict = {
            "wine": wine, 
            "quantity": quantity, 
            "subtotal_value": subtotal, 
        }

        wine.grid(row=0, column=0, pady=20, sticky="w")
        quantity.grid(row=1, column=0, sticky="w")
        subtotal.grid(row=1, column=1, sticky="w")
        button_add_line.grid(row=2, column=0, columnspan=2, pady=20)

        # =Lines section=
        lines_frame = ctk.CTkFrame(
            self,
        )
        # TODO: IT has to include the new line and a remove button.
        
        total = DoubleLabel(
            lines_frame,
            label_title_text="Total",
            label_value_text=None
        )
        total.pack()

        lines_frame.grid(row=3, column=0)

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
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            corner_radius=10,
            cursor="hand2",
            command=None, # Add  function
        )
        frame_buttons.grid(row=4, column=0, pady=20)
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

    def on_entry_change(self, *args) -> None:
        """
        When a wine is selected or the quantity is changed, variables are updated
        """
        # Get variables
        wine = self.wine_name_var.get()
        try:
            quantity = self.quantity_var.get()
        except:
            # Catch empty entry and update process
            quantity = 0 
        print(wine)
        print(quantity)