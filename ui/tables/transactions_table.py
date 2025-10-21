"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, date
from typing import Callable, Dict, List

from helpers import get_coords_center
from ui.components import ActionMenuButton
from ui.forms.add_edit_transaction import EditTransactionForm
from ui.style import Colours, Fonts
from ui.tables.data_table import DataTable
from ui.tables.mixins import SortMixin


class TransactionsTable(DataTable, SortMixin):
    """
    Contains the components of the table with the wine purchases and sellings.
    Uses incremental data loading and it can sort and filter rows.
    """
    def __init__(self, root: ctk.CTkFrame, *args, **kwargs):
        # Set up form frame
        super().__init__(root, *args, **kwargs)

        # Create table
        self.column_widths = [115, 120, 100, 115, 100, 80, 100, 100]
        self.remove_lines = True
        self.create_components()
        self.setup_sorting()
        self.refresh_visible_rows()

    def customize_row(self, line, frame_row):
        """
        Create a row for the line called by refresh visible rows.
        Parameters:
            line: Instance of a stock_movement (purchase or sale)
        Returns:
            row_frame: A ctkframe containing the labels of the line (row)
        """
        column_index = len(self.headers)
        label = ctk.CTkLabel(
            frame_row,
            width= self.column_widths[-1],
            text=""
        )
        label.grid(row=0, column=column_index, padx=5, sticky="ew")
        
        ActionMenuButton(
            label,
            btn_name="Transaction",
            on_edit=lambda t=line: self.edit_transaction(t),
            on_delete=lambda t=line: self.delete_transaction(t),
        ).grid(row=0, column=0, padx=5)
        
        frame_row.grid_columnconfigure(column_index, weight=1)

    def delete_transaction(self, transaction) -> None:
        """
        Removes the line where the button that triggered the event was clicked
        """
        # Ask user for confirmation
        confirm_dialog = messagebox.askyesno(
            "Confirm Removal",
            (f"Do you want to remove the {transaction.transaction_type} for € " 
            + f"{transaction.quantity * transaction.price}?")
        )
        if not confirm_dialog:
            return

        # Remove line from db
        self.session.delete(transaction)
        self.session.commit()

        # Remove line from lines list
        self.lines.remove(transaction)
        self.filtered_lines.remove(transaction)

        # Remove line from UI
        self.line_widget_map[transaction].destroy()
        del self.line_widget_map[transaction]

        # Update load more button
        self.create_load_more_button()

        # Show a message
        messagebox.showinfo(
            "Transaction Removed",
            "The transaction has been successfully removed."
        )
    
    def get_line_columns(self, line) -> List:
        """
        Returns a list with the values of the instance stored in "line".
        Parameters:
            - line: DB instance of an imported table
        Returns:
            - A list with the values of the instance formatted to be used as
            the text of a label.
        """
        return [
            str(line.datetime), line.wine.name, line.wine.code,
            line.transaction_type.capitalize(), str(line.quantity), f"€ {line.price}",
            f"€ {line.quantity * line.price}"
        ]

    def on_header_click(self, event, col_index: int):
        """
        After clicking a header, add an arrow on its name and sort it.
        """
        # Sort rows
        self.sort_table(event, col_index)

        # Refresh rows
        self.refresh_visible_rows()   

    def get_sorting_keys(self) -> Dict[int, Callable]:
        """
        Get a dict of callables used as sorting keys.
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
            self, filtered_names, filtered_codes, transaction_type, date_from, 
            date_to
        ):
        """
        Update the table by filters. 
        """
        # Convert date strings to date
        date_from = datetime.strptime(date_from, "%d/%m/%Y").date() if date_from else date(1900, 1, 1)
        date_to = datetime.strptime(date_to, "%d/%m/%Y").date() if date_to else datetime.today().date()
        
        # Update filtered lines
        self.filtered_lines = []
   
        for line in self.lines:
            if (                
                line.wine.name.lower() in filtered_names
                and line.wine.code.lower() in filtered_codes
                and (line.transaction_type.lower() == transaction_type or not transaction_type)
                and date_from <= line.datetime.date() <= date_to
            ):
                self.filtered_lines.append(line)

        # Sort rows
        if self.last_sort:
            self.sort_by(self.last_sort, new_sort=False)

        # restart index and rows
        self.visible_rows_count = self.INITIAL_ROWS
        self.refresh_visible_rows()

    def edit_transaction(self, transaction):
        """
        Open a new modal window to edit an existing transaction.
        Parameters:
            - wine: Wine instance of the clicked row.
        """
        # Create a modal top level
        edit_window = ctk.CTkToplevel(
            self.winfo_toplevel(),
            fg_color=Colours.BG_MAIN,
        )
        edit_window.title("Edit Transaction")
        
        center_x, center_y = get_coords_center(edit_window)
        w_width, w_height = 700, min(int(self.winfo_screenheight() * 0.8), 1000)
        edit_window.geometry(f"{w_width}x{w_height}+{center_x - w_width}+{center_y}")
        edit_window.update_idletasks() # Necessary to then use grab_set
        edit_window.grab_set()
        edit_window.focus_set()
        
        # Add scroll
        frame_scroll = ctk.CTkScrollableFrame(
            edit_window,
            fg_color="transparent"
        )
        frame_scroll.pack(expand=True, fill="both")

        # Add title
        title = ctk.CTkLabel(
            frame_scroll,
            text="Edit Transaction",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )

        # Place title       
        title.grid(row=0, column=0, pady=(20, 0), sticky="n")

        # Add form
        form = EditTransactionForm(
            frame_scroll,
            session=self.session,
            fg_color="transparent",
            movement=transaction,
            on_save=self.refresh_edited_rows,
        )
        form.grid(row=1, column=0, pady=(10, 0), sticky="nsew")

        # Make everything responsive
        frame_scroll.grid_columnconfigure(0, weight=1)

    def refresh_edited_rows(self, movement):
        """
        After a movement is edited, it refreshes the table/
        """
        # Delete old movement address from move_widget_map
        del self.line_widget_map[movement]
        # Refresh list
        self.refresh_visible_rows()
        # Refresh lists in filters form
        self.master.filters_form.update_lists()