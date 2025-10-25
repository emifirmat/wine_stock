"""
Table that contains the list of added wines with their stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from sqlalchemy.exc import IntegrityError
from typing import Callable, Dict, List

from db.models import Wine
from helpers import load_ctk_image, get_coords_center
from ui.components import DoubleLabel, FixedSizeToplevel, ActionMenuButton
from ui.forms.add_edit_wine import AddWineForm
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
        self.column_widths = [100, 120, 100, 90, 95, 95, 90, 90, 90, 80]
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
            line.origin_display, str(line.quantity), line.min_stock_display,
            f"€ {line.purchase_price}", f"€ {line.selling_price}"
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
            6: lambda l: l.min_stock_sort,
            7: lambda l: l.purchase_price,
            8: lambda l: l.selling_price,
            9: None
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

    def customize_row(self, line: Wine, frame_row: ctk.CTkFrame):
        """
        Creates additional components for the row line called by refresh visible rows.
        Parameters:
            line: Instance of the Wine class 
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
            btn_name="Wine",
            on_show=lambda w=line: self.show_details(w),
            on_edit=lambda w=line: self.edit_wine(w),
            on_delete=lambda w=line: self.delete_wine(w),
        ).grid(row=0, column=0, padx=5)

        frame_row.grid_columnconfigure(column_index, weight=1)

    def show_details(self, line: Wine):
        """
        Creates a toplevel that shows the details of the click wine.
        """
        # Check the clicked wine is not opened
        if line in self.opened_toplevels and self.opened_toplevels[line]:
            return

        # Create top level
        tl_width = 350
        tl_height = 550
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
            "origin", "stock", "min. stock", "purchase price", "selling price"
        ]

        text_values = [
            line.name, line.code, line.winery, line.colour.name.title(), 
            line.style.name.title(), line.varietal_display.title(), line.vintage_year, 
            line.origin_display, str(line.quantity), line.min_stock_display,
            f"€ {line.purchase_price}", f"€ {line.selling_price}"
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

    def edit_wine(self, wine):
        """
        Open a new modal window to edit an existing wine.
        Parameters:
            - wine: Wine instance of the clicked row.
        """
        # Create a modal top level
        edit_window = ctk.CTkToplevel(
            self.winfo_toplevel(),
            fg_color=Colours.BG_MAIN,
        )
        edit_window.title("Edit Wine")
        
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
            text="Edit Wine",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )

        # Place title       
        title.grid(row=0, column=0, pady=(20, 0), sticky="n")

        # Add form
        form = AddWineForm(
            frame_scroll,
            self.session,
            fg_color="transparent",
            wine=wine,
            on_save=self.refresh_edited_rows,
        )
        form.grid(row=1, column=0, pady=(10, 0), sticky="nsew")

        # Make everything responsive
        frame_scroll.grid_columnconfigure(0, weight=1)

    def delete_wine(self, wine):
        """
        Removes the wine from the DB and table.
        """   
        # Ask for confirmation
        confirm_dialog = messagebox.askyesno(
            "Confirm Removal",
            f"Do you want to remove the wine '{wine.name}'?"
        )

        if not confirm_dialog:
            return
        
        # Remove it from the DB    
        try: 
            self.session.delete(wine)
            self.session.commit()
        except IntegrityError:
            # Don't delete if there are transactions involved
            self.session.rollback() 
            mov_count = len(wine.movements) 
            words = ["is", "movement"] if mov_count == 1 else ["are", "movements"]
            error_message = (
                f"There {words[0]} {mov_count} stock {words[1]} related with this wine. "
                "Please, remove them before continuing."
            )
            messagebox.showinfo(
                "Couln't Remove The Wine ",
                error_message
            )
            # End function
            return
        
        # Remove it from the lists (data)
        self.lines.remove(wine)
        self.filtered_lines.remove(wine)
      
        # Remove it from the UI table
        self.line_widget_map[wine].destroy()
        del self.line_widget_map[wine]

        # Update load more button
        self.create_load_more_button()

        # Show a message
        messagebox.showinfo(
            "Wine Removed",
            "The wine has been successfully removed."
        )

    def refresh_edited_rows(self, wine):
        """
        After a wine is edited, it refreshes the table.
        """
        # Delete old wine address from wine_widget_map
        del self.line_widget_map[wine]
        # Refresh alert message
        self.master.update_alert_label()
        # Refresh list
        self.refresh_visible_rows()
        # Refresh lists in filters form
        self.master.filters_form.update_lists()
        