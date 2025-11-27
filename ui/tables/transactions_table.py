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
from ui.components import ActionMenuButton
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
        edit_window = ctk.CTkToplevel(
            self.winfo_toplevel(),
            fg_color=Colours.BG_MAIN,
        )
        edit_window.title("Edit Transaction")
        
        # Remove window decorations (title bar)
        # Note: WSL becomes unstable if this is removed
        if running_in_wsl():
            edit_window.overrideredirect(False)
            print(
                "Warning: This app is running under Windows Subsystem for Linux (WSL). "
                "Standard window borders have been enabled to improve stability."
            )
        else:
            edit_window.overrideredirect(True)
            

        # Define window dimensions
        w_width= 700

        # Get parent window info
        parent = self.winfo_toplevel()
        parent.update_idletasks() # Get parent's last dimensions
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        screen_height = edit_window.winfo_screenheight()

        # Calculate max height
        max_height = int(screen_height * 0.8)

        # Temporarily set geometry  
        center_x = parent_x + (parent_width - w_width) // 2
        edit_window.geometry(f"{w_width}x{max_height}+{center_x}+{parent_y}")
        edit_window.update_idletasks()
        
        # Create main container with border
        main_container = ctk.CTkFrame(
            edit_window,
            fg_color=Colours.BG_MAIN,
            border_width=2,
            border_color=Colours.BORDERS
        )
        main_container.pack(expand=True, fill="both")

        # Create custom title bar
        title_bar = ctk.CTkFrame(
            main_container,
            fg_color=Colours.BG_HOVER_NAV,
            height=40
        )
        title_bar.pack(fill="x", side="top", padx=Spacing.XSMALL, pady=Spacing.XSMALL)
        title_bar.pack_propagate(False)  # Maintain fixed height
        
        # Create close button
        close_button = ctk.CTkButton(
            title_bar,
            text="✕",
            text_color=Colours.TEXT_MAIN,
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=Colours.BG_SECONDARY,
            command=lambda: self._close_edit_window(edit_window),
            font=Fonts.SUBTITLE,
        )
        close_button.pack(side="right", padx=Spacing.SMALL, pady=Spacing.SMALL)

        # Create title label
        title_label = ctk.CTkLabel(
            title_bar,
            text="Edit Transaction",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.SUBTITLE,
        )
        title_left_padding = Spacing.SMALL + 30 # Close button width
        title_label.pack(
            side="left", expand=True, fill="both",
            padx=(title_left_padding, Spacing.SMALL), pady=Spacing.SMALL
        )
        
        # Make title bar draggable
        self._make_draggable(title_bar, edit_window)
        self._make_draggable(title_label, edit_window)

        # Add edit form
        form = EditTransactionForm(
            main_container,
            session=self.session,
            fg_color="transparent",
            movement=transaction,
            on_save=self.refresh_edited_rows,
        )
        form.pack(
            fill="both", expand=True, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y
        )

        # Force update to get actual widget sizes
        edit_window.update_idletasks()
        
        # Calculate required height
        title_bar_height = 40
        form_height = form.winfo_reqheight()
        total_padding = (Spacing.XSMALL * 2) + (Spacing.SECTION_Y * 2)
        w_height = min(title_bar_height * 2 + form_height + total_padding, max_height)

        # Set final geometry
        edit_window.geometry(f"{w_width}x{w_height}")
        
        edit_window.grab_set() # Modal window
        edit_window.focus_set()

    def _close_edit_window(self, window: ctk.CTkToplevel) -> None:
        """
        Close the edit window and release grab.

        Parameters:
            window: Edit window Toplevel
        """
        window.grab_release()
        window.destroy()

    def _make_draggable(self, title_bar:ctk.CTkFrame, window: ctk.CTkToplevel) -> None:
        """
        Make window draggable by clicking and dragging the title bar.

        Parameters:
            title_bar: Frame with the title and close button
            window: Edit window Toplevel
        """
        def start_move(event):
            window.x = event.x
            window.y = event.y

        def do_move(event):
            deltax = event.x - window.x
            deltay = event.y - window.y
            x = window.winfo_x() + deltax
            y = window.winfo_y() + deltay
            window.geometry(f"+{x}+{y}")

        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

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