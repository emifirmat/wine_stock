"""
Table that contains the movements of the stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox

from ui.style import Colours, Fonts


class MovementsTable(ctk.CTkFrame):
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
        self.row_header_frame = None
        self.rows_container = None
        
        # Sorting data
        self.sort_reverse = False

        # Add components
        self.create_components()

    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        # ==Add Components==
        # headers
        row_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_header_frame.pack(fill="x", pady=2)

        widths = [100, 200, 100, 120, 80, 80, 100]
        for i, (header, width) in enumerate(zip(self.headers, widths)):
            label = ctk.CTkLabel(
                row_header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=width,
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
        for line in self.lines: 
            row_frame = ctk.CTkFrame(self.rows_container, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            # Columns
            label_datetime = ctk.CTkLabel(
                row_frame, 
                text=line.datetime.replace(microsecond=0),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
                wraplength=100,
            )
            label_wine_name = ctk.CTkLabel(
                row_frame, 
                text=line.wine.name,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=200,
                wraplength=200,
            )
            label_wine_code = ctk.CTkLabel(
                row_frame, 
                text=line.wine.code,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
            )
            label_transaction = ctk.CTkLabel(
                row_frame, 
                text=line.transaction_type.capitalize(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=120,
            )
            label_quantity = ctk.CTkLabel(
                row_frame, 
                text=line.quantity,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=80,
            )
            label_price = ctk.CTkLabel(
                row_frame, 
                text=f"€ {line.price}",
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=80,
            )
            label_subtotal = ctk.CTkLabel(
                row_frame, 
                text=f"€ {line.quantity * line.price}",
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
            )

            label_datetime.grid(row=0, column=0, padx=5)
            label_wine_name.grid(row=0, column=1, padx=5)
            label_wine_code.grid(row=0, column=2, padx=5)
            label_transaction.grid(row=0, column=3, padx=5)
            label_quantity.grid(row=0, column=4, padx=5)
            label_price.grid(row=0, column=5, padx=5)
            label_subtotal.grid(row=0, column=6, padx=5)
            
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
            remove_button.grid(row=0, column=7, padx=5)

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
        self.create_rows()
