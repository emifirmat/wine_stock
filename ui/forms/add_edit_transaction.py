"""
Form that contain the inputs and methods to add a new sale
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from helpers import deep_getattr
from ui.components import (IntInput, DropdownInput, DoubleLabel, AutocompleteInput,
    ClearSaveButtons)
from ui.style import Colours, Fonts, Icons
from ui.tables.add_line_table import AddLineTable
from db.models import Wine, StockMovement


class BaseTransactionForm(ctk.CTkFrame):
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
    ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(
            fg_color="transparent",
            height=500
        )

        # Include db instances
        self.session = session
        self.wine_names_dict = self.get_wine_names_dict()
        self.wine_names_list = list(self.wine_names_dict.keys())

        # TK variables
        self.wine_name_var = tk.StringVar()
        self.quantity_var = tk.StringVar()

        # Listen to any change on their values
        self.wine_name_var.trace_add("write", self.on_entry_change)
        self.quantity_var.trace_add("write", self.on_entry_change)
        self.subtotal_value = None

        # Add components
        self.label_error = None
        self.label_wine_code = None
        self.label_subtotal = None
        self.inputs_dict = None

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

    def get_quantity_var(self) -> int:
        """
        Returns the quantity typed by the user or 0 if it is empty.
        """
        value = self.quantity_var.get()
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
        
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
            if not isinstance(input, DropdownInput) and not isinstance(input, DoubleLabel):
                input.clear()



class AddTransactionForm(BaseTransactionForm):
    """
    Contains all the components and logic related to ADD a Sale.
    """
    def __init__(self, root, transaction_type: str, **kwargs):
        # Set up form frame
        super().__init__(root, **kwargs)
     
        # Listen to any change on their values
        self.temp_stock = {}

        # Add components
        self.transaction = transaction_type       
        self.label_stock = None
        self.table_lines = None
        self.frame_buttons = None
        self.inputs_dict = self.create_components()
        
    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)
      
        # ==Inputs section==
        autocomplete_wine = AutocompleteInput(
            self,
            label_text="Wine",
            item_list=self.wine_names_list,
            textvariable=self.wine_name_var,
        )

        self.label_wine_code = DoubleLabel(
            self,
            label_title_text= "Code",
            label_value_text="-",
        )

        self.label_stock = DoubleLabel(
            self,
            label_title_text= "Stock",
            label_value_text="-",
        )

        textbox_quantity = IntInput(
            self,
            label_text="Quantity (Bottles)",
            from_=0,
            textvariable=self.quantity_var,
        )

        self.label_subtotal = DoubleLabel(
            self,
            label_title_text="Subtotal",
            label_value_text="€ -",
        )
        self.label_subtotal.bold_value_text()
        
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

        # Assign initial values
        textbox_quantity.update_text_value(1)

        # Place widgets
        autocomplete_wine.grid(row=0, column=0, pady=20, sticky="w")
        self.label_wine_code.grid(row=0, column=1, pady=20, sticky="w")
        textbox_quantity.grid(row=1, column=0, sticky="w")
        self.label_stock.grid(row=1, column=1, sticky="w")
        self.label_subtotal.grid(row=1, column=2, sticky="w")
        button_add_line.grid(row=2, column=0, columnspan=3, pady=(20, 5))
        self.label_error.grid(row=3, column=0, columnspan=3, pady=(0, 20))

        # Save inputs for later
        inputs_dict = {
            "wine": autocomplete_wine, 
            "quantity": textbox_quantity, 
        }

        # ==Lines section==
        headers = [" ", "Name", "Quantity", "Price", "Subtotal", " "]
        self.table_lines = AddLineTable(
            self, 
            self.session, 
            headers,
            on_lines_change=self.on_lines_removal
        )
        self.table_lines.grid(row=4, column=0, columnspan=3, pady=20)

        # =Buttons=
        self.frame_buttons = ClearSaveButtons(
            self,
            btn_clear_function=self.clear_inputs,
            btn_save_function=self.save_values
        )
      
        self.frame_buttons.grid(row=5, column=0, pady=20, columnspan=3)

        return inputs_dict

    def clear_inputs(self) -> None:
        """
        Clear the text typed or selected image by the user on the inputs.
        It doesn't clear dropdowns
        """
        super().clear_inputs()

        # Remove all lines
        self.remove_all_lines()

    def remove_all_lines(self):
        """
        Remove all lines added by the user.
        """
        # Remove all lines
        for line in self.table_lines.winfo_children()[2:]:
            # Access to line_number button to remove all lines
            label_line_button = line.winfo_children()[-1]
            if isinstance(label_line_button, ctk.CTkButton):
                # Click button
                label_line_button.invoke()
        
        # Clean temp stock dict
        self.temp_stock.clear()

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
        for line in self.table_lines.get_line_list():
            wine = line["wine"]
            transaction = line["transaction_type"]
            quantity = line["quantity"]

            # Add movement
            movement = StockMovement(
                wine=wine,
                transaction_type=transaction,
                quantity=quantity,
                price=line["price"]
            )
            self.session.add(movement)

        self.session.commit()

        # Show a message
        messagebox.showinfo(
            "Lines Saved",
            f"All added lines from the wine {self.transaction} have been successfully saved."
        )

        # Clear all lines
        self.remove_all_lines()
        
        # Update stock label
        wine_name = self.wine_name_var.get().strip()
        wine_instance = self.session.query(Wine).filter(Wine.name.ilike(wine_name)).first()
        if wine_instance: # Conditional necessary for edge cases.
            self.temp_stock[wine_name.lower()] = wine_instance.quantity
            self.update_label_stock(wine_instance)
        
    def on_entry_change(self, *args) -> None:
        """
        When a wine is selected or the quantity is changed, variables are updated
        """
        # Get variables
        selected_wine_name = self.wine_name_var.get()
        quantity = self.get_quantity_var()
        
        # If used typed invalid wine name, stop the function
        if selected_wine_name not in self.wine_names_dict:
            self.label_subtotal.configure_label_value(text=f"€ -")
            self.label_wine_code.configure_label_value(text="-")
            self.label_stock.configure_label_value(
                text="-", 
                text_color=Colours.TEXT_MAIN,
                image=Icons.EMPTY, # Remove image
                compound=None,
                padx=0
            )
            return

        # Get wine price
        wine_instance = self.wine_names_dict[selected_wine_name]
        if self.transaction == "sale":
            transaction_price = wine_instance.selling_price
        elif self.transaction == "purchase":
            transaction_price = wine_instance.purchase_price
        else:
            raise ValueError("Transaction type should be sale or purchase.")
        
        # Get subtotal
        self.subtotal_value = quantity * transaction_price
        
        # Update labels
        self.label_subtotal.configure_label_value(text=f"€ {self.subtotal_value}")
        self.label_wine_code.configure_label_value(text=wine_instance.code)
        
        wine_name_lower = selected_wine_name.lower()
        if wine_name_lower not in self.temp_stock:
            self.temp_stock[wine_name_lower] = wine_instance.quantity
        
        self.update_label_stock(wine_instance)

    def add_new_wine_line(self):
        """
        It creates a new line in frame_lines, with the data of the inputs and a 
        remove button. It also updates the value in label_total.
        """
        # Get variables
        selected_wine_name = self.wine_name_var.get().strip()
        wine_name_lower = self.wine_name_var.get().strip().lower()
        self.wine_name_var.set(selected_wine_name) # updates variable too
        
        quantity = self.get_quantity_var()
        
        # Check if wine name is invalid
        if selected_wine_name not in self.wine_names_dict:
            self.label_error.configure(
                text = "Wine not found. Make sure it's added to the wine list."
            )
            return

        # If stock becomes negative, warn the user
        wine_instance = self.wine_names_dict[selected_wine_name]
        if self.transaction == "purchase":
            self.temp_stock[wine_name_lower] += quantity
        elif self.transaction == "sale":
            self.temp_stock[wine_name_lower] -= quantity
        
        if self.temp_stock[wine_name_lower] < 0:
            user_reply = messagebox.askyesno(
                title="Negative stock",
                message = (
                    "Adding this transaction will result in a negative stock level."
                    "\nDo you want to proceed anyway?"
                )
            )
            if not user_reply:
                self.temp_stock[wine_name_lower] += quantity
                return
        
        # Show transaction on the table
        self.table_lines.add_new_transaction_line(
            wine_instance, 
            self.transaction,
            quantity, 
            self.subtotal_value
        )

        # Update stock and want user if it is below stock
        self.update_label_stock(wine_instance)
        
        # Enable save button and clear errors
        self.frame_buttons.enable_save_button()
        self.label_error.configure(text="")

    def on_lines_removal(self, lines_size: int, wine_name: str, quantity: int):
        """
        Check the number of lines and disable save button if it is 0. Also, it
        updates temp stock.
        Inputs:
            - lines_size: Number of existing lines in the table
            - wine_name_lower: Name of the wine (lowercase) of the deleted
            transaction, used for temp stock.
            - Quantity: Number of wines of the deleted transaction, used for temp
            stock.
        """
        wine_name_lower = wine_name.lower()
        wine_instance = self.wine_names_dict[wine_name.title()]
        # Disable save button
        if lines_size == 0:
            self.frame_buttons.disable_save_button()
        # Update stock
        if self.transaction == "sale":
            self.temp_stock[wine_name_lower] += quantity
        elif self.transaction == "purchase":
            self.temp_stock[wine_name_lower] -= quantity
        if self.wine_name_var.get().strip().lower() == wine_name_lower:
            self.update_label_stock(wine_instance)

    def update_label_stock(self, wine_instance):
        """
        Updates the text and color of the stock label.
        Parameters:
            - wine_instance: Instance of the wine used for checking stock labels.
        """
        # Update text
        wine_name_lower = wine_instance.name.lower()
        self.label_stock.configure_label_value(text=self.temp_stock[wine_name_lower])
        
        # Update color
        if self.temp_stock[wine_name_lower] < wine_instance.min_stock_sort:
            self.label_stock.configure_label_value(
                text_color=Colours.ERROR,
                image=Icons.WARNING,
                compound="right",
                padx=5,
            )
        else:            
            self.label_stock.configure_label_value(
                text_color=Colours.TEXT_MAIN,
                image=Icons.EMPTY, # Remove image
                compound=None,
                padx=0
            )
            


class EditTransactionForm(BaseTransactionForm):
    """
    Contains all the components and logic related to edit a transaction.
    """
    def __init__(self, root: ctk.CTkFrame, movement, on_save=None, **kwargs):
        # Set up form frame
        super().__init__(root, **kwargs)
        
        # Db instances
        self.movement = movement
        
        # Callbacks
        self.on_save = on_save

        # Add components
        self.inputs_dict = self.create_components()
        self.on_entry_change()

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

        datetime = DoubleLabel(
            frame_background,
            label_title_text="Datetime"
        )

        wine_name = AutocompleteInput(
            frame_background,
            label_text="Wine Name",
            item_list=self.wine_names_list,
            textvariable=self.wine_name_var,
        )

        self.label_wine_code = DoubleLabel(
            frame_background,
            label_title_text="Wine Code"
        )

        transaction = DropdownInput(
            frame_background,
            label_text="Transaction",
            values=["", "Purchase", "Sale"]
        )

        quantity = IntInput(
            frame_background,
            label_text="Quantity",
            textvariable=self.quantity_var,
        )

        self.label_price = DoubleLabel(
            frame_background,
            label_title_text="Price"
        )

        self.label_subtotal = DoubleLabel(
            frame_background,
            label_title_text="Subtotal"
        )

        inputs_dict = {
            "datetime": datetime,
            "wine.name": wine_name, 
            "wine.code": self.label_wine_code,
            "transaction_type": transaction, 
            "quantity": quantity,
            "price": self.label_price,
            "subtotal": self.label_subtotal
        }

        # Add initial values
        for input_name, input in inputs_dict.items():
            # Get value
            value = deep_getattr(self.movement, input_name)
            
            if hasattr(input, "set_to_value"):
                input.set_to_value(value)
            elif hasattr(input,"update_text_value"):
                input.update_text_value(value)
            elif input_name == "datetime":
                input.configure_label_value(text=value)
        
        # Align and place widgets
        for index, input in enumerate(inputs_dict.values()):
            if isinstance(input, DoubleLabel):
                # Value width should be fixed because values update with tkvar
                input.set_columns_layout(title_width=90, value_width=100)
            input.set_total_width(450)
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
            btn_clear_function=self.clear_inputs,
            btn_save_function=self.save_values
        )
        frame_buttons.enable_save_button()
        
        frame_buttons.grid(row=len(inputs_dict) + 1, column=0, pady=20)

        return inputs_dict

    def on_entry_change(self, *args) -> None:
        """
        When a wine is selected or the quantity is changed, variables are updated
        """
        # Don't execute method when creating components.
        if not self.inputs_dict:
            return

        # Get variables
        selected_wine_name = self.wine_name_var.get().title()
        quantity = self.get_quantity_var()
        transaction = self.inputs_dict["transaction_type"].get().lower()

        # If used typed invalid wine name, stop the function
        if selected_wine_name not in self.wine_names_dict:
            self.label_wine_code.configure_label_value(text="-")
            self.label_price.configure_label_value(text=f"€ -")
            self.label_subtotal.configure_label_value(text=f"€ -")
            return

        # Get wine price
        wine_instance = self.wine_names_dict[selected_wine_name]
        
        # Update Labels
        self.label_wine_code.configure_label_value(text=wine_instance.code)            
        if transaction == "sale":
            transaction_price = wine_instance.selling_price
        elif transaction == "purchase":
            transaction_price = wine_instance.purchase_price
        else:
            self.label_price.configure_label_value(text=f"€ -")
            self.label_subtotal.configure_label_value(text=f"€ -")
            return
        
        self.label_price.configure_label_value(text=f"€ {transaction_price}")
        self.subtotal_value = quantity * transaction_price
        self.label_subtotal.configure_label_value(text=f"€ {self.subtotal_value}")
    
    def save_values(self) -> None:
        """
        Save added lines into the db
        """
        selected_wine_name = self.wine_name_var.get().strip().title()
        self.wine_name_var.set(selected_wine_name) # updates variable too
        quantity = self.get_quantity_var()
        transaction_type = self.inputs_dict["transaction_type"].get().lower()
        
        # Validate wine name
        if selected_wine_name not in self.wine_names_dict:
            self.label_error.configure(
                text = "Wine not found. Make sure it's added to the wine list."
            )
            return

        # If stock becomes negative, warn the user
        wine_instance = self.wine_names_dict[selected_wine_name]
        
        if wine_instance == self.movement.wine:
            if self.movement.transaction_type == "purchase":
                new_stock = wine_instance.quantity - self.movement.quantity
            elif self.movement.transaction_type == "sale":
                new_stock = wine_instance.quantity + self.movement.quantity
        else:
            new_stock = self.movement.wine.quantity

        if transaction_type == "purchase":            
            new_stock += quantity
        elif transaction_type == "sale":
            new_stock -= quantity
        
        if new_stock < 0:
            user_reply = messagebox.askyesno(
                title="Negative stock",
                message = (
                    "Modifying this transaction will result in a negative stock "
                    "level.\nDo you want to proceed anyway?"
                )
            )
            if not user_reply:
                return

        # Ask for confirmation
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            f"The transaction will be modified. Proceed?"
        )
        if not confirm_dialog:
            return

        # Save db
        attrs = ["wine", "transaction_type", "quantity"]
        values = [wine_instance, transaction_type , quantity]
        
        for attr, value in zip(attrs, values):
            setattr(self.movement, attr, value)
        try:
            self.session.commit()
        except IntegrityError as e:
            # Rollback session
            self.session.rollback()
        
            messagebox.showinfo(
                "Error Saving",
                "Couldn't save the wine, please contact the admin. (code=2)"
            )
            print(str(e.orig))
            # Stop function            
            return
            
        # Refresh table
        self.on_save(self.movement)
    
        # Close window
        self.winfo_toplevel().destroy()