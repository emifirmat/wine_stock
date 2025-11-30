"""
Transaction history table with sorting and filtering.

This module provides a table for displaying stock movement transactions
(sales and purchases) with capabilities for sorting, filtering, editing,
and deleting individual transactions.
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, date
from sqlalchemy.orm import Session
from typing import Callable

from helpers import running_in_wsl
from ui.components import ActionMenuButton, ToplevelCustomised
from ui.forms.add_edit_transaction import EditTransactionForm
from ui.style import Colours, Fonts, Spacing
from ui.tables.data_table import DataTable
from ui.tables.mixins import SortMixin
from db.models import StockMovement


class TransactionsTable(DataTable, SortMixin):
    """
    Table displaying stock movement transactions with CRUD operations.
    
    Extends DataTable and SortMixin to provide a sortable, filterable table
    of sales and purchases with edit and delete capabilities.
    """
    def __init__(self, root: ctk.CTkFrame, session: Session, *args, **kwargs):
        """
        Initialize transactions table with sorting and filtering.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            *args: Additional positional arguments for DataTable
            **kwargs: Additional keyword arguments for DataTable
        """
        super().__init__(root, session, *args, **kwargs)

        # Configure table layout
        self.column_widths = [115, 120, 100, 115, 100, 80, 100, 100]
        
        # Build table
        self.create_components()
        self.setup_sorting()
        self.refresh_visible_rows()

    def customize_row(self, line: StockMovement, frame_row: ctk.CTkFrame) -> None:
        """
        Add action menu button to transaction row.
        
        Parameters:
            line: StockMovement instance for the row
            frame_row: Frame containing the row
        """
        column_index = len(self.headers)

        # Create placeholder label for actions column
        label = ctk.CTkLabel(
            frame_row,
            width= self.column_widths[-1],
            text=""
        )
        label.grid(
            row=0, column=column_index, 
            padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y, sticky="ew"
        )
        
        # Add action menu button
        ActionMenuButton(
            label,
            btn_name="Transaction",
            on_edit=lambda t=line: self.edit_transaction(t),
            on_delete=lambda t=line: self.delete_transaction(t),
        ).grid(
            row=0, column=0,  
            padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y
        )
        
        frame_row.grid_columnconfigure(column_index, weight=1)

    def delete_transaction(self, transaction: StockMovement) -> None:
        """
        Delete a transaction after user confirmation.
        
        Removes transaction from database and updates UI accordingly.
        
        Parameters:
            transaction: StockMovement instance to delete
        """
        # Confirm deletion
        confirm_dialog = messagebox.askyesno(
            "Confirm Removal",
            (f"Do you want to remove the {transaction.transaction_type} for " 
            f"€ {transaction.quantity * transaction.price}?")
        )
        if not confirm_dialog:
            return

        # Delete from database
        self.session.delete(transaction)
        self.session.commit()

        # Remove from data lists
        self.lines.remove(transaction)
        self.filtered_lines.remove(transaction)

        # Remove from UI
        self.line_widget_map[transaction].destroy()
        del self.line_widget_map[transaction]

        # Update pagination button
        self.create_load_more_button()

        # Show success message
        messagebox.showinfo(
            "Transaction Removed",
            "The transaction has been successfully removed."
        )
    
    def get_line_columns(self, line: StockMovement) -> list[str]:
        """
        Get formatted column values for a transaction row.
        
        Parameters:
            line: StockMovement instance
            
        Returns:
            List of formatted strings for each column
        """
        return [
            str(line.datetime), line.wine.name, line.wine.code,
            line.transaction_type.capitalize(), str(line.quantity), f"€ {line.price}",
            f"€ {line.quantity * line.price}"
        ]

    def on_header_click(self, event, col_index: int) -> None:
        """
        Handle header click to sort table.
        
        Parameters:
            event: Click event from header label
            col_index: Index of clicked column
        """
        # Sort by clicked column
        self.sort_table(event, col_index)

        # Refresh display
        self.refresh_visible_rows()   

    def get_sorting_keys(self) -> dict[int, Callable]:
        """
        Get sorting key functions for each column.
        
        Returns:
            Dictionary mapping column indices to sorting functions
        """
        return {
            0: lambda l: l.datetime,
            1: lambda l: l.wine.name.lower(),
            2: lambda l: l.wine.code.upper(),
            3: lambda l: l.transaction_type,
            4: lambda l: l.quantity,
            5: lambda l: l.price,
            6: lambda l: l.quantity * l.price
        } 

    def apply_filters(
        self, filtered_names: list[str], filtered_codes: list[str],
        transaction_type: str, date_from: str, date_to: str
    ) -> None:
        """
        Filter transactions by wine, type, and date range.
        
        Parameters:
            filtered_names: List of wine names to include (lowercase)
            filtered_codes: List of wine codes to include (lowercase)
            transaction_type: Transaction type filter - "sale", "purchase", or empty
            date_from: Start date in format "dd/mm/yyyy" (empty for no limit)
            date_to: End date in format "dd/mm/yyyy" (empty for today) 
        """
        # Parse date strings
        date_from_obj = (
            datetime.strptime(date_from, "%d/%m/%Y").date() 
            if date_from else date(1900, 1, 1)
        )
        date_to_obj = (
            datetime.strptime(date_to, "%d/%m/%Y").date()
            if date_to else datetime.today().date()
        )
        
        # Apply filters
        self.filtered_lines = []
        
        for line in self.lines:
            if (                
                line.wine.name.lower() in filtered_names and 
                line.wine.code.lower() in filtered_codes and 
                (line.transaction_type.lower() == transaction_type or not transaction_type) and 
                date_from_obj <= line.datetime.date() <= date_to_obj
            ):
                self.filtered_lines.append(line)

        # Re-apply last sort if any
        if self.last_sort is not None:
            self.sort_by(self.last_sort, new_sort=False)

        # Reset pagination and refresh
        self.visible_rows_count = self.INITIAL_ROWS
        self.refresh_visible_rows()

    def edit_transaction(self, transaction: StockMovement) -> None:
        """
        Open modal window to edit a transaction.
        
        Parameters:
            transaction: StockMovement instance to edit
        """
        # Create a modal top level
        edit_window = ToplevelCustomised(
            self, width=700, title="Edit Transaction", modal=True
        )

        # Create edit form
        form = EditTransactionForm(
            edit_window.content_frame,
            session=self.session,
            fg_color="transparent",
            movement=transaction,
            on_save=self.refresh_edited_rows,
        )
        form.pack(
            fill="both", expand=True, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y
        )

        edit_window.refresh_geometry()

    def refresh_edited_rows(self, movement: StockMovement) -> None:
        """
        Refresh table after a transaction is edited.
        
        Updates widget mapping and refreshes filter options.
        
        Parameters:
            movement: Updated StockMovement instance
        """
        # Remove old widget from cache (address may have changed)
        if movement in self.line_widget_map:
            del self.line_widget_map[movement]
        
        # Refresh visible rows
        self.refresh_visible_rows()
        
        # Refresh filter options in parent form
        if hasattr(self.master, 'filters_form'):
            self.master.filters_form.update_lists()