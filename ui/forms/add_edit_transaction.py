"""
Transaction forms for adding and editing sales and purchases.

This module provides forms for creating new transactions (sales/purchases)
and editing existing transactions, including validation and stock tracking
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Callable

from helpers import deep_getattr
from ui.components import (IntInput, DropdownInput, DoubleLabel, AutocompleteInput,
    ClearSaveButtons)
from ui.style import Colours, Fonts, Icons, Spacing, Rounding
from ui.tables.add_line_table import AddLineTable
from db.models import Wine, StockMovement


class BaseTransactionForm(ctk.CTkFrame):
    """
    Base form for transaction management.
    
    Provides shared functionality for adding and editing transactions,
    including wine selection, quantity input, and validation.
    """
    def __init__(self, root: ctk.CTkFrame, session: Session, **kwargs):
        """
        Initialize base transaction form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            **kwargs: Additional CTkFrame keyword arguments
        """
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(fg_color="transparent")

        # DB instances
        self.session = session
        self.wine_names_dict = self.get_wine_names_dict()
        self.wine_names_list = list(self.wine_names_dict.keys())

        # Tk variables
        self.wine_name_var = tk.StringVar()
        self.quantity_var = tk.StringVar()

        # Listen to changes
        self.wine_name_var.trace_add("write", self.on_entry_change)
        self.quantity_var.trace_add("write", self.on_entry_change)
        self.subtotal_value = None

        # Components (to be set by subclasses)
        self.label_error = None
        self.label_wine_code = None
        self.label_subtotal = None
        self.inputs_dict = None

    def get_wine_names_dict(self) -> dict[str, Wine]:
        """
        Get dictionary of wine names mapped to Wine instances.
        
        Returns:
            Dictionary with wine names (title case) as keys and Wine instances as values
        """
        wines = Wine.all_ordered(self.session)
        return {wine.name.title(): wine for wine in wines}

    def get_quantity_var(self) -> int:
        """
        Get quantity from input, returning 0 if empty or invalid.
        
        Returns:
            Quantity as integer, or 0 if invalid
        """
        value = self.quantity_var.get()
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
        
    def clear_inputs(self) -> None:
        """
        Clear all input fields after user confirmation.
        
        Shows confirmation dialog before clearing. Does not clear dropdowns
        or DoubleLabel components as they don't support clearing.
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Clearing the form will discard all current inputs and added lines. Continue?"
        )
        if not confirm_dialog:
            return
        
        for input_widget in self.inputs_dict.values():         
            # Dropdowns and DoubleLabels don't have meaningful empty states
            if not isinstance(input_widget, (DropdownInput, DoubleLabel)):
                input_widget.clear()


class AddTransactionForm(BaseTransactionForm):
    """
    Form for adding new sales or purchases with multiple lines.
    
    Allows users to add multiple wine transactions, tracks temporary stock
    levels, validates quantities, and saves all lines to the database.
    """
    def __init__(self, root, session: Session, transaction_type: str, **kwargs):
        """
        Initialize add transaction form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            transaction_type: Type of transaction - "sale" or "purchase"
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, session, **kwargs)
     
        # Transaction state
        self.transaction = transaction_type
        self.temp_stock = {}

        # Components
        self.label_stock = None
        self.table_lines = None
        self.frame_buttons = None
        self.inputs_dict = self.create_components()
        
    def create_components(self) -> dict[str, ctk.CTkBaseClass]:
        """
        Create and position form inputs, table, and buttons.
        
        Returns:
            Dictionary of input widgets keyed by field name
        """
        # Configure grid
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)

        # Create input components
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
        self.label_wine_code.fix_value_width(chars_count=10)

        self.label_stock = DoubleLabel(
            self,
            label_title_text= "Stock",
            label_value_text="-",
        )
        self.label_stock.fix_value_width(chars_count=6)

        textbox_quantity = IntInput(
            self,
            label_text="Quantity (Bottles)",
            from_=0,
            to=999,
            textvariable=self.quantity_var,
        )

        self.label_subtotal = DoubleLabel(
            self,
            label_title_text="Subtotal",
            label_value_text="€ -",
        )
        self.label_subtotal.bold_value_text()
        self.label_subtotal.fix_value_width(chars_count=10)
        
        button_add_line = ctk.CTkButton(
            self,
            text="Add Line",
            fg_color=Colours.BTN_ADD_LINE,
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_ADD_LINE,
            corner_radius=Rounding.BUTTON,
            cursor="hand2",
            command=self.add_new_wine_line 
        )
        
        self.label_error = ctk.CTkLabel(
            self,
            text="Wine not found. Make sure it's added to the wine list.",
            text_color=Colours.ERROR,
            font=Fonts.TEXT_ERROR
        )

        # Set initial values
        textbox_quantity.update_text_value("1")

        # Position input components
        autocomplete_wine.grid(
            row=0, column=0, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y, sticky="w"
        )
        self.label_wine_code.grid(
            row=0, column=1, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y, sticky="w"
        )
        textbox_quantity.grid(
            row=1, column=0, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y, sticky="w"
        )
        self.label_stock.grid(
            row=1, column=1, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y, sticky="w"
        )
        self.label_subtotal.grid(
            row=1, column=2, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y, sticky="w"
        )
        button_add_line.grid(
            row=2, column=0, columnspan=3, 
            padx=Spacing.BUTTON_X, pady=Spacing.BUTTON_Y
        )

        # Save inputs dictionary
        inputs_dict = {
            "wine": autocomplete_wine, 
            "quantity": textbox_quantity, 
        }

        # Create transaction lines table
        headers = [" ", "Name", "Quantity", "Price", "Subtotal", " "]
        self.table_lines = AddLineTable(
            self, 
            self.session, 
            headers,
            on_lines_change=self.on_lines_removal
        )
        self.table_lines.grid(
            row=4, column=0, columnspan=3, 
            padx=Spacing.TABLE_X, pady=Spacing.TABLE_Y
        )

        # Create action buttons
        self.frame_buttons = ClearSaveButtons(
            self,
            btn_clear_function=self.clear_inputs,
            btn_save_function=self.save_values
        )
      
        self.frame_buttons.grid(
            row=5, column=0, columnspan=3,
            padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y,
        )

        return inputs_dict

    def clear_inputs(self) -> None:
        """
        Clear inputs and remove all added transaction lines.
        """
        super().clear_inputs()
        self.remove_all_lines()

    def remove_all_lines(self):
        """
        Remove all transaction lines from the table.
        """
        # Invoke remove button for each line (skip header rows)
        for line in self.table_lines.winfo_children()[2:]:
            # Access line's remove button (last child)
            line_button = line.winfo_children()[-1]
            if isinstance(line_button, ctk.CTkButton):
                line_button.invoke()
        
        # Clear temporary stock tracking
        self.temp_stock.clear()

    def save_values(self) -> None:
        """
        Save all added transaction lines to the database.
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            f"Do you want to save this {self.transaction}?"
        )
        if not confirm_dialog:
            return

        # Create StockMovement for each line
        for line in self.table_lines.get_line_list():
            movement = StockMovement(
                wine=line["wine"],
                transaction_type=line["transaction_type"],
                quantity=line["quantity"],
                price=line["price"]
            )
            self.session.add(movement)

        self.session.commit()

        # Show success message
        messagebox.showinfo(
            "Lines Saved",
            f"All added lines from the wine {self.transaction} have been successfully saved."
        )

        # Clear added transactions from the table
        self.remove_all_lines()
        
        # Update stock label for current wine
        wine_name = self.wine_name_var.get().strip()
        wine_instance = self.session.query(Wine).filter(
            Wine.name.ilike(wine_name)
        ).first()
        if wine_instance: # Handle edge case where wine was deleted
            self.temp_stock[wine_name.lower()] = wine_instance.quantity
            self.update_label_stock(wine_instance)
        
    def on_entry_change(self, *args) -> None:
        """
        Update labels when wine selection or quantity changes.
        
        Parameters:
            *args: Trace callback arguments (unused but required by trace_add)
        """
        # Get current values
        selected_wine_name = self.wine_name_var.get()
        quantity = self.get_quantity_var()
        
        # Reset labels if invalid wine name
        if selected_wine_name not in self.wine_names_dict:
            self.label_subtotal.configure_label_value(text="€ -")
            self.label_wine_code.configure_label_value(text="-")
            self.label_stock.configure_label_value(
                text="-", 
                text_color=Colours.TEXT_MAIN,
                image=Icons.EMPTY, # Hide image
                compound="center",
                padx=0
            )
            return

        # Get wine and calculate values
        wine_instance = self.wine_names_dict[selected_wine_name]

        if self.transaction == "sale":
            transaction_price = wine_instance.selling_price
        elif self.transaction == "purchase":
            transaction_price = wine_instance.purchase_price
        else:
            raise ValueError("Transaction type should be 'sale' or 'purchase'.")
        
        self.subtotal_value = quantity * transaction_price
        
        # Update labels
        self.label_subtotal.configure_label_value(text=f"€ {self.subtotal_value}")
        self.label_wine_code.configure_label_value(text=wine_instance.code)
        
        # Initialize temp stock if not already tracked
        wine_name_lower = selected_wine_name.lower()
        if wine_name_lower not in self.temp_stock:
            self.temp_stock[wine_name_lower] = wine_instance.quantity
        
        self.update_label_stock(wine_instance)

    def add_new_wine_line(self) -> None:
        """
        Add a new transaction line to the table.
        
        Validates wine selection, checks for negative stock, and adds
        the line to the table if validation passes.
        """
        # Get and validate wine name
        selected_wine_name = self.wine_name_var.get().strip()
        wine_name_lower = self.wine_name_var.get().strip().lower()
        self.wine_name_var.set(selected_wine_name)
        
        quantity = self.get_quantity_var()
        
        if selected_wine_name not in self.wine_names_dict:
            self.label_error.grid(
                row=3, column=0, columnspan=3, 
                padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y,
            )
            return

        # Update temp stock and check for negative values
        wine_instance = self.wine_names_dict[selected_wine_name]
        
        if self.transaction == "purchase":
            self.temp_stock[wine_name_lower] += quantity
        elif self.transaction == "sale":
            self.temp_stock[wine_name_lower] -= quantity
        
        # Warn if stock becomes negative
        if self.temp_stock[wine_name_lower] < 0:
            user_reply = messagebox.askyesno(
                title="Negative Stock",
                message = (
                    "Adding this transaction will result in a negative stock level."
                    "\nDo you want to proceed anyway?"
                )
            )
            if not user_reply:
                # Revert temp stock change
                if self.transaction == "purchase":
                    self.temp_stock[wine_name_lower] -= quantity
                elif self.transaction == "sale":
                    self.temp_stock[wine_name_lower] += quantity
                return
        
        # Add line to table
        self.table_lines.add_new_transaction_line(
            wine_instance, 
            self.transaction,
            quantity, 
            self.subtotal_value
        )

        # Update UI
        self.update_label_stock(wine_instance)
        self.frame_buttons.enable_save_button()
        self.label_error.grid_forget()

    def on_lines_removal(
        self, lines_size: int, wine_name: str, quantity: int
    ) -> None:
        """
        Handle line removal from table.
        
        Updates temp stock and disables save button if no lines remain.
        
        Parameters:
            lines_size: Number of remaining lines in table
            wine_name: Name of wine from removed transaction
            quantity: Quantity from removed transaction
        """
        wine_name_lower = wine_name.lower()
        wine_instance = self.wine_names_dict[wine_name.title()]

        # Disable save button if no lines remain
        if lines_size == 0:
            self.frame_buttons.disable_save_button()
        
        # Revert temp stock change
        if self.transaction == "sale":
            self.temp_stock[wine_name_lower] += quantity
        elif self.transaction == "purchase":
            self.temp_stock[wine_name_lower] -= quantity
        
        # Update stock label if same wine is selected
        if self.wine_name_var.get().strip().lower() == wine_name_lower:
            self.update_label_stock(wine_instance)

    def update_label_stock(self, wine_instance: Wine) -> None:
        """
        Update stock label with current value and warning indicator.
        
        Displays warning icon if stock is below minimum threshold.
        
        Parameters:
            wine_instance: Wine instance to check stock level
        """
        wine_name_lower = wine_instance.name.lower()

        # Update stock value
        self.label_stock.configure_label_value(
            text=str(self.temp_stock[wine_name_lower])
        )
        
        # Show warning if below minimum stock
        if self.temp_stock[wine_name_lower] < wine_instance.min_stock_sort:
            self.label_stock.configure_label_value(
                text_color=Colours.ERROR,
                image=Icons.WARNING,
                compound="right",
                padx=Spacing.SMALL,
            )
        else:            
            self.label_stock.configure_label_value(
                text_color=Colours.TEXT_MAIN,
                image=Icons.EMPTY, # Hide image
                compound=None,
                padx=0
            )
            

class EditTransactionForm(BaseTransactionForm):
    """
    Form for editing existing transactions.
    
    Allows modification of wine, transaction type, and quantity for
    an existing StockMovement record.
    """
    def __init__(
        self, root: ctk.CTkFrame, session: Session, movement: StockMovement, 
        on_save: Callable | None = None, **kwargs
    ):
        """
        Initialize edit transaction form.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            movement: StockMovement instance to edit
            on_save: Callback executed after saving with updated movement
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, session, **kwargs)
        
        # DB instances
        self.movement = movement
        
        # Callbacks
        self.on_save = on_save

        # Components
        self.label_price = None
        self.inputs_dict = self.create_components()
        self.on_entry_change()

    def create_components(self) -> dict[str, ctk.CTkBaseClass]:
        """
        Create and position edit form inputs and buttons.
        
        Returns:
            Dictionary of input widgets keyed by field name
        """
        self.grid_columnconfigure(0, weight=1)

        # Create background frame
        frame_background = ctk.CTkFrame(self, fg_color = Colours.BG_FORM,)
        frame_background.grid(
            row=1, column=0, 
            padx=Spacing.WINDOW_X, pady=Spacing.WINDOW_Y
        )
        frame_background.grid_columnconfigure(0, weight=1)

        # Create input components
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

        # Populate with initial values
        for input_name, input_widget in inputs_dict.items():
            # Get value
            value = deep_getattr(self.movement, input_name)
            
            if hasattr(input_widget, "set_to_value"):
                input_widget.set_to_value(value)
            elif hasattr(input_widget,"update_text_value"):
                input_widget.update_text_value(str(value))
            elif input_name == "datetime":
                input_widget.configure_label_value(text=str(value))
        
        # Position components
        for index, input_widget in enumerate(inputs_dict.values()):
            if isinstance(input_widget, DoubleLabel):
                # Fixed width for value labels with dynamic content
                input_widget.set_columns_layout(title_width=90, value_width=100)
            input_widget.set_total_width(450)
            input_widget.grid(
                row=index, column=0, 
                padx=Spacing.LABEL_X, 
                pady=Spacing.LABEL_Y
            )
                   
        # Error message label
        self.label_error = ctk.CTkLabel(
            frame_background,
            fg_color="transparent",
            text="",
            text_color=Colours.ERROR,
            font=Fonts.TEXT_ERROR,
            width=450,
        )
        self.label_error.grid(
            row=len(inputs_dict), column=0, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y
        )

        # Action buttons
        frame_buttons = ClearSaveButtons(
            frame_background,
            btn_clear_function=self.clear_inputs,
            btn_save_function=self.save_values
        )
        frame_buttons.enable_save_button()
        
        frame_buttons.grid(
            row=len(inputs_dict) + 1, column=0,
            padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y
        )
        
        return inputs_dict

    def on_entry_change(self, *args) -> None:
        """
        Update price and subtotal when wine or quantity changes.
        
        Parameters:
            *args: Trace callback arguments (unused but required by trace_add)
        """
        # Skip during component creation
        if not self.inputs_dict:
            return

        # Get current values
        selected_wine_name = self.wine_name_var.get().title()
        quantity = self.get_quantity_var()
        transaction = self.inputs_dict["transaction_type"].get().lower()

        # Reset labels if invalid wine
        if selected_wine_name not in self.wine_names_dict:
            self.label_wine_code.configure_label_value(text="-")
            self.label_price.configure_label_value(text="€ -")
            self.label_subtotal.configure_label_value(text="€ -")
            return

        # Get wine and update code
        wine_instance = self.wine_names_dict[selected_wine_name]
        self.label_wine_code.configure_label_value(text=wine_instance.code)

        # Calculate price and subtotal based on transaction type
        if transaction == "sale":
            transaction_price = wine_instance.selling_price
        elif transaction == "purchase":
            transaction_price = wine_instance.purchase_price
        else:
            self.label_price.configure_label_value(text="€ -")
            self.label_subtotal.configure_label_value(text="€ -")
            return
        
        self.label_price.configure_label_value(text=f"€ {transaction_price}")
        self.subtotal_value = quantity * transaction_price
        self.label_subtotal.configure_label_value(text=f"€ {self.subtotal_value}")
    
    def save_values(self) -> None:
        """
        Save edited transaction to database after validation.
        """
        # Get and validate values
        selected_wine_name = self.wine_name_var.get().strip().title()
        self.wine_name_var.set(selected_wine_name)
        quantity = self.get_quantity_var()
        transaction_type = self.inputs_dict["transaction_type"].get().lower()
        
        # Validate wine name
        if selected_wine_name not in self.wine_names_dict:
            self.label_error.configure(
                text = "Wine not found. Make sure it's added to the wine list."
            )
            return

        # Calculate new stock level
        wine_instance = self.wine_names_dict[selected_wine_name]
        
        # Revert old transaction's effect on stock
        if wine_instance == self.movement.wine:
            if self.movement.transaction_type == "purchase":
                new_stock = wine_instance.quantity - self.movement.quantity
            elif self.movement.transaction_type == "sale":
                new_stock = wine_instance.quantity + self.movement.quantity
            else:
                new_stock = self.movement.wine.quantity        
        else:
            # Different wine selected, start with its current stock
            new_stock = self.movement.wine.quantity

        # Apply new transaction's effect
        if transaction_type == "purchase":            
            new_stock += quantity
        elif transaction_type == "sale":
            new_stock -= quantity
        
        # Warn if negative stock
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

        # Confirm save
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            f"The transaction will be modified. Proceed?"
        )
        if not confirm_dialog:
            return

        # Update movement attributes
        self.movement.wine = wine_instance
        self.movement.transaction_type = transaction_type
        self.movement.quantity = quantity
        
        # Save to database
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()        
            messagebox.showerror(
                "Error Saving",
                "Couldn't save the transaction. Please contact the administrator. (code=2)"
            )
            print(f"IntegrityError: {e.orig}")
            # Stop function            
            return
            
        # Refresh parent view and close window
        if self.on_save:
            self.on_save(self.movement)
    
        # Close window
        self.winfo_toplevel().destroy()