"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from datetime import datetime
from decimal import Decimal
from PIL import Image

from ui.components import (TextInput, IntInput, Card, DropdownInput, ImageInput,
    DoubleLabel)
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine, Colour, Style, StockMovement

class MovementsTable(ctk.CTkScrollableFrame):
    """
    Contains the components of the table with the wine purchases and sellings.
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
        
        # Include db instances
        self.session = session
        self.wine_names_dict = self.get_wine_names_dict()
        self.wine_names_list = list(self.wine_names_dict.keys())
        
        # TK variables
        self.wine_name_var = tk.StringVar(value=self.wine_names_list[0])
        self.quantity_var = tk.IntVar(value=1)
        self.total_var = tk.StringVar(value=f"€ 0.00")
        # Listen to any change on their values
        self.quantity_var.trace_add("write", self.on_entry_change)

        self.subtotal_value = None
        self.line_counter = 0
        self.line_list = [] # It contains dicts

        # Add components
        self.dropdown_wine = None
        self.textbox_quantity = None
        self.label_subtotal = None
        self.frame_lines = None
        self.button_clear = None
        self.button_save = None
        self.inputs_dict = self.create_components()
        self.on_entry_change() # Initial subtotal label update

    def get_wine_names_dict(self) -> dict[str:int]:
        """
        Get a list of wine names with their instances.
        Returns:
            A dict of wine names with their instance as value.
        """
        wines = Wine.all_ordered(self.session)
        return {
            f"{wine.name.title()}": wine for wine in wines
        }

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
        self.dropdown_wine = DropdownInput(
            self,
            label_text="Wine",
            values=self.wine_names_list,
            variable=self.wine_name_var,
            command=self.on_entry_change, # It doesn't need variable trace
        )
        
        self.textbox_quantity = IntInput(
            self,
            label_text="Quantity (Bottles)",
            from_=0,
            textvariable=self.quantity_var
        )
        self.label_subtotal = DoubleLabel(
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
            command=self.add_new_wine_line 
        )
        # Save inputs for later
        inputs_dict = {
            "wine": self.dropdown_wine, 
            "quantity": self.textbox_quantity, 
        }

        self.dropdown_wine.grid(row=0, column=0, pady=20, sticky="w", columnspan=2)
        self.textbox_quantity.grid(row=1, column=0, sticky="w")
        self.label_subtotal.grid(row=1, column=1, sticky="w")
        button_add_line.grid(row=2, column=0, columnspan=2, pady=20)

        # =Lines section=
        self.frame_lines = ctk.CTkFrame(
            self,
            fg_color=Colours.BG_MAIN
        )
        
        frame_headers = ctk.CTkFrame(
            self.frame_lines,
            fg_color="transparent"
        )

        header_invisible = ctk.CTkLabel(
            frame_headers,
            text=" ",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_HEADER,
            #anchor="w",
            width=30,
            
        )
        header_invisible.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        header_name = ctk.CTkLabel(
            frame_headers,
            text="Name",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_HEADER,
            #anchor="w",
            width=300,
            
        )
        header_name.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        for i, header in enumerate(["Quantity", "Price", "Subtotal"], start=2):
            label_header = ctk.CTkLabel(
                frame_headers,
                text=header,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                #anchor="w",
                width=100,
                
            )

            label_header.grid(row=0, column=i, padx=(0, 20))
        
        header_invisible = ctk.CTkLabel(
            frame_headers,
            text=" ",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_HEADER,
            width=30,
        )
        header_invisible.grid(row=0, column=6, sticky="w", padx=(0, 20))

        frame_headers.pack(pady=(10))

        total = DoubleLabel(
            self.frame_lines,
            label_title_text="Total",
            text_variable=self.total_var
        )
        total.label_value.configure(font=Fonts.TEXT_HEADER)
        total.pack(side="bottom", anchor="se")

        self.frame_lines.grid(row=3, column=0, columnspan=2)

        # =Buttons=
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
            command=self.clear_inputs,
        )
        self.button_save = ctk.CTkButton(
            frame_buttons,
            text="Save",
            fg_color=Colours.BTN_SAVE,
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            corner_radius=10,
            state="disabled",
            command=self.save_values, 
        )
        frame_buttons.grid(row=4, column=0, pady=20, columnspan=2)
        button_clear.grid(row=0, column=0)
        self.button_save.grid(row=0, column=1, padx=20)

        return inputs_dict