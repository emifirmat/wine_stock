"""
Table that contains the list of added wines with their stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import Callable, Dict, List

from db.models import Wine
from helpers import load_ctk_image
from ui.components import DoubleLabel, FixedSizeToplevel
from ui.style import Colours, Fonts
from ui.tables.mixins import SortMixin
from ui.tables.data_table import DataTable


class WinesTable(DataTable, SortMixin):
    """
    Contains the components of the table with the wine purchases and sellings.
    """
    INITIAL_ROWS = 40 
    LOAD_MORE_ROWS = 30

    def __init__(self, root: ctk.CTkFrame, *args, **kwargs):
        # Set up form frame
        super().__init__(root, *args, **kwargs)
        
        # Track opened toplevels
        self.opened_toplevels = {}

        # Create table
        self.column_width = 98
        self.remove_lines = True
        self.create_components()
        self.setup_sorting()
        self.refresh_visible_rows()

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
            line.code, line.picture_path_display, line.name, str(line.vintage_year), 
            line.origin_display, str(line.quantity), f"€ {line.purchase_price}", 
            f"€ {line.selling_price}"
        ]

    def on_header_click(self, event, col_index: int):
        """
        After clicking a header, add an arrow on its name and sort it.
        """
        # Sort and refresh rows
        self.sort_table(event, col_index)
        self.refresh_visible_rows()    

    def get_sorting_keys(self) -> Dict[int, Callable]:
        """
        Get a dict of callables used as sorting keys.
        """
        return {
            0: lambda l: l.code.upper(),
            1: None,
            2: lambda l: l.name.lower(),
            3: lambda l: l.vintage_year,
            4: lambda l: l.origin.lower(),
            5: lambda l: l.quantity,
            6: lambda l: l.purchase_price,
            7: lambda l: l.selling_price
        }
 
    def apply_filters(
            self, filtered_names, filtered_codes, filtered_wineries, wine_colour, 
            wine_style, wine_varietal, wine_year, filtered_origin
        ):
        """
        Update the table by filters. 
        """
        # Update filtered lines
        self.filtered_lines = []

        for line in self.lines:
            if (                
                line.name.lower() in filtered_names
                and line.code.lower() in filtered_codes
                and line.winery.lower() in filtered_wineries
                and (line.colour.name.capitalize() == wine_colour or not wine_colour)
                and (line.style.name.capitalize() == wine_style or not wine_style)
                and (line.varietal_display.capitalize() == wine_varietal or not wine_varietal)
                and (str(line.vintage_year) == wine_year or not wine_year)
                and line.origin.lower() in filtered_origin

            ):
                self.filtered_lines.append(line)

        # Sort rows
        if self.last_sort:
            self.sort_by(self.last_sort, new_sort=False)

        # restart index and rows
        self.visible_rows_count = self.INITIAL_ROWS
        self.refresh_visible_rows()

    def customize_row(self, line: Wine, row_frame: ctk.CTkFrame):
        """
        Create a row for the line called by refresh visible rows.
        Parameters:
            line: Instance of a stock_movement (purchase or sale)
        Returns:
            row_frame: A ctkframe containing the labels of the line (row)
        """
        button_details = ctk.CTkButton(
            row_frame,
            text="+",
            fg_color=Colours.BTN_SAVE,
            text_color=Colours.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            width=30,
            cursor="hand2",
            command=lambda l=line: self.show_details(l) 
        )
        button_details.grid(row=0, column=len(self.headers), padx=5)

    def show_details(self, line: Wine):
        """
        Creates a toplevel that shows the details of the click wine.
        """
        # Check the clicked wine is not opened
        if line in self.opened_toplevels and self.opened_toplevels[line]:
            return

        # Create top level
        tl_width = 350
        tl_height = 500
        toplevel = ctk.CTkToplevel(
            self,
            fg_color=Colours.BG_MAIN,
        )
        toplevel.title("Wine Details")
        toplevel.resizable(False, False)
        toplevel.protocol(
            "WM_DELETE_WINDOW", lambda tl=toplevel, l=line: self.toplevel_on_close(tl, l)
        )
        self.opened_toplevels[line] = True
        
        # Locate TopLevel
        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()
        x = (screen_width // 2) - (tl_width // 3)
        y = (screen_height // 2) + (tl_height // 3)
        toplevel.geometry(f"{tl_width}x{tl_height}+{x}+{y}")

        # Fill toplevel with widgets and details
        self.build_wine_details(toplevel, line)
        
    def build_wine_details(self, top_level: ctk.CTkToplevel, line: Wine):
        """
        It creates the image and details of the wine instance inside the toplevel.
        Parameters:
            - top_level: Container of the labels (images and details)
            - line: Instance of the DB class Wine
        """
        ctk.CTkLabel(
            top_level, 
            image=load_ctk_image(line.picture_path_display, size=(120, 120)),
            text="",  
        ).pack(padx=5, pady=(15, 0))

        # Set up double labels with wine details
        text_labels = [
            "name", "code", "winery", "colour", "style", "varietal", "vintage year",
            "origin", "stock", "purchase price", "selling price"
        ]

        text_values = [
            line.name, line.code, line.winery, line.colour.name.title(), 
            line.style.name.title(), line.varietal_display.title(), line.vintage_year, 
            line.origin_display, str(line.quantity), f"€ {line.purchase_price}", 
            f"€ {line.selling_price}"
        ]
        
        for text_label, text_value in zip(text_labels, text_values):
            label = DoubleLabel(
                top_level,
                label_title_text=text_label.capitalize(),
                label_value_text=text_value
            )
            label.set_columns_layout(120, 200, anchor="w")
            label.pack(anchor="w", padx=20, pady=(5, 0))

    def toplevel_on_close(self, toplevel: ctk.CTkToplevel, line: Wine):
        """
        When the toplevel is closed, it updates the dict opened_toplevels
        Parameters:
            -line: Instance of the DB class Wine
        """
        self.opened_toplevels[line] = False
        toplevel.destroy()
