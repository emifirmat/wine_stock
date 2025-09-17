"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox

from ui.style import Colours, Fonts


class TransactionsTable(ctk.CTkFrame):
    """
    Contains the components of the table with the wine purchases and sellings.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, headers: list[str], lines, **kwargs
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
        self.header_labels = []
        self.lines = lines
        self.rows_lines_map = {}
        self.rows_info = {}
        self.row_header_frame = None
        self.rows_container = None
        
        # Sorting data
        self.sort_reverse = False

        # Add components
        self.create_components()

    def create_components(self):
        """
        Create headers and rows.
        """
        # ==Add Components==
        # headers
        row_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_header_frame.pack(fill="x", pady=2)

        for i, header in enumerate(self.headers):
            label = ctk.CTkLabel(
                row_header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=120,
                cursor="hand2"
            )
            label.grid(row=0, column=i, padx=5)

            # Bind
            label.bind(
                "<Button-1>", 
                lambda e, col_index=i: self.on_header_click(e, col_index)
            )

            self.header_labels.append(label)

        # Rows container
        self.rows_container = ctk.CTkFrame(self, fg_color="transparent")
        self.rows_container.pack(fill="both", expand=True)

        # Rows
        self.create_rows()

    def create_rows(self):
        """
        Create a row for each existing transaction
        """
        # Clean what was before
        for widget in self.rows_container.winfo_children():
            widget.destroy()
        
        # Movements
        for i, line in enumerate(self.lines): 
            row_frame = ctk.CTkFrame(self.rows_container, fg_color="transparent")
            row_frame.grid(row=i, pady=2)

            # Columns
            line_properties = [
                line.datetime.replace(microsecond=0), line.wine.name, line.wine.code,
                line.transaction_type.capitalize(), line.quantity, f"€ {line.price}",
                f"€ {line.quantity * line.price}"
            ]
            for j, line_property in enumerate(line_properties):
                label = ctk.CTkLabel(
                    row_frame, 
                    text=line_property,
                    text_color=Colours.TEXT_MAIN,
                    font=Fonts.TEXT_LABEL,
                    width=120,
                    wraplength=120,
                )
                
                label.grid(row=0, column=j, padx=5)
            
            # Remove Button
            remove_button = ctk.CTkButton(
                row_frame,
                text="X",
                fg_color=Colours.BTN_CLEAR,
                text_color=Colours.TEXT_BUTTON,
                hover_color=Colours.BG_HOVER_BTN_CLEAR,
                width=30,
                cursor="hand2",
                command=lambda f=row_frame, l=line: self.remove_line(f, l) # Pass f, l to get the current value and not last one.
            )
            remove_button.grid(row=0, column=len(line_properties), padx=5)

            # Save row info for future actions (sort, etc)
            self.rows_lines_map[line] = row_frame 
            self.rows_info[row_frame] = row_frame.grid_info()

    def remove_line(self, parent_frame, instance) -> None:
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
        # Remove line from list
        self.lines.remove(instance)

    def on_header_click(self, event, col_index: int):
        """
        After clicking a header, add an arrow on its name and sort it.
        """
        # Get ctkLabel of the clicked header
        event_label = event.widget.master

        # Prevents an error when user click on label but not on the text
        if not (0 <= event.x <= event_label.winfo_width() and 0 <= event.y <= event_label.winfo_height()):
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

    def sort_by(self, col_index):
        """
        Order rows based on the clicked header.
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
 
        # Sort
        self.lines.sort(key=sorting_keys[col_index], reverse=self.sort_reverse)
        
        # Toggle reverse mode
        self.sort_reverse = not self.sort_reverse
        
        # Refresh rows
        self.reorder_rows()

    def reorder_rows(self):
        """
        Modify the place of the rows without detroying the widgets.
        """
        for i, line in enumerate(self.lines):
            # Get widget
            row = self.rows_lines_map[line]
            grid_info = self.rows_info[row]
             
            # If widget is hidden, skip
            if not row.winfo_ismapped():
                continue

            # Update grid info
            grid_info["row"] = i

            # Replace widget
            row.grid_forget()
            row.grid(**grid_info)
            


    def update_by_filter(self, filtered_names):
        """
        Update the table by filters
        """
        # Iterate over rows
        for row in self.rows_container.winfo_children():
            # Get text in label wine name
            label_name = row.winfo_children()[1].cget("text")
            
            # If the wine name matches the filter, show it in the table
            if label_name in filtered_names:
                row_grid_info = self.rows_info[row]
                row.grid(**row_grid_info)
            else:
                # If not matched, hide it
                row.grid_forget()