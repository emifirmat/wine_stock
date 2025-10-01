"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, date
from typing import Callable, Dict, List

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
        self.column_width = 115
        self.remove_lines = True
        self.create_components()
        self.setup_sorting()
        self.refresh_visible_rows()

    def customize_row(self, line, row_frame):
        """
        Create a row for the line called by refresh visible rows.
        Parameters:
            line: Instance of a stock_movement (purchase or sale)
        Returns:
            row_frame: A ctkframe containing the labels of the line (row)
        """
        button_remove = ctk.CTkButton(
            row_frame,
            text="X",
            fg_color=Colours.BTN_CLEAR,
            text_color=Colours.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            width=30,
            cursor="hand2",
            command=lambda f=row_frame, l=line: self.remove_line(f, l) # Pass f, l to get the current value and not last one.
        )
        button_remove.grid(row=0, column=len(self.headers), padx=5)
    
    def remove_line(self, parent_frame: ctk.CTkFrame, instance) -> None:
        """
        Removes the line where the button that triggered the event was clicked
        """
        # Ask user for confirmation
        confirm_dialog = messagebox.askyesno(
            "Confirm Removal",
            (f"Do you want to remove the {instance.transaction_type} for € " 
            + f"{instance.quantity * instance.price}?")
        )
        if not confirm_dialog:
            return

        # Remove line from db
        self.session.delete(instance)
        self.session.commit()
       
        # Remove line from UI
        parent_frame.destroy()

        # Remove line from lines list
        self.lines.remove(instance)
        self.filtered_lines.remove(instance)

        # Update load more button
        self.create_load_more_button()
    
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
            str(line.datetime.replace(microsecond=0)), line.wine.name, line.wine.code,
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
                and (line.transaction_type.capitalize() == transaction_type or not transaction_type)
                and date_from <= line.datetime.date() <= date_to
            ):
                self.filtered_lines.append(line)

        # Sort rows
        if self.last_sort:
            self.sort_by(self.last_sort, new_sort=False)

        # restart index and rows
        self.visible_rows_count = self.INITIAL_ROWS
        self.refresh_visible_rows()

        