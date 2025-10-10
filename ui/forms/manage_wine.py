"""
Form that contain the inputs and methods to add a new sale
"""
import customtkinter as ctk
from datetime import datetime, timedelta
import tkinter as tk
import tkinter.messagebox as messagebox
from decimal import Decimal

from ui.components import (IntInput, DropdownInput, DoubleLabel, AutoCompleteInput,
    ClearSaveButtons, DateInput)
from ui.style import Colours, Fonts
from ui.tables.wines_table import WinesTable
from db.models import Wine, Colour, Style, Varietal

class ShowWineForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to show wines details.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
        ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(height=500)
        
        # Include db instances
        self.session = session
        self.wine_names_dict = self.get_wine_names_dict()
        self.wine_names_list = list(self.wine_names_dict.keys()) # ordered
        self.wine_codes_list = [
            wine.code for wine in Wine.column_ordered(self.session, "code", "code")
        ]
        self.wine_winery_list = [
            wine.winery 
            for wine in Wine.column_ordered(self.session, "winery", "winery", "winery")
        ]
        self.wine_origin_list = [
            wine.origin 
            for wine in Wine.column_ordered(self.session, "origin", "origin", "origin")
        ]

        # TK variables
        self.wine_name_var = tk.StringVar()
        self.wine_code_var = tk.StringVar()
        self.wine_winery_var = tk.StringVar()
        self.wine_varietal_var = tk.StringVar()
        self.wine_year_var = tk.StringVar()
        self.wine_origin_var = tk.StringVar()
       
        # Listen to any change on their values
        self.wine_name_var.trace_add("write", self.on_entry_change)
        self.wine_code_var.trace_add("write", self.on_entry_change)
        self.wine_winery_var.trace_add("write", self.on_entry_change)
        self.wine_varietal_var.trace_add("write", self.on_entry_change)
        self.wine_year_var.trace_add("write", self.on_entry_change)
        self.wine_origin_var.trace_add("write", self.on_entry_change)

        # Add components
        self.wines_table = None
        self.frame_lines = None
        self.frame_buttons = None
        self.inputs_dict = self.create_components()

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
        Create the filters and table.

        Returns:
            A list containing all the created filters in the form.
        """
        self.grid_columnconfigure(0, weight=1)
    
        # ==Filters section==
        filter_frame = ctk.CTkFrame(
            self,
            fg_color ="transparent",
            border_width=1,
            border_color=Colours.BORDERS
        )

        filter_frame.grid(row=0, column=0, pady=20, sticky="we")
        
        section_title= ctk.CTkLabel(
            filter_frame,
            text="Filters",
            font=Fonts.SUBTITLE,
            text_color=Colours.TEXT_MAIN,
            anchor="center"
        )

        section_title.grid(
            row=0, column=0, padx=2, pady=20, columnspan=4, sticky="wen"
        )

        autocomplete_wine = AutoCompleteInput(
            filter_frame,
            label_text="Wine",
            item_list=self.wine_names_list,
            textvariable=self.wine_name_var,
            optional=True
        )
     
        autocomplete_code = AutoCompleteInput(
            filter_frame,
            label_text="Code",
            item_list=self.wine_codes_list,
            textvariable=self.wine_code_var,
            optional=True
        )

        autocomplete_winery = AutoCompleteInput(
            filter_frame,
            label_text="Winery",
            item_list=self.wine_winery_list,
            textvariable=self.wine_winery_var,
            optional=True
        )

        dropdown_colours = DropdownInput(
            filter_frame,
            label_text="Colour",
            values=[""] + [
                w_colour.name.capitalize()
                for w_colour in self.session.query(Colour).all()
            ],
            optional=True,
            command=self.on_entry_change, # It doesn't need variable trace
        )

        dropdown_styles = DropdownInput(
            filter_frame,
            label_text="Style",
            values=[""] + [
                style.name.capitalize() 
                for style in self.session.query(Style).all()
            ],
            optional=True,
            command=self.on_entry_change,
        )
        
        dropdown_varietals = DropdownInput(
            filter_frame,
            label_text="Varietal",
            values=[""] + [
                varietal.name.capitalize() 
                for varietal in self.session.query(Varietal).all()
            ],
            optional=True,
            command=self.on_entry_change,
        )

        input_year = IntInput(
            filter_frame,
            label_text="Year",
            textvariable=self.wine_year_var,
            optional=True
        )

        autocomplete_origin = AutoCompleteInput(
            filter_frame,
            label_text="Origin",
            item_list=self.wine_origin_list,
            textvariable=self.wine_origin_var,
            optional=True
        )

        autocomplete_wine.grid(row=1, column=0, padx=5, pady=(0, 20), sticky="w")
        autocomplete_code.grid(row=1, column=1, padx=5, pady=(0, 20))
        autocomplete_winery.grid(row=1, column=2, padx=(5, 2), pady=(0, 20))
        dropdown_colours.grid(row=2, column=0, padx=5, pady=(0, 20))
        dropdown_styles.grid(row=2, column=1, padx=5, pady=(0, 20))
        dropdown_varietals.grid(row=2, column=2, padx=(5, 2), pady=(0, 20))
        input_year.grid(row=3, column=0, padx=5, pady=(0, 20))
        autocomplete_origin.grid(row=3, column=1, padx=5, pady=(0, 20))

        # Save inputs for later
        inputs_dict = {
            "wine": autocomplete_wine, 
            "code": autocomplete_code, 
            "winery": autocomplete_winery,
            "colour": dropdown_colours,
            "style": dropdown_styles,
            "varietal": dropdown_varietals,
            "year": input_year,
            "origin": autocomplete_origin
        }

        # Clear button
        button_clear = ctk.CTkButton(
            filter_frame,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=10,
            cursor="hand2",
            command=self.clear_inputs,
        )
        button_clear.grid(row=3, column=2, padx=5, pady=(0, 20))

        # ==Table section==
        self.wines_table = WinesTable(
            self,
            self.session,
            headers=[
                "code", "picture", "name", "vintage year", "origin", "quantity",
                "purchase price", "selling price", "actions"
            ],
            lines=Wine.all_ordered(self.session)
        )
        self.wines_table.grid(row=1, column=0, pady=(10, 20), sticky="nsew")

        return inputs_dict

    def clear_inputs(self) -> None:
        """
        Clear the text typed by the user on the inputs and eet dropdowns to 
        their first value.
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Remove all current filters?"
        )
        if not confirm_dialog:
            return
        
        for input in self.inputs_dict.values():         
            if type(input) is not DropdownInput:
                input.clear()
            else:
                input.set_to_first_value()
        
        # Update table
        self.on_entry_change()


    def on_entry_change(self, *args) -> None:
        """
        When a the user types on any inputs, variables are updated and filters
        reviewed to update the table.
        """
        # Get variables
        wine_name = self.wine_name_var.get().strip().lower()
        wine_code = self.wine_code_var.get().strip().lower()
        winery = self.wine_winery_var.get().strip().lower()
        wine_colour = self.inputs_dict["colour"].get().strip()
        wine_style = self.inputs_dict["style"].get().strip()
        wine_varietal = self.inputs_dict["varietal"].get().strip()
        wine_year = self.wine_year_var.get().strip().lower()
        wine_origin = self.wine_origin_var.get().strip().lower()
  
        
        # Get wines that matches what the user typed
        filtered_names = [
            wn.lower() for wn in self.wine_names_list 
            if wine_name in wn.lower()
        ]
        filtered_codes = [
            wc.lower() for wc in self.wine_codes_list 
            if wine_code in wc.lower()
        ]
        filtered_wineries = [
            ww.lower() for ww in self.wine_winery_list 
            if winery in ww.lower()
        ]
        filtered_origin = [
            wo.lower() for wo in self.wine_origin_list 
            if wine_origin in wo.lower()
        ]

        # If there is no match, stop the function
        if (len(filtered_names) == 0 
            and len(filtered_codes) == 0
            and winery == 0
            and wine_colour == ""
            and wine_style == ""
            and wine_varietal == ""
            and wine_year == ""
            and len(filtered_origin) == 0
        ):
            return

        # else, update the table
        self.wines_table.apply_filters(
            filtered_names, filtered_codes, filtered_wineries, wine_colour, 
            wine_style, wine_varietal, wine_year, filtered_origin
        )
