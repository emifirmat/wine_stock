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
from ui.tables.add_line_table import AddLineTable
from models import Wine, StockMovement

class AddTransactionForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to ADD a Sale.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, transaction_type, **kwargs
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
        self.quantity_var = tk.IntVar(value=1)
     
        # Listen to any change on their values
        self.wine_name_var.trace_add("write", self.on_entry_change)
        self.quantity_var.trace_add("write", self.on_entry_change)
        self.subtotal_value = None
        self.line_counter = 0
        self.line_list = [] # It contains dicts

        # Add components
        self.transaction = transaction_type
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
        self.grid_columnconfigure(1, weight=1)

        # ==Add Components==
        # =Inputs section=
        autocomplete_wine = AutoCompleteInput(
            self,
            label_text="Wine",
            wine_list=self.wine_names_list,
            textvariable=self.wine_name_var,
        )

        self.label_code = DoubleLabel(
            self,
            label_title_text= "Code",
            label_value_text="",
        )

        textbox_quantity = IntInput(
            self,
            label_text="Quantity (Bottles)",
            from_=0,
            textvariable=self.quantity_var
        )
        self.label_subtotal = DoubleLabel(
            self,
            label_title_text="Subtotal",
            label_value_text="€ -"
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
        
        self.label_error = ctk.CTkLabel(
            self,
            text="",
            text_color=Colours.ERROR,
            font=Fonts.TEXT_ERROR
        )


        autocomplete_wine.grid(row=0, column=0, pady=20, sticky="w")
        self.label_code.grid(row=0, column=1, pady=20, sticky="w")
        textbox_quantity.grid(row=1, column=0, sticky="w")
        self.label_subtotal.grid(row=1, column=1, sticky="w")
        button_add_line.grid(row=2, column=0, columnspan=2, pady=(20, 5))
        self.label_error.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        # Save inputs for later
        inputs_dict = {
            "wine": autocomplete_wine, 
            "quantity": textbox_quantity, 
        }

        # =Lines section=
        headers = [" ", "Name", "Quantity", "Price", "Subtotal", " "]
        self.frame_lines = AddLineTable(
            self, 
            self.session, 
            headers,
            on_lines_change=self.on_lines_change
        )
        self.frame_lines.grid(row=4, column=0, columnspan=2, pady=20)

        # =Buttons=
        self.frame_buttons = ClearSaveButtons(
            self,
            btn_clear_function=self.clear_inputs,
            btn_save_function=self.save_values
        )
      
        self.frame_buttons.grid(row=5, column=0, pady=20, columnspan=2)

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

    def remove_all_lines(self):
        """
        Remove all lines added by the user.
        """
        # Remove all lines
        for line in self.frame_lines.winfo_children()[2:]:
            # Access to line_number button to remove all lines
            label_line_button = line.winfo_children()[-1]
            if isinstance(label_line_button, ctk.CTkButton):
                # Click button
                label_line_button.invoke()

    def save_values(self) -> None:
        """
        Save added lines into the db
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            f"Do you want to save this {self.transaction}?"
        )
        if not confirm_dialog:
            return

        # Iterate over each line
        for line in self.frame_lines.get_line_list():
            movement = StockMovement(
                wine=line["wine"],
                transaction_type=line["transaction_type"],
                quantity=line["quantity"],
                price=line["price"]
            )
            # Save it in the DB    
            self.session.add(movement)
        
        self.session.commit()

        # Show a message
        messagebox.showinfo(
            "Lines Saved",
            f"All added lines from the wine {self.transaction} have been successfully saved."
        )

        # Clear all lines
        self.remove_all_lines()

    def on_entry_change(self, *args) -> None:
        """
        When a wine is selected or the quantity is changed, variables are updated
        """
        # Get variables
        selected_wine_name = self.wine_name_var.get()
        quantity = self.get_quantity_var()
        
        # If used typed invalid wine name, stop the function
        if selected_wine_name not in self.wine_names_dict:
            self.label_subtotal.update_value_text(f"€ -")
            self.label_code.update_value_text("-")
            return

        # Get wine price
        wine_instance = self.wine_names_dict[selected_wine_name]
        selling_price = wine_instance.selling_price
        
        # Get subtotal
        self.subtotal_value = quantity * selling_price
        
        # Update labels
        self.label_subtotal.update_value_text(f"€ {self.subtotal_value}")
        self.label_code.update_value_text(wine_instance.code)

    def get_quantity_var(self) -> int:
        """
        Returns the quantity typed by the user or 0 if it is empty.
        """
        try:
            return self.quantity_var.get()
        except:
            # Catch empty entry and update process
            return 0 

    def add_new_wine_line(self):
        """
        It creates a new line in frame_lines, with the data of the inputs and a 
        remove button. It also updates the value in label_total.
        """
        # Get variables
        selected_wine_name = self.wine_name_var.get().strip()
        self.wine_name_var.set(selected_wine_name) # updates variable too
        
        quantity = self.get_quantity_var()
        
        # Check if wine name is invalid
        if selected_wine_name not in self.wine_names_dict:
            self.label_error.configure(
                text = "Wine not found. Make sure it's added to the wine list."
            )
            return

        # Show transaction on the table
        wine_instance = self.wine_names_dict[selected_wine_name]
        self.frame_lines.add_new_transaction_line(
            wine_instance, 
            self.transaction,
            quantity, 
            self.subtotal_value
        )

        # Enable save button and clear errors
        self.frame_buttons.enable_save_button()
        self.label_error.configure(text = "")

    def on_lines_change(self, lines_size: int):
        """
        Check the number of lines and disable save button if it is 0.
        Inputs:
            - lines_size: Number of existing lines in the table
        """
        # Disable save button
        if lines_size == 0:
            self.frame_buttons.disable_save_button()