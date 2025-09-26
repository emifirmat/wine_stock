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
from ui.tables.transactions_table import TransactionsTable
from db.models import Wine, StockMovement

class RemoveTransactionForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to remove a transaction.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
        ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            height=500
        )
        
        # Include db instances
        self.session = session
        self.wine_names_dict = self.get_wine_names_dict()
        self.wine_names_list = list(self.wine_names_dict.keys()) # ordered
        self.wine_codes_list = [wine.code for wine in Wine.all_ordered(self.session)]
        
        # TK variables
        self.wine_name_var = tk.StringVar()
        self.wine_code_var = tk.StringVar()
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()
       
        # Listen to any change on their values
        self.wine_name_var.trace_add("write", self.on_entry_change)
        self.wine_code_var.trace_add("write", self.on_entry_change)
        self.date_from_var.trace_add("write", self.on_entry_change)
        self.date_to_var.trace_add("write", self.on_entry_change)

        # Add components
        self.transactions_table = None
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
            fg_color = "transparent",
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
            wine_list=self.wine_names_list,
            textvariable=self.wine_name_var,
            optional=True
        )
     
        autocomplete_code = AutoCompleteInput(
            filter_frame,
            label_text= "Code",
            wine_list=self.wine_codes_list,
            textvariable=self.wine_code_var,
            optional=True
        )

        dropdown_transaction = DropdownInput(
            filter_frame,
            label_text= "Transaction",
            values=["", "Purchase", "Sale"],
            optional=True,
            command=self.on_entry_change, # It doesn't need variable trace
        )

        input_from_date = DateInput(
            filter_frame,
            label_text="From",
            textvariable=self.date_from_var,
            optional=True,
        )
        
        input_to_date = DateInput(
            filter_frame,
            label_text="To",
            textvariable=self.date_to_var,
            optional=True,
        )

        autocomplete_wine.grid(row=1, column=0, padx=5, pady=(0, 20), sticky="w")
        autocomplete_code.grid(row=1, column=1, padx=5, pady=(0, 20))
        dropdown_transaction.grid(row=1, column=2, padx=(5, 2), pady=(0, 20))
        input_from_date.grid(row=2, column=0, padx=5, pady=(0, 20))
        input_to_date.grid(row=2, column=1, padx=5, pady=(0, 20))

        # Save inputs for later
        inputs_dict = {
            "wine": autocomplete_wine, 
            "code": autocomplete_code, 
            "transaction": dropdown_transaction,
            "input_from_date": input_from_date,
            "input_to_date": input_to_date
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
        button_clear.grid(row=2, column=2, padx=5, pady=(0, 20))

        # ==Table section==
        self.transactions_table = TransactionsTable(
            self,
            self.session,
            headers=[
                "datetime", "wine name", "wine code", "transaction", "quantity",
                "price", "subtotal"
            ],
            lines=StockMovement.all_ordered(self.session)
        )
        self.transactions_table.grid(row=1, column=0, pady=(10, 0), sticky="nsew")

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
        selected_wine_name = self.wine_name_var.get().strip().lower()
        selected_wine_code = self.wine_code_var.get().strip().lower()
        transaction_type = self.inputs_dict["transaction"].get()
        date_from = self.date_from_var.get().strip()
        date_to = self.date_to_var.get().strip()
        
        # Get wines that matches what the user typed
        filtered_names = [
            wn.lower() for wn in self.wine_names_list 
            if selected_wine_name in wn.lower()
        ]
        filtered_codes = [
            wc.lower() for wc in self.wine_codes_list 
            if selected_wine_code in wc.lower()
        ]
        
        # If there is no match, stop the function
        if (len(filtered_names) == 0 
            and len(filtered_codes) == 0
            and transaction_type == ""
            and date_from == ""
            and date_to == ""
        ):
            return

        # else, update the table
        self.transactions_table.apply_filters(
            filtered_names, filtered_codes, transaction_type, date_from, date_to
        )
