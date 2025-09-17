"""
Form that contain the inputs and methods to add a new sale
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from decimal import Decimal

from ui.components import (IntInput, DropdownInput, DoubleLabel, AutoCompleteInput,
    ClearSaveButtons)
from ui.style import Colours, Fonts
from ui.tables.transactions_table import TransactionsTable
from models import Wine, StockMovement

class RemoveTransactionForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to ADD a Sale.
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
        self.wine_names_list = list(self.wine_names_dict.keys())
        
        # TK variables
        self.wine_name_var = tk.StringVar()
        self.wine_code_var = tk.StringVar()
       
        # Listen to any change on their values
        self.wine_name_var.trace_add("write", self.on_entry_change)
        self.wine_code_var.trace_add("write", self.on_entry_change)

        # Add components
        self.transactions_table = None
        self.label_error = None
        self.label_code = None
        self.label_subtotal = None
        self.frame_lines = None
        self.frame_buttons = None
        self.inputs_dict = self.create_components()
        #self.on_entry_change() # Initial subtotal label update

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

        section_title.grid(row=0, column=0, padx=5, pady=20, columnspan=2, sticky="wen")

        autocomplete_wine = AutoCompleteInput(
            filter_frame,
            label_text="Wine",
            wine_list=self.wine_names_list,
            textvariable=self.wine_name_var,
            optional=True
        )

        """
        autocomplete_code = AutoCompleteInput(
            self,
            label_title_text= "Code",
             wine_list=self.wine_names_list,
            textvariable=self.wine_code_var,
        )

        dropdown_transaction = DropdownInput(
            self,
            label_title_text= "Transaction",
            label_value_text="",
        )
        """

        autocomplete_wine.grid(row=1, column=0, padx=5, pady=20, sticky="w")
        #autocomplete_code.grid(row=0, column=1, pady=20, sticky="w")
        #dropdown_transaction.grid(row=1, column=0, sticky="w")
     
        # Save inputs for later
        inputs_dict = {
            "wine": autocomplete_wine, 
            #"code": autocomplete_code, 
            #"transaction": dropdown_transaction
        }

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
        Clear the text typed or selected image by the user on the inputs.
        It doesn't clear dropdowns
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Clearing the form will discard all current inputs and added lines. Continue?"
        )
        if not confirm_dialog:
            return
        
        for input in self.inputs_dict.values():         
            # Still dropdown doesn't have an empty value, so it makes no sense to
            # Change its value to the first item.
            if type(input) is not DropdownInput:
                input.clear()

        # Remove all lines
        self.remove_all_lines()


    def on_entry_change(self, *args) -> None:
        """
        When a wine is selected or the quantity is changed, variables are updated
        """
        # Get variables
        selected_wine_name = self.wine_name_var.get().strip().lower()
        
        # Get wines that matches what the user typed
        filtered_names = list(filter(lambda wn: selected_wine_name in wn.lower(), self.wine_names_list))
        
        # If there is no match, stop the function
        if len(filtered_names) == 0:
            return

        # else, update the table
        self.transactions_table.update_by_filter(filtered_names)
        

    def get_quantity_var(self) -> int:
        """
        Returns the quantity typed by the user or 0 if it is empty.
        """
        value = self.quantity_var.get()
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
