"""
Transaction lines table for adding multiple wines.

This module provides a table component for displaying and managing
transaction lines (sales/purchases) added by the user before saving.
"""
import customtkinter as ctk
import tkinter as tk
from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Callable

from db.models import Wine
from ui.style import Colours, Fonts, Spacing
from ui.components import DoubleLabel


class AddLineTable(ctk.CTkFrame):
    """
    Table for managing transaction lines before saving.
    
    Displays a list of wines with quantity, price, and subtotal for each line.
    Users can add and remove lines, with automatic total calculation.
    """

    def __init__(
        self, root: ctk.CTkFrame, session: Session, headers: list[str], 
        on_lines_change: Callable | None = None, **kwargs
    ):
        """
        Initialise transaction lines table.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            headers: List of column header labels
            on_lines_change: Callback executed when lines are removed,
                receives (lines_count, wine_name, quantity)
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color=Colours.BG_MAIN)
        
        # DB instances
        self.session = session

        # Table data
        self.headers = headers
        self.line_counter = 0
        self.line_list = [] # List of transaction dictionaries
        self.total_var = tk.StringVar(value="€ 0.00")

        # Callback
        self.on_lines_change = on_lines_change

        # Create components
        self.create_components()

    def create_components(self) -> None:
        """
        Create and display table headers and total label.
        """
        # Create header row
        row_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_header_frame.pack(fill="x", pady=2)
        
        # Define column widths
        widths = [50, 200, 100, 100, 100, 30]
        
        # Create header labels
        for i, (header, width) in enumerate(zip(self.headers, widths)):
            label = ctk.CTkLabel(
                row_header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=width,
                wraplength=width
            )
            label.grid(
                row=0, column=i, 
                padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y
            )

        # Create total amount label
        total = DoubleLabel(
            self,
            label_title_text="Total",
            text_variable=self.total_var
        )
        total.bold_value_text()
        total.pack(side="bottom", anchor="se")

    def add_new_transaction_line(
        self, wine_instance: Wine, transaction_type: str, quantity: int, 
        subtotal: Decimal
    ) -> None:
        """
        Add a new transaction line to the table.
        
        Creates a row with wine details and a remove button, updates
        the running total.
        
        Parameters:
            wine_instance: Wine object selected by the user
            transaction_type: Type of transaction - "sale" or "purchase"
            quantity: Number of bottles
            subtotal: Pre-calculated subtotal (quantity x price)
        """
        # Increment line counter
        self.line_counter += 1

        # Get transaction price
        if transaction_type == "sale":
            price = wine_instance.selling_price
        elif transaction_type == "purchase": 
            price = wine_instance.purchase_price
        else:
            raise ValueError("Transaction type must be 'sale' or 'purchase'")
        
        # Add transaction to list
        self.line_list.append({
            "wine": wine_instance,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": price
        })

        # Create line frame
        frame_line = ctk.CTkFrame(self, fg_color="transparent")

        # Create line number label
        column_line_number = ctk.CTkLabel(
            frame_line,
            text=f"{self.line_counter}.",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_LABEL,
            width=50,
            wraplength=50
        )

        # Create wine name label
        column_name = ctk.CTkLabel(
            frame_line,
            text=wine_instance.name,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_LABEL,
            width=200,
            wraplength=200
        )

        # Position line number and name
        column_line_number.grid(
            row=0, column=0, 
            padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y
        )
        column_name.grid(
            row=0, column=1, 
            padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y
        )

        # Create quantity, price, and subtotal labels
        for i, column_text in enumerate(
            [quantity, f"€ {price}", f"€ {subtotal}"], start=2
        ):
            label_column = ctk.CTkLabel(
                frame_line,
                text=str(column_text),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
                wraplength=100
            
            )
            label_column.grid(
                row=0, column=i,
                padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y
            )

        # Create remove button
        button_remove = ctk.CTkButton(
            frame_line,
            text="X",
            fg_color=Colours.BTN_CLEAR,
            text_color=Colours.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            width=30,
            cursor="hand2",
            command=lambda: self.remove_line(frame_line, subtotal)
        )
        button_remove.grid(
            row=0, column=6, sticky="e", 
            padx=Spacing.BUTTON_X, pady=Spacing.BUTTON_Y
        )
        
        # Pack line frame
        frame_line.pack(padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y)

        # Update total value
        self.update_total_value(subtotal)
    
    def remove_line(self, parent_frame: ctk.CTkFrame, subtotal: Decimal) -> None:
        """
        Remove a transaction line from the table.
        
        Updates line numbers for remaining lines, adjusts total, and triggers 
        callback if provided.
        
        Parameters:
            parent_frame: Frame containing the line to remove
            subtotal: Subtotal amount to subtract from total
        """
        # Extract wine name and quantity from line
        wine_name = parent_frame.winfo_children()[1].cget("text").strip() 
        quantity = parent_frame.winfo_children()[2].cget("text")
        
        # Get line index (convert "1." to 0-based index)
        line_table_index = parent_frame.winfo_children()[0].cget("text")
        line_table_index = int(line_table_index.replace(".","")) - 1
        
        # Update total value
        self.update_total_value(subtotal, subtract=True)

        # Update line numbers for subsequent lines
        # Skip first 2 children (headers and total label)
        current_index = line_table_index
        for line in self.winfo_children()[line_table_index + 2:]:
            label_line_number = line.winfo_children()[0]
            if isinstance(label_line_number, ctk.CTkLabel):
                label_line_number.configure(text=f"{current_index}.")
                current_index += 1

        # Remove line from UI and data
        parent_frame.destroy()
        del self.line_list[line_table_index]
        self.line_counter -= 1
        
        # Trigger callback with updated state
        if self.on_lines_change:
            self.on_lines_change(len(self.line_list), wine_name, int(quantity))

    def update_total_value(
        self, subtotal: Decimal, subtract: bool = False
    ) -> None:
        """
        Update the total amount by adding or subtracting a subtotal.
        
        Parameters:
            subtotal: Amount to add or subtract from total
            subtract: If True, subtract subtotal; otherwise add it
        """
        # Parse total value
        current_total = Decimal(self.total_var.get().replace("€ ", ""))
        
        # Calculate new total
        if subtract:
            new_total = current_total - subtotal
        else:
            new_total = current_total + subtotal
        
        # Update total variable
        self.total_var.set(f"€ {new_total}")
    
    def get_line_list(self) -> list[dict]:
        """
        Get list of all transaction lines.
        
        Returns:
            List of dictionaries, each containing wine, transaction_type,
            quantity, and price for a line
        """
        return self.line_list
    
