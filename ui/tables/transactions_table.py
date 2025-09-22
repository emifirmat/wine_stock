"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, date

from ui.style import Colours, Fonts


class TransactionsTable(ctk.CTkFrame):
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
        self.configure(
            fg_color=Colours.BG_MAIN,
            height=500
        )
        
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
        self.rows_container = None
        self.load_more_btn = None
        self.lbl_no_results = None
        self.create_components()
        
        # Sorting data
        self.sort_reverse = False
        self.last_sort = None

        # Show rows
        self.refresh_visible_rows()

    def create_components(self):
        """
        Create headers, rows container, and "no results" message.
        """
        # Headers
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=2)

        for i, header in enumerate(self.headers):
            # Create label
            label = ctk.CTkLabel(
                header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=110,
                cursor="hand2"
            )
            label.grid(row=0, column=i, padx=5)

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
        for i in range(7):
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
            self.lbl_no_results.grid(row=0, column=0, sticky="ew", columnspan=7)  
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
        line_columns = [
            line.datetime.replace(microsecond=0), line.wine.name, line.wine.code,
            line.transaction_type.capitalize(), line.quantity, f"€ {line.price}",
            f"€ {line.quantity * line.price}"
        ]
        for j, line_column in enumerate(line_columns):
            label = ctk.CTkLabel(
                row_frame, 
                text=line_column,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=110,
                wraplength=110,
            )
            
            label.grid(row=0, column=j, padx=5)
        
        # Create button "Remove"
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
        button_remove.grid(row=0, column=len(line_columns), padx=5)

        return row_frame

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

    def on_header_click(self, event, col_index: int):
        """
        After clicking a header, add an arrow on its name and sort it.
        """
        # Get ctkLabel of the clicked header
        event_label = event.widget.master

        # Prevents an error when user click on label but not on the text
        if (not (
            0 <= event.x <= event_label.winfo_width() 
            and 0 <= event.y <= event_label.winfo_height()
        )):
            return
        
        # Clean arrow in all labels
        for lbl in self.header_labels:
            lbl_text = lbl.cget("text").replace("↑", "").replace("↓", "")
            lbl.configure(text=lbl_text)

        # Add arrow depending on order
        clean_text = event_label.cget("text").replace("↑", "").replace("↓", "")
        arrow = "↓" if self.sort_reverse else "↑"
        event_label.configure(text=clean_text + arrow)

        # Sort rows
        self.sort_by(col_index)

        # Refresh rows
        self.refresh_visible_rows()   

    def sort_by(self, col_index: int, new_sort: bool = True):
        """
        Order lines based on the clicked header.
        """
        sorting_keys = {
            0: lambda l: l.datetime,
            1: lambda l: l.wine.name.lower(),
            2: lambda l: l.wine.code.upper(),
            3: lambda l: l.transaction_type,
            4: lambda l: l.quantity,
            5: lambda l: l.price,
            6: lambda l: l.quantity * l.price
        }

        # Sort the list of filtered lines
        reverse = self.sort_reverse if new_sort else not self.sort_reverse
        self.filtered_lines.sort(key=sorting_keys[col_index], reverse=reverse)
        
        # Toggle reverse mode and save last sort
        if new_sort:
            self.sort_reverse = not self.sort_reverse
            self.last_sort = col_index     

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

        