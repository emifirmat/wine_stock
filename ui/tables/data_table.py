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
from ui.style import Colours, Fonts, Spacing, Placeholders


class DataTable(ctk.CTkFrame, ABC):
    """
    Abstract base table with incremental data loading.
    
    Provides core functionality for displaying large datasets with pagination,
    sorting capabilities, and customizable row rendering. Subclasses must
    implement get_line_columns() for specific data formatting.
    """
    INITIAL_ROWS = 30 
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
        self.configure(fg_color=Colours.BG_MAIN)
        
        # DB instances
        self.session = session

        # Table data
        self.headers = headers
        self.lines = lines
        self.filtered_lines = lines.copy()
        self.visible_rows_count = self.INITIAL_ROWS
        self.line_widget_map = {}
        self.missing_image_paths = set()
        self._last_missing_images_count = 0
        
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
                wraplength=self.column_widths[i] - Spacing.TABLE_CELL_X * 2,
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
        self.rows_container.columnconfigure(0, weight=1)

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
        
        # Configure column responsiveness
        self.rows_container.columnconfigure(0, weight=1)

        # Show "no results" message if no filtered data
        if not self.filtered_lines:
            self.lbl_no_results.grid(
                row=0, column=0, sticky="ew", columnspan=len(self.headers)
            )
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
        
        # Add "load more" button if needed
        self.create_load_more_button()

        # Show missing images warning
        if self.missing_image_paths:
            # Get total missing_image_paths
            new_count = len(self.missing_image_paths)
            # Show message when there are new missing images
            if new_count > self._last_missing_images_count:
                self.show_missing_images_warning(new_count - self._last_missing_images_count)
                # Update count to prevent permanent warnings
                self._last_missing_images_count = new_count

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
        # Note: Positioning is handled by refresh_visible_rows()
        row_frame = ctk.CTkFrame(self.rows_container, fg_color=row_bg)

        # Create label for each column
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
            else:
                # Handle image loading with fallback
                try:
                    if line_value == "default.png":
                        image = Placeholders.WINE_DEFAULT
                    else:
                        image = load_ctk_image(line_value)
                except FileNotFoundError:
                    # Record missing image and use warning placeholder
                    self.missing_image_paths.add(line_value)
                    print(f"[WARN] Image not found: {line_value}")
                    image = Placeholders.WINE_WARNING

                label_config = {
                    "image": image,
                    "text": "",   
                    "fg_color": "transparent"
                }
            
            # Create and position label
            label = ctk.CTkLabel(
                row_frame, 
                width=self.column_widths[i],
                wraplength=self.column_widths[i] - Spacing.TABLE_CELL_X * 2,
                **label_config
            )
            
            label.grid(
                row=0, column=i, 
                padx=Spacing.TABLE_CELL_X, pady=Spacing.TABLE_CELL_Y, sticky="ew"
            )

            # Configure column responsiveness
            row_frame.grid_columnconfigure(i, weight=1)

        # Allow subclasses to add custom widgets (e.g., action buttons)
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

        Displays a button showing how many more rows can be loaded. Removes
        the button if all rows are already visible.
        """
        # Remove existing button
        if self.load_more_btn:
            self.load_more_btn.destroy()
            self.load_more_btn = None

        # Calculate remaining rows
        remaining_rows = len(self.filtered_lines) - self.visible_rows_count

        # Only show button if more rows available                
        if remaining_rows > 0:
            rows_to_load = min(remaining_rows, self.LOAD_MORE_ROWS)
            text_content = f"Load {rows_to_load} More Rows ({remaining_rows} left)"
            
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
                padx=Spacing.BUTTON_X, pady=Spacing.BUTTON_Y, sticky="ew",
                columnspan=len(self.headers)
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
        
        Override this method in subclasses to implement sorting functionality.
        
        Parameters:
            event: Click event from header label
            col_index: Index of clicked column
        """
        pass

    def customize_row(self, line, widget: ctk.CTkFrame) -> None:
        """
        Add custom widgets to a row.
        
        Override this method in subclasses to add action buttons or other custom
        widgets to specific rows (e.g., edit, delete, view details).
        
        Parameters:
            line: Data instance for the row
            widget: Row frame to customize
        """
        pass

    def show_missing_images_warning(self, count: int) -> None:
        """
        Display warning about missing images.
        
        Override this method in subclasses to show appropriate warnings
        when image files cannot be loaded.
        
        Parameters:
            count: Number of missing images
        """
        pass