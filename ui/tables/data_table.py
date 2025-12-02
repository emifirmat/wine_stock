"""
Base table component with incremental loading and sorting.

This module provides an abstract base class for data tables with features
like lazy loading, sorting, filtering, and customizable row rendering.
"""
import customtkinter as ctk
import tkinter as tk
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from helpers import load_ctk_image
from ui.style import Colours, Fonts, Spacing


class DataTable(ctk.CTkFrame, ABC):
    """
    Abstract base table with incremental data loading.
    
    Provides core functionality for displaying large datasets with pagination,
    sorting capabilities, and customizable row rendering. Subclasses must
    implement get_line_columns() for specific data formatting..
    """
    INITIAL_ROWS = 40 
    LOAD_MORE_ROWS = 30
    
    def __init__(
            self, root: ctk.CTkFrame, session: Session, headers: list[str],
            lines: list, **kwargs
        ):
        """
        Initialise data table with headers and data.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            headers: List of column header labels
            lines: List of data rows to display
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color=Colours.BG_MAIN, height=500)
        
        # DB instances
        self.session = session

        # Table data
        self.headers = headers
        self.lines = lines
        self.filtered_lines = lines.copy()
        self.visible_rows_count = self.INITIAL_ROWS
        self.line_widget_map = {}
        
        # Table UI components
        self.header_labels = []
        self.column_widths = None
        self.rows_container = None
        self.load_more_btn = None
        self.lbl_no_results = None       

    def create_components(self) -> None:
        """
        Create and display table headers, rows container, and empty state label.
        """
        # Create header row
        row_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_header_frame.pack(
            fill="x", padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y
        )

        for i, header in enumerate(self.headers):
            # Create header label
            label = ctk.CTkLabel(
                row_header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=self.column_widths[i],
                wraplength=self.column_widths[i],
                anchor="center",
            )
            label.grid(
                row=0, column=i, 
                padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y, sticky="ew"
            )

            # Make header clickable for sorting (except special columns)
            if header.lower() not in ["picture", "actions"]:
                label.configure(cursor="hand2")
                label.bind(
                    "<Button-1>", 
                    lambda e, col_index=i: self.on_header_click(e, col_index)
                )
                self.header_labels.append(label)

            # Configure column responsiveness
            row_header_frame.grid_columnconfigure(i, weight=1)

        # Create rows container
        self.rows_container = ctk.CTkFrame(self, fg_color="transparent")
        self.rows_container.pack(fill="both", expand=True) 

        # Create "no results" label (hidden by default)
        self.lbl_no_results = ctk.CTkLabel(
            self.rows_container,
            text="No results found.",
            font=Fonts.TEXT_LABEL,
            text_color=Colours.TEXT_MAIN,
            anchor="center",
        )
        
    def refresh_visible_rows(self) -> None:
        """
        Update displayed rows based on current filter and pagination state.
        
        Shows only the visible slice of filtered data, creating or reusing
        widgets as needed. Displays "no results" message if no data matches.
        """
        # Hide all existing widgets
        for widget in self.rows_container.winfo_children():
            widget.grid_forget()
        
        # Show "no results" message if no filtered data
        if not self.filtered_lines:
            self.lbl_no_results.grid(
                row=0, column=0, sticky="ew", columnspan=len(self.headers)
            )
            self.rows_container.columnconfigure(1, weight=1)
            return
        
        # Determine rows to display
        rows_to_show = min(self.visible_rows_count, len(self.filtered_lines))
        visible_slice = self.filtered_lines[:rows_to_show]
        
        # Show or create widgets for visible rows
        for i, line in enumerate(visible_slice):
            # Reuse existing widget if available
            if line in self.line_widget_map:
                widget = self.line_widget_map[line]
            # Create new widget
            else:
                widget = self.create_row_widget(line)
                self.line_widget_map[line] = widget
            
            # Display widget
            widget.grid(
                row=i, column=0, columnspan=len(self.headers),
                padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y, sticky="ew"
            )
        
        # Configure column responsiveness
        self.rows_container.grid_columnconfigure(0, weight=1)
        
        # Add "load more" button if needed
        self.create_load_more_button()

    def create_row_widget(self, line) -> ctk.CTkFrame:
        """
        Create a widget for a single data row.
        
        Builds a frame with labels for each column value. Handles both
        text and image content. Applies alert background for low stock items.
        
        Parameters:
            line: Data instance (e.g., Wine or StockMovement)
            
        Returns:
            Frame containing all column labels for the row
        """
        # Determine background color (alert if below minimum stock)
        row_bg = (
            Colours.BG_ALERT 
            if hasattr(line, "min_stock") and line.is_below_min_stock
            else "transparent"
        )
        
        # Create row frame
        # Note: row_frame is placed by refresh_visible_rows
        row_frame = ctk.CTkFrame(self.rows_container, fg_color=row_bg)

        # Create label for each row
        line_values = self.get_line_columns(line)
        for i, line_value in enumerate(line_values):
            # Detect if value is an image path
            is_image = (
                isinstance(line_value, str) and
                line_value.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
            )

            # Configure label for text or image
            if not is_image:
                label_config = {
                    "text": str(line_value),
                    "text_color": Colours.TEXT_MAIN,
                    "font": Fonts.TEXT_LABEL,   
                }
            # Image labels
            else:
                label_config = {
                    "image": load_ctk_image(line_value),
                    "text": "",   
                    "fg_color": "transparent"
                }
            
            # Create and position label
            label = ctk.CTkLabel(
                row_frame, 
                width=self.column_widths[i],
                wraplength=self.column_widths[i],
                **label_config
            )
            
            label.grid(
                row=0, column=i, 
                padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y, sticky="ew"
            )

            # Configure column responsiveness
            row_frame.grid_columnconfigure(i, weight=1)

        # Allow subclasses to add custom widgets
        self.customize_row(line, row_frame)

        return row_frame

    @abstractmethod
    def get_line_columns(self, line) -> list:
        """
        Get formatted column values for a data row.
        
        Subclasses must implement this to extract and format values
        from their specific data model.
        
        Parameters:
            line: Data instance from the table
            
        Returns:
            List of formatted values for each column
        """
        raise NotImplementedError("Subclasses must implement get_line_columns()")


    def create_load_more_button(self) -> None:
        """
        Create or update the 'Load More' button based on remaining rows.
        """
        # Remove existing button
        if self.load_more_btn:
            self.load_more_btn.destroy()
            self.load_more_btn = None

        # Calculate remaining rows
        remaining_rows = len(self.filtered_lines) - self.visible_rows_count

        # Only show button if more rows available                
        if remaining_rows > 0:
            text_content = (
                f"Load {min(remaining_rows, self.LOAD_MORE_ROWS)} More Rows "
                f"({remaining_rows} left)"
            )
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
            # Position at end of visible rows
            self.load_more_btn.grid(
                row=self.visible_rows_count, 
                padx=Spacing.BUTTON_X, pady=Spacing.BUTTON_Y, sticky="ew"
            )

    def load_more_rows(self) -> None:
        """
        Increase visible row count and refresh display.
        """
        self.visible_rows_count += self.LOAD_MORE_ROWS
        self.refresh_visible_rows()

    def on_header_click(self, event: tk.Event, col_index: int) -> None:
        """
        Handle header click event for sorting.
        
        Override this method to implement sorting functionality.
        
        Parameters:
            event: Click event from header label
            col_index: Index of clicked column
        """
        pass

    def customize_row(self, line, widget: ctk.CTkFrame) -> None:
        """
        Add custom widgets to a row.
        
        Override this method to add action buttons or other custom
        widgets to specific rows.
        
        Parameters:
            line: Data instance for the row
            widget: Row frame to customize
        """
        pass