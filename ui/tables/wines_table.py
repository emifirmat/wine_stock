"""
Wines table with sorting, filtering, and CRUD operations.

This module provides a table for displaying and managing the wine catalog
with capabilities for sorting, filtering, viewing details, editing, and
deleting wine records.
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Callable

from db.models import Wine
from helpers import load_ctk_image
from ui.components import DoubleLabel, ActionMenuButton, ToplevelCustomised
from ui.forms.add_edit_wine import AddWineForm
from ui.style import Spacing, Placeholders
from ui.tables.mixins import SortMixin
from ui.tables.data_table import DataTable


class WinesTable(DataTable, SortMixin):
    """
    Wine catalog table with CRUD operations and low stock alerts.
    
    Extends DataTable and SortMixin to provide a sortable, filterable table
    of wines with view, edit, and delete capabilities. Highlights wines below
    minimum stock and tracks opened detail windows to prevent duplicates.
    """
    INITIAL_ROWS = 40 
    LOAD_MORE_ROWS = 30

    def __init__(self, root: ctk.CTkFrame, session: Session, *args, **kwargs):
        """
        Initialize wines table with sorting and filtering.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            *args: Additional positional arguments for DataTable
            **kwargs: Additional keyword arguments for DataTable
        """
        super().__init__(root, session, *args, **kwargs)
        
        # Track opened detail windows to prevent duplicates
        self.opened_toplevels = {}

        # Configure table layout
        self.column_widths = [110, 120, 100, 90, 95, 80, 90, 90, 90, 80]
        
        # Build table
        self.create_components()
        self.setup_sorting()
        self.refresh_visible_rows()

    def get_line_columns(self, line: Wine) -> list[str]:
        """
        Get formatted column values for a wine row.
        
        Parameters:
            line: Wine instance
            
        Returns:
            List of formatted strings for each column
        """
        return [
            line.code, line.picture_path_display, line.name, str(line.vintage_year), 
            line.origin_display, str(line.quantity), line.min_stock_display,
            f"€ {line.purchase_price}", f"€ {line.selling_price}"
        ]

    def on_header_click(self, event: tk.Event, col_index: int) -> None:
        """
        Handle header click to sort table by column.
        
        Parameters:
            event: Click event from header label
            col_index: Index of clicked column
        """
        self.sort_table(event, col_index)
        self.refresh_visible_rows()    

    def get_sorting_keys(self) -> dict[int, Callable | None]:
        """
        Get sorting key functions for each column.
        
        Returns:
            Dictionary mapping column indices to sorting functions, with None 
            for non-sortable columns (picture, actions)
        """
        return {
            0: lambda l: l.code.upper(),
            1: None, # Picture column not sortable
            2: lambda l: l.name.lower(),
            3: lambda l: l.vintage_year,
            4: lambda l: l.origin.lower() if l.origin else "", # Handle optional field
            5: lambda l: l.quantity,
            6: lambda l: l.min_stock_sort,
            7: lambda l: l.purchase_price,
            8: lambda l: l.selling_price,
            9: None # Actions column not sortable
        }
 
    def apply_filters(
        self, filtered_names: list[str], filtered_codes: list[str],
        filtered_wineries: list[str], wine_colour: str, wine_style: str, 
        wine_varietal: str, wine_year: str, filtered_origin: list[str]
    ) -> None:
        """
        Filter wines by various criteria and refresh display.
        
        Parameters:
            filtered_names: List of wine names to include (lowercase)
            filtered_codes: List of wine codes to include (lowercase)
            filtered_wineries: List of winery names to include (lowercase)
            wine_colour: Colour filter (capitalized), empty for all
            wine_style: Style filter (capitalized), empty for all
            wine_varietal: Varietal filter (capitalized), empty for all
            wine_year: Year filter as string, empty for all
            filtered_origin: List of origins to include (lowercase) 
        """
        # Apply filters
        self.filtered_lines = []

        for line in self.lines:
            if (                
                line.name.lower() in filtered_names and 
                line.code.lower() in filtered_codes and 
                line.winery.lower() in filtered_wineries and 
                (line.colour.name.capitalize() == wine_colour or not wine_colour) and 
                (line.style.name.capitalize() == wine_style or not wine_style) and 
                (line.varietal_display.capitalize() == wine_varietal or not wine_varietal) and 
                (str(line.vintage_year) == wine_year or not wine_year) and 
                line.origin.lower() in filtered_origin
            ):
                self.filtered_lines.append(line)

        # Re-apply last sort if any
        if self.last_sort is not None:
            self.sort_by(self.last_sort, new_sort=False)

        # Reset pagination and refresh display
        self.visible_rows_count = self.INITIAL_ROWS
        self.refresh_visible_rows()

    def customize_row(self, line: Wine, frame_row: ctk.CTkFrame) -> None:
        """
        Add action menu button to wine row.
        
        Creates an action menu with options to view details, edit, or delete the wine.

        Parameters:
            line: Wine instance for the row
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
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y, sticky="ew"
        )

        # Add action menu button
        ActionMenuButton(
            label,
            btn_name="Wine",
            on_show=lambda w=line: self.show_details(w),
            on_edit=lambda w=line: self.edit_wine(w),
            on_delete=lambda w=line: self.delete_wine(w),
        ).grid(
            row=0, column=0, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y
        )

        frame_row.grid_columnconfigure(column_index, weight=1)

    def show_details(self, line: Wine) -> None:
        """
        Open window displaying wine details.
        
        Prevents opening multiple detail windows for the same wine by tracking
        open windows in self.opened_toplevels.
        
        Parameters:
            line: Wine instance to display
        """
        # Prevent duplicate windows
        if line in self.opened_toplevels and self.opened_toplevels[line]:
            return

        # Create detail window
        toplevel = ToplevelCustomised(
            self, width=450, title="Wine Details", 
            on_close=lambda: self.toplevel_on_close(toplevel, line)
        )
    
        self.opened_toplevels[line] = True

        # Build detail view
        self.build_wine_details(toplevel.content_frame, line)

        # Apply geometry and show
        toplevel.refresh_geometry()
        
    def build_wine_details(
            self, widgets_container: ctk.CTkFrame, line: Wine
        ) -> None:
        """
        Build wine detail view with image and attributes.
        
        Parameters:
            widgets_container: Container frame for detail widgets
            line: Wine instance to display
        """
        # Display wine image
        try:
            if line.picture_path_display == "default.png":
                image = Placeholders.WINE_DEFAULT_BIG
            else:
                image = load_ctk_image(line.picture_path_display, Placeholders.big_size)
        except FileNotFoundError:
            image = Placeholders.WINE_WARNING_BIG

        ctk.CTkLabel(
            widgets_container, 
            image=image,
            text="",  
        ).pack(padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y)

        # Define detail labels and values
        text_labels = [
            "name", "code", "winery", "colour", "style", "varietal", "vintage year",
            "origin", "stock", "min. stock", "purchase price", "selling price"
        ]

        text_values = [
            line.name, line.code, line.winery, line.colour.name.title(), 
            line.style.name.title(), line.varietal_display.title(), 
            str(line.vintage_year), line.origin_display, str(line.quantity), 
            line.min_stock_display, f"€ {line.purchase_price}", 
            f"€ {line.selling_price}"
        ]
        
        # Create detail labels
        for text_label, text_value in zip(text_labels, text_values):
            label = DoubleLabel(
                widgets_container,
                label_title_text=text_label.capitalize(),
                label_value_text=text_value
            )
            label.set_columns_layout(120, 200, anchor="w")
            label.pack(
                expand=True, fill="y",
                padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y
            )

    def toplevel_on_close(self, toplevel: ctk.CTkToplevel, line: Wine) -> None:
        """
        Handle detail window close event.
        
        Updates tracking dictionary and destroys window.
        
        Parameters:
            toplevel: Window to close
            line: Wine instance associated with the window
        """
        self.opened_toplevels[line] = False
        toplevel.destroy()

    def edit_wine(self, wine: Wine) -> None:
        """
        Open modal window to edit a wine.
        
        Parameters:
            wine: Wine instance to edit
        """
        # Create modal window
        edit_window = ToplevelCustomised(
            self, width=700, title="Edit Wine", modal=True
        )
        
        # Create edit form
        form = AddWineForm(
            edit_window.content_frame,
            self.session,
            fg_color="transparent",
            wine=wine,
            on_save=self.refresh_edited_rows,
        )
        form.pack(
            expand=True, fill="both",
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y
        )

        # Apply geometry and show
        edit_window.refresh_geometry()


    def delete_wine(self, wine: Wine) -> None:
        """
        Delete a wine after validation and user confirmation.
        
        Prevents deletion if wine has associated stock movements.
        
        Parameters:
            wine: Wine instance to delete
        """   
        # Confirm deletion
        confirm_dialog = messagebox.askyesno(
            "Confirm Removal",
            f"Do you want to remove the wine '{wine.name}'?"
        )

        if not confirm_dialog:
            return
        
        # Attempt deletion    
        try: 
            self.session.delete(wine)
            self.session.commit()
        except IntegrityError:
            # Rollback if wine has stock movements
            self.session.rollback() 

            mov_count = len(wine.movements) 
            verb, noun, pronoun = (
                ["is", "movement", "it"] 
                if mov_count == 1 else ["are", "movements", "them"]
            )
            error_message = (
                f"There {verb} {mov_count} stock {noun} related with this wine. "
                f"Please, remove {pronoun} before continuing."
            )
            messagebox.showinfo("Couldn't Remove The Wine ", error_message)

            return
        
        # Remove from data list
        self.lines.remove(wine)
        self.filtered_lines.remove(wine)
      
        # Remove from UI
        self.line_widget_map[wine].destroy()
        del self.line_widget_map[wine]

        # Update pagination button
        self.create_load_more_button()

        # Show success message
        messagebox.showinfo(
            "Wine Removed",
            "The wine has been successfully removed."
        )

    def refresh_edited_rows(self, wine: Wine) -> None:
        """
        Refresh table and related views after wine is edited.

        Clears the widget cache for the edited wine and updates all
        dependent UI components.
        
        Parameters:
            wine: Updated Wine instance
        """
        # Remove old widget from cache (address may have changed)
        if wine in self.line_widget_map:
            del self.line_widget_map[wine]
        
        # Refresh alert message in parent form
        if hasattr(self.master, 'update_alert_label'):
            self.master.update_alert_label()
        
        # Refresh visible rows
        self.refresh_visible_rows()

        # Refresh filter options in parent form
        if hasattr(self.master, 'filters_form'):
            self.master.filters_form.update_lists()
      
    def show_missing_images_warning(self, count: int) -> None:
        """
        Display warning dialog about wines with invalid image paths.
        
        Parameters:
            count: Number of wines with missing images
        """
        
        plural, verb = ["", "has"] if count < 2 else ["s", "have"]

        message = (
            f"{count} wine{plural} {verb} invalid image paths and couldn't be loaded.\n"
            f"Please edit the affected wine{plural} to correct or clear the image path."
        )
        messagebox.showwarning(f"Invalid Image Path{plural}", message)