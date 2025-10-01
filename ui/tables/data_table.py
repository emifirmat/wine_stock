"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Callable, Dict, List

from helpers import load_ctk_image
from ui.style import Colours, Fonts


class DataTable(ctk.CTkFrame, ABC):
    """
    Contains the components of the table with the wine purchases and sellings.
    Uses incremental data loading and it can sort and filter rows.
    """
    INITIAL_ROWS = 40 
    LOAD_MORE_ROWS = 30
    
    def __init__(
            self, root: ctk.CTkFrame, session, headers: list[str], lines: list, 
            **kwargs
        ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(fg_color=Colours.BG_MAIN, height=500)
        
        # Include db instances
        self.session = session

        # Table data
        self.headers = headers
        self.lines = lines
        self.filtered_lines = lines.copy()
        self.visible_rows_count = self.INITIAL_ROWS
        self.line_widget_map = {}
        
        # Table UI
        self.header_labels = []
        self.column_width = None
        self.rows_container = None
        self.load_more_btn = None
        self.lbl_no_results = None       

    def create_components(self):
        """
        Create headers, rows container, and "no results" message.
        """
        # Headers
        row_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_header_frame.pack(fill="x", pady=2)

        for i, header in enumerate(self.headers):
            # Create label
            label = ctk.CTkLabel(
                row_header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=self.column_width,
                wraplength=self.column_width,
                cursor="hand2" if header != "picture" else "arrow"
            )
            label.grid(row=0, column=i, padx=5)

            if header != "picture":
                # Bind label with a click
                label.bind(
                    "<Button-1>", 
                    lambda e, col_index=i: self.on_header_click(e, col_index)
                )

                # Add label in header_labels 
                self.header_labels.append(label)

        # Rows container
        self.rows_container = ctk.CTkFrame(self, fg_color="transparent")
        self.rows_container.pack(fill="both", expand=True) 

        # No results label  
        self.lbl_no_results = ctk.CTkLabel(
            self.rows_container,
            text="No results found.",
            font=Fonts.TEXT_LABEL,
            text_color=Colours.TEXT_MAIN,
            anchor="center",
        )
        
        # Let columns expand to fill the width
        for i in range(len(self.headers)):
            self.rows_container.grid_columnconfigure(i, weight=1)
        
    def refresh_visible_rows(self):
        """
        Creates/shows only visible rows.
        """
        # Hide all the widgets
        for widget in self.rows_container.winfo_children():
            widget.grid_forget()
        
        # If there is no filtered_lines, show message "no results"
        if not self.filtered_lines:
            self.lbl_no_results.grid(
                row=0, column=0, sticky="ew", columnspan=len(self.header_labels)
            )  
            return
        
        # Show/create the slice's widgets
        rows_to_show = min(self.visible_rows_count, len(self.filtered_lines))
        visible_slice = self.filtered_lines[:rows_to_show]
        
        for i, line in enumerate(visible_slice):
            # Get existing widget
            if line in self.line_widget_map:
                widget = self.line_widget_map[line]
            # Create new widget
            else:
                widget = self.create_row_widget(line)
                self.customize_row(line, widget)
                self.line_widget_map[line] = widget
            # Show widget    
            widget.grid(row=i, pady=2)
        
        # Add "load more" button
        self.create_load_more_button()

    def create_row_widget(self, line) -> ctk.CTkFrame:
        """
        Create a row for the line called by refresh visible rows.
        Parameters:
            line: Instance of a stock_movement (purchase or sale)
        Returns:
            row_frame: A ctkframe containing the labels of the line (row)
        """
        # Crate row frame
        row_frame = ctk.CTkFrame(self.rows_container, fg_color="transparent")
        # Note: row_frame is placed by refresh_visible_rows

        # Create labels of the row
        line_columns = self.get_line_columns(line)
        for j, line_column in enumerate(line_columns):
            # Text labels
            if not line_column.startswith("assets/user_images/wines"): 
                label_config = {
                    "text": line_column,
                    "text_color": Colours.TEXT_MAIN,
                    "font": Fonts.TEXT_LABEL,   
                }
           # Image labels
            else:
                label_config = {
                    "image": load_ctk_image(line_column),
                    "text": "",   
                }
            
            label = ctk.CTkLabel(
                row_frame, 
                width=self.column_width,
                wraplength=self.column_width,
                **label_config
            )
            
            label.grid(row=0, column=j, padx=5)

        return row_frame

    @abstractmethod
    def get_line_columns(self, line) -> List:
        """
        Returns a list with the values of the instance stored in "line".
        Parameters:
            - line: DB instance of an imported table
        Returns:
            - A list with the values of the instance formatted to be used as
            the text of a label.
        """
        raise NotImplementedError


    def create_load_more_button(self):
        """
        Creates or updates button "Load More"
        """
        # Destroy existing button
        if self.load_more_btn:
            self.load_more_btn.destroy()
            self.load_more_btn = None

        # Only show button if there are more rows to show
        remaining_rows = len(self.filtered_lines) - self.visible_rows_count
        text_content = (
            f"Load {min(remaining_rows, self.LOAD_MORE_ROWS)} More Rows "
            f"({remaining_rows} left)"
        )
                        
        if remaining_rows > 0:
            self.load_more_btn = ctk.CTkButton(
                self.rows_container,
                text=text_content,
                fg_color=Colours.BTN_SAVE,
                hover_color=Colours.BG_HOVER_BTN_SAVE,
                font=Fonts.TEXT_BUTTON,
                text_color=Colours.TEXT_BUTTON,
                height=35,
                cursor="hand2",
                command=self.load_more_rows
            )
            # Place it at the end of the table
            self.load_more_btn.grid(row=self.visible_rows_count, pady=15, sticky="ew")

    def load_more_rows(self):
        """Load more rows incrementally"""
        # Increase count
        self.visible_rows_count += self.LOAD_MORE_ROWS
        
        # Refresh rows
        self.refresh_visible_rows()

    def on_header_click(self, event, col_index: int):
        """
        After clicking a header, add an arrow on its name and sort it.
        """
        # Sort rows
        pass

    def customize_row(self, line, widget):
        pass