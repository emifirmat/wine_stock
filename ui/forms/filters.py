"""
Filter forms for table data filtering.

This module provides base and specialized filter forms for filtering
table data by various criteria. Includes collapsible filter panels
and automatic table updates on filter changes.
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from sqlalchemy.orm import Session

from db.models import Wine, Colour, Style, Varietal
from ui.components import IntInput, DropdownInput,AutocompleteInput, DateInput
from ui.style import Colours, Fonts, Icons, Spacing, Rounding


class BaseFiltersForm(ctk.CTkFrame):
    """
    Base class for collapsible filter forms.
    
    Provides common functionality for filter forms including toggle visibility,
    variable tracing, and filter clearing. Subclasses must implement
    create_filter_fields() and trigger_filters().
    """
    def __init__(self, root: ctk.CTkFrame, session: Session, filtered_table, **kwargs):
        """
        Initialize base filters form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            filtered_table: Table instance to apply filters to
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(
            fg_color=Colours.BG_FORM,
            border_width=1,
            border_color=Colours.BORDERS
        )

        # DB session and target table
        self.session = session
        self.filtered_table = filtered_table
        self.inputs_dict = {}
        self.vars_dict = {}

        # UI state
        self.filters_visible = False
        self.fields_container = None
        self.btn_toggle = None

        # Build components
        self.create_components()
        self.create_filter_fields()
        self.add_variable_traces()
        self.fields_container.grid_remove() # Start with hidden filters

    def create_components(self) -> None:
        """
        Create common filter form components (title and toggle button).
        """
        # Create top container
        top_container = ctk.CTkFrame(self, fg_color="transparent")
        top_container.grid(
            row=0, column=0, 
            padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y, sticky="we"
        )
        
        # Create title label
        ctk.CTkLabel(
            top_container,
            text="Filters",
            font=Fonts.SUBTITLE,
            text_color=Colours.TEXT_MAIN,
            anchor="center",
        ).grid(
            row=0, column=0, 
            padx=Spacing.TITLE_X, pady=Spacing.TITLE_Y, sticky="e"
        )
        # Create toggle button
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
        self.btn_toggle.grid(
            row=0, column=1, 
            padx=Spacing.BUTTON_X, pady=Spacing.TITLE_Y, sticky="w"
        )
        
        # Create fields container (initially hidden)
        self.fields_container = ctk.CTkFrame(self, fg_color="transparent")
        self.fields_container.grid(
            row=1, column=0, columnspan=2, 
            padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y
        )

        # Configure grid responsiveness
        self.grid_columnconfigure(0, weight=1)
        top_container.grid_columnconfigure(0, weight=1)
        top_container.grid_columnconfigure(1, weight=1)
        
        
    def create_filter_fields(self) -> None:
        """
        Create filter input fields.
        
        Must be implemented by subclasses to define specific filter inputs.
        Should populate self.inputs_dict and self.vars_dict.
        """
        raise NotImplementedError("Subclasses must implement create_filter_fields()")

    def trigger_filters(self) -> None:
        """
        Apply current filter values to table.
        
        Must be implemented by subclasses to extract filter values
        and apply them to the filtered_table.
        """
        raise NotImplementedError

    def add_variable_traces(self) -> None:
        """
        Attach change listeners to all Tk variables.
        """
        for var in self.vars_dict.values():
            if isinstance(var, tk.Variable):
                var.trace_add("write", self.on_entry_change)

    def on_entry_change(self, *args) -> None:
        """
        Handle input change event.
        
        Parameters:
            *args: Trace callback arguments (unused but required by trace_add)
        """
        self.trigger_filters()

    def clear_inputs(self) -> None:
        """
        Clear all filter inputs after user confirmation.
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Remove all current filters?"
        )
        if not confirm_dialog:
            return
        
        # Clear all inputs
        for input_widget in self.inputs_dict.values():
            if isinstance(input_widget, DropdownInput):
                input_widget.set_to_first_value()
            else:
                input_widget.clear()

        # Reapply filters (will show all data)
        self.trigger_filters()

    def toggle_filters(self) -> None:
        """
        Toggle visibility of filter fields.
        """
        if self.filters_visible:
            self.fields_container.grid_remove()
            self.btn_toggle.configure(image=Icons.EXPAND)
        else:
            self.fields_container.grid()
            self.btn_toggle.configure(image=Icons.COLLAPSE)
            
        self.filters_visible = not self.filters_visible
        

class TransactionFiltersForm(BaseFiltersForm):
    """
    Filter form for transactions table.
    
    Provides filters for wine name, code, transaction type, and date range.
    """       
    def create_filter_fields(self) -> None:
        """
        Create transaction-specific filter inputs.
        """
        # Load wine data
        self.update_lists()

        # Create Tk variables
        self.vars_dict = {
            "name": tk.StringVar(),
            "code": tk.StringVar(),
            "date_from": tk.StringVar(),
            "date_to": tk.StringVar(),
        }

        # Create filter inputs
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
            command=self.on_entry_change, # It doesn't need trace
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

        # Position inputs
        autocomplete_wine.grid(
            row=0, column=0, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y), sticky="w"
        )
        
        autocomplete_code.grid(
            row=0, column=1, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        
        dropdown_transaction.grid(
            row=0, column=2, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        
        input_from_date.grid(
            row=1, column=0, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        
        input_to_date.grid(
            row=1, column=1, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )

        # Store input references
        self.inputs_dict = {
            "wine": autocomplete_wine, 
            "code": autocomplete_code, 
            "transaction": dropdown_transaction,
            "input_from_date": input_from_date,
            "input_to_date": input_to_date,
        }

        # Configure input widths
        for input_name, input_widget in self.inputs_dict.items():
            label_width = 100 if input_name == "transaction" else 60
            input_widget.set_label_layout(label_width)
            input_widget.set_total_width(300)

        # Create clear button
        button_clear = ctk.CTkButton(
            self.fields_container,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=Rounding.BUTTON,
            cursor="hand2",
            command=self.clear_inputs,
        )
        button_clear.grid(
            row=1, column=2, 
            padx=Spacing.BUTTON_X, pady=(0, Spacing.BUTTON_Y)
        )

    def trigger_filters(self, *args) -> None:
        """
        Apply transaction filters to table.
        
        Parameters:
            *args: Trace callback arguments (unused but required by trace_add)
        """
        # Get filter values
        name = self.vars_dict["name"].get().strip().lower()
        code = self.vars_dict["code"].get().strip().lower()
        transaction_type = self.inputs_dict["transaction"].get().strip().lower()
        date_from = self.vars_dict["date_from"].get().strip()
        date_to = self.vars_dict["date_to"].get().strip()
        
        # Get matching wines
        filtered_names = [
            wn.lower() for wn in self.wine_names_list 
            if name in wn.lower()
        ]
        filtered_codes = [
            wc.lower() for wc in self.wine_codes_list 
            if code in wc.lower()
        ]

        # Only apply filters if at least one filter is set
        if not any([
            filtered_names, filtered_codes, transaction_type, date_from, date_to
        ]):
            return

        # Apply filters to table
        self.filtered_table.apply_filters(
            filtered_names, filtered_codes, transaction_type, date_from, date_to
        )

    def update_lists(self) -> None:
        """
        Update autocomplete lists with current wine data.
        """
        self.wine_names_list = [
            wine.name for wine in Wine.column_ordered(self.session, "name", "name")
        ]
        self.wine_codes_list = [
            wine.code for wine in Wine.column_ordered(self.session, "code", "code")
        ]

    
class WineFiltersForm(BaseFiltersForm):
    """
    Filter form for wines table.
    
    Provides filters for wine attributes including name, code, winery, colour, 
    style, varietal, year, and origin.
    """        
    def create_filter_fields(self) -> None:
        """
        Create wine-specific filter inputs.
        """
        # Load wine data
        self.update_lists()

        # Create Tk variables
        self.vars_dict = {
            "name": tk.StringVar(),
            "code": tk.StringVar(),
            "winery": tk.StringVar(),
            "origin": tk.StringVar(),
            "year": tk.StringVar(),
        }

        # Create filter inputs
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
                colour.name.capitalize()
                for colour in self.session.query(Colour).all()
            ],
            optional=True,
            command=self.on_entry_change
        )

        dropdown_styles = DropdownInput(
            self.fields_container,
            label_text="Style",
            values=[""] + [
                style.name.capitalize() 
                for style in self.session.query(Style).all()
            ],
            optional=True,
            command=self.on_entry_change
        )
        
        dropdown_varietals = DropdownInput(
            self.fields_container,
            label_text="Varietal",
            values=[""] + [
                varietal.name.capitalize() 
                for varietal in self.session.query(Varietal).all()
            ],
            optional=True,
            command=self.on_entry_change
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

        autocomplete_wine.grid(
            row=0, column=0, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y), sticky="w"
        )
        autocomplete_code.grid(
            row=0, column=1, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        autocomplete_winery.grid(
            row=0, column=2, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        dropdown_colours.grid(
            row=1, column=0, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        dropdown_styles.grid(
            row=1, column=1, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        dropdown_varietals.grid(
            row=1, column=2, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        input_year.grid(
            row=2, column=0, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )
        autocomplete_origin.grid(
            row=2, column=1, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )

        # Store input references
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

        # Configure input widths
        for input_widget in self.inputs_dict.values():
            input_widget.set_label_layout(60)
            input_widget.set_total_width(300)

        # Create clear button
        button_clear = ctk.CTkButton(
            self.fields_container,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=Rounding.BUTTON,
            cursor="hand2",
            command=self.clear_inputs,
        )
        button_clear.grid(
            row=2, column=2, 
            padx=Spacing.LABEL_X, pady=(0, Spacing.LABEL_Y)
        )

    def trigger_filters(self, *args) -> None:
        """
        Apply wine filters to table.
        
        Parameters:
            *args: Trace callback arguments (unused but required by trace_add)
        """
        # Get filter values
        name = self.vars_dict["name"].get().strip().lower()
        code = self.vars_dict["code"].get().strip().lower()
        winery = self.vars_dict["winery"].get().strip().lower()
        origin = self.vars_dict["origin"].get().strip().lower()
        year = self.vars_dict["year"].get().strip()

        colour = self.inputs_dict["colour"].get().strip()
        style = self.inputs_dict["style"].get().strip()
        varietal = self.inputs_dict["varietal"].get().strip()
        
        # Get matching wines
        filtered_names = [
            wn.lower() for wn in self.wine_names_list 
            if name in wn.lower()
        ]
        filtered_codes = [
            wc.lower() for wc in self.wine_codes_list 
            if code in wc.lower()
        ]
        filtered_wineries = [
            ww.lower() for ww in self.wine_winery_list 
            if winery in ww.lower()
        ]
        filtered_origins = [
            wo.lower() for wo in self.wine_origin_list 
            if origin in wo.lower()
        ]
        
        # Only apply filters if at least one filter is set
        if not any([
            filtered_names, filtered_codes, filtered_wineries, colour, style, 
            varietal, year, filtered_origins
        ]):
            return

        # Apply filters to table
        self.filtered_table.apply_filters(
            filtered_names, filtered_codes, filtered_wineries, 
            colour, style, varietal, year, filtered_origins
        )

    def update_lists(self) -> None:
        """
        Update autocomplete lists with current wine data.
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