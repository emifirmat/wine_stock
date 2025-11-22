"""
Filters form file.
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox

from db.models import Wine, Colour, Style, Varietal
from ui.components import (TextInput, IntInput, DropdownInput, ImageInput,
    DecimalInput, ClearSaveButtons, AutocompleteInput, DateInput)
from ui.style import Colours, Fonts, Icons


class BaseFiltersForm(ctk.CTkFrame):
    """
    Base class for filters forms. Handles common setup, event tracing, and clear logic.
    """
    def __init__(self, root: ctk.CTkFrame, session, filtered_table, **kwargs):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color=Colours.BG_FORM,
            border_width=1,
            border_color=Colours.BORDERS
        )

        # Db session and table to filter
        self.session = session
        self.filtered_table = filtered_table
        self.inputs_dict = {}
        self.vars_dict = {}

        # Components
        self.background = None
        self.filters_visible = False
        self.create_components()
        self.create_filter_fields()
        self.add_variable_traces()
        self.fields_container.grid_remove() # Start with hidden filters

    def create_components(self):
        """
        Implemented by subclasses. Must define `self.inputs_dict` and 
        `self.vars_dict`.
        """
        # ==Common Components==
        top_container = ctk.CTkFrame(self, fg_color="transparent")
        top_container.grid(row=0, column=0, padx=2, pady=(20, 10), sticky="we")
        
        # Title
        ctk.CTkLabel(
            top_container,
            text="Filters",
            font=Fonts.SUBTITLE,
            text_color=Colours.TEXT_MAIN,
            anchor="center",
        ).grid(row=0, column=0, padx=2, pady=5, sticky="e")
        # Toggle button
        self.btn_toggle = ctk.CTkButton(
            top_container,
            image=Icons.EXPAND,
            fg_color="transparent",
            hover_color=Colours.BG_FORM,
            text="",
            cursor="hand2",
            width=20,
            command=self.toggle_filters
        )
        self.btn_toggle.grid(row=0, column=1, padx=2, pady=5, sticky="w")
        # Background
        self.fields_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        self.fields_container.grid(row=1, column=0, columnspan=2, pady=(0,2))

        self.grid_columnconfigure(0, weight=1)
        top_container.grid_columnconfigure(0, weight=1)
        top_container.grid_columnconfigure(1, weight=1)
        
        
    def create_filter_fields(self):
        """
        Implemented by subclasses. Must define `self.inputs_dict` and 
        `self.vars_dict`.
        """
        raise NotImplementedError

    def trigger_filters(self):
        """
        Called when user changes a filter input. Implemented by subclasses.
        """
        raise NotImplementedError

    def add_variable_traces(self):
        """
        Attach trace listeners for all tk variables in vars_dict.
        """
        for var in self.vars_dict.values():
            if isinstance(var, tk.Variable):
                var.trace_add("write", self.on_entry_change)

    def on_entry_change(self, *args):
        """
        Triggered whenever any tk variable changes.
        """
        self.trigger_filters()

    def clear_inputs(self):
        """
        Reset all inputs.
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Remove all current filters?"
        )
        if not confirm_dialog:
            return
        
        for key, input in self.inputs_dict.items():
            if not isinstance(input, DropdownInput):
                input.clear()
            else:
                input.set_to_first_value

        self.trigger_filters()

    def toggle_filters(self):
        if self.filters_visible:
            self.fields_container.grid_remove()
            self.btn_toggle.configure(
                image=Icons.EXPAND,
                text="",
            )
        else:
            self.fields_container.grid()
            self.btn_toggle.configure(
                image=Icons.COLLAPSE,
                text="",
            )
            
        self.filters_visible = not self.filters_visible
        

class TransactionFiltersForm(BaseFiltersForm):
    """
    Contains the components and logic for filtering the Transactions table.
    """       
    def create_filter_fields(self) -> list:
        """
        Create the filters and table.

        Returns:
            A list containing all the created filters in the form.
        """
        # DB lists
        self.update_lists()

        # TK variables
        self.vars_dict = {
            "name": tk.StringVar(),
            "code": tk.StringVar(),
            "date_from": tk.StringVar(),
            "date_to": tk.StringVar(),
        }

        # Components
        autocomplete_wine = AutocompleteInput(
            self.fields_container,
            label_text="Wine",
            item_list=self.wine_names_list,
            textvariable=self.vars_dict["name"],
            optional=True
        )
    
        autocomplete_code = AutocompleteInput(
            self.fields_container,
            label_text="Code",
            item_list=self.wine_codes_list,
            textvariable=self.vars_dict["code"],
            optional=True
        )

        dropdown_transaction = DropdownInput(
            self.fields_container,
            label_text="Transaction",
            values=["", "Purchase", "Sale"],
            optional=True,
            command=self.on_entry_change, # It doesn't need variable trace
        )

        input_from_date = DateInput(
            self.fields_container,
            label_text="From",
            textvariable=self.vars_dict["date_from"],
            optional=True,
        )
        
        input_to_date = DateInput(
            self.fields_container,
            label_text="To",
            textvariable=self.vars_dict["date_to"],
            optional=True,
        )

        autocomplete_wine.grid(row=0, column=0, padx=5, pady=(0, 20), sticky="w")
        autocomplete_code.grid(row=0, column=1, padx=5, pady=(0, 20))
        dropdown_transaction.grid(row=0, column=2, padx=(5, 2), pady=(0, 20))
        input_from_date.grid(row=1, column=0, padx=5, pady=(0, 20))
        input_to_date.grid(row=1, column=1, padx=5, pady=(0, 20))

        # Save input references
        self.inputs_dict = {
            "wine": autocomplete_wine, 
            "code": autocomplete_code, 
            "transaction": dropdown_transaction,
            "input_from_date": input_from_date,
            "input_to_date": input_to_date,
        }

        for input_name, input in self.inputs_dict.items():
            if input_name == "transaction":
                label_width = 100    
            else:
                label_width = 60    
            input.set_label_layout(label_width)
            input.set_total_width(300)

        # Clear button
        button_clear = ctk.CTkButton(
            self.fields_container,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=10,
            cursor="hand2",
            command=self.clear_inputs,
        )
        button_clear.grid(row=1, column=2, padx=5, pady=(0, 20))

    def trigger_filters(self, *args) -> None:
        """
        When the user types on an input, the variables and the table get updated.
        """
        # Get variables
        name = self.vars_dict["name"].get().strip().lower()
        code = self.vars_dict["code"].get().strip().lower()
        transaction_type = self.inputs_dict["transaction"].get().strip().lower()
        date_from = self.vars_dict["date_from"].get().strip().lower()
        date_to = self.vars_dict["date_to"].get().strip()
        
        # Get wines that matches what the user typed
        filtered_names = [
            wn.lower() for wn in self.wine_names_list 
            if name in wn.lower()
        ]
        filtered_codes = [
            wc.lower() for wc in self.wine_codes_list 
            if code in wc.lower()
        ]

        # If there is no match, stop the function
        if not any([
            filtered_names, filtered_codes, transaction_type, date_from, date_to
        ]):
            return

        # Else, update the table
        self.filtered_table.apply_filters(
            filtered_names, filtered_codes, transaction_type, date_from, date_to
        )

    def update_lists(self):
        """
        Updates the lists of wines.
        """
        self.wine_names_list = [
            wine.name for wine in Wine.column_ordered(self.session, "name", "name")
        ]
        self.wine_codes_list = [
            wine.code for wine in Wine.column_ordered(self.session, "code", "code")
        ]

    
class WineFiltersForm(BaseFiltersForm):
    """
    Contains all the components and logic for filtering the Wines table.
    """        
    def create_filter_fields(self) -> list:
        """
        Create the filters and table.

        Returns:
            A list containing all the created filters in the form.
        """
        # DB lists
        self.update_lists()

        # TK variables
        self.vars_dict = {
            "name": tk.StringVar(),
            "code": tk.StringVar(),
            "winery": tk.StringVar(),
            "origin": tk.StringVar(),
            "year": tk.StringVar(),
        }

        # Components
        autocomplete_wine = AutocompleteInput(
            self.fields_container,
            label_text="Wine",
            item_list=self.wine_names_list,
            textvariable=self.vars_dict["name"],
            optional=True
        )
    
        autocomplete_code = AutocompleteInput(
            self.fields_container,
            label_text="Code",
            item_list=self.wine_codes_list,
            textvariable=self.vars_dict["code"],
            optional=True
        )

        autocomplete_winery = AutocompleteInput(
            self.fields_container,
            label_text="Winery",
            item_list=self.wine_winery_list,
            textvariable=self.vars_dict["winery"],
            optional=True
        )

        dropdown_colours = DropdownInput(
            self.fields_container,
            label_text="Colour",
            values=[""] + [
                w_colour.name.capitalize()
                for w_colour in self.session.query(Colour).all()
            ],
            optional=True,
            command=self.on_entry_change, # It doesn't need variable trace
        )

        dropdown_styles = DropdownInput(
            self.fields_container,
            label_text="Style",
            values=[""] + [
                style.name.capitalize() 
                for style in self.session.query(Style).all()
            ],
            optional=True,
            command=self.on_entry_change,
        )
        
        dropdown_varietals = DropdownInput(
            self.fields_container,
            label_text="Varietal",
            values=[""] + [
                varietal.name.capitalize() 
                for varietal in self.session.query(Varietal).all()
            ],
            optional=True,
            command=self.on_entry_change,
        )

        input_year = IntInput(
            self.fields_container,
            label_text="Year",
            textvariable=self.vars_dict["year"],
            optional=True
        )

        autocomplete_origin = AutocompleteInput(
            self.fields_container,
            label_text="Origin",
            item_list=self.wine_origin_list,
            textvariable=self.vars_dict["origin"],
            optional=True
        )

        autocomplete_wine.grid(row=0, column=0, padx=5, pady=(0, 20), sticky="w")
        autocomplete_code.grid(row=0, column=1, padx=5, pady=(0, 20))
        autocomplete_winery.grid(row=0, column=2, padx=(5, 2), pady=(0, 20))
        dropdown_colours.grid(row=1, column=0, padx=5, pady=(0, 20))
        dropdown_styles.grid(row=1, column=1, padx=5, pady=(0, 20))
        dropdown_varietals.grid(row=1, column=2, padx=(5, 2), pady=(0, 20))
        input_year.grid(row=2, column=0, padx=5, pady=(0, 20))
        autocomplete_origin.grid(row=2, column=1, padx=5, pady=(0, 20))

        # Save input references
        self.inputs_dict = {
            "wine": autocomplete_wine, 
            "code": autocomplete_code, 
            "winery": autocomplete_winery,
            "colour": dropdown_colours,
            "style": dropdown_styles,
            "varietal": dropdown_varietals,
            "year": input_year,
            "origin": autocomplete_origin
        }

        for _, input in self.inputs_dict.items():
            input.set_label_layout(60)
            input.set_total_width(300)

        # Clear button
        button_clear = ctk.CTkButton(
            self.fields_container,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=10,
            cursor="hand2",
            command=self.clear_inputs,
        )
        button_clear.grid(row=2, column=2, padx=5, pady=(0, 20))

    def trigger_filters(self, *args) -> None:
        """
        When the user types on an input, the variables and the table get updated.
        """
        # Get variables
        name = self.vars_dict["name"].get().strip().lower()
        code = self.vars_dict["code"].get().strip().lower()
        winery = self.vars_dict["winery"].get().strip().lower()
        origin = self.vars_dict["origin"].get().strip().lower()
        year = self.vars_dict["year"].get().strip()

        colour = self.inputs_dict["colour"].get().strip()
        style = self.inputs_dict["style"].get().strip()
        varietal = self.inputs_dict["varietal"].get().strip()
        
        # Get wines that matches what the user typed
        self.filtered_names = [
            wn.lower() for wn in self.wine_names_list 
            if name in wn.lower()
        ]
        self.filtered_codes = [
            wc.lower() for wc in self.wine_codes_list 
            if code in wc.lower()
        ]
        self.filtered_wineries = [
            ww.lower() for ww in self.wine_winery_list 
            if winery in ww.lower()
        ]
        self.filtered_origin = [
            wo.lower() for wo in self.wine_origin_list 
            if origin in wo.lower()
        ]
        
        # If there is no match, stop the function
        if not any([
            self.filtered_names, self.filtered_codes, self.filtered_wineries, 
            colour, style, varietal, year, self.filtered_origin
        ]):
            return

        # Else, update the table
        self.filtered_table.apply_filters(
            self.filtered_names, self.filtered_codes, self.filtered_wineries, colour, 
            style, varietal, year, self.filtered_origin
        )

    def update_lists(self):
        """
        Updates the lists of wines.
        """
        self.wine_names_list = [
            w.name for w in Wine.column_ordered(self.session, "name", "name")
        ]
        self.wine_codes_list = [
            w.code for w in Wine.column_ordered(self.session, "code", "code")
        ]
        self.wine_winery_list = [
            w.winery for w in Wine.column_ordered(self.session, "winery", "winery", "winery")
        ]
        self.wine_origin_list = [
            w.origin for w in Wine.column_ordered(self.session, "origin", "origin", "origin")
        ]