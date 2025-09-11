"""
Table that contains the list of added wines with their stock
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox

from ui.style import Colours, Fonts
from helpers import load_ctk_image


class WinesTable(ctk.CTkFrame):
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
        self.headers = headers # code, picture, name, vintage_year, origin, quantity, purchase_price, selling price
        self.header_labels = []
        self.lines = lines
        self.row_header_frame = None
        self.rows_container = None
        
        # Sorting data
        self.sort_reverse = False

        # Add components
        self.create_components()

    def create_components(self) :
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
                wraplength=120,
                cursor="hand2" if header != "picture" else "arrow"
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
        Create a row for each existing wine
        """
        # Clean what was there before
        for widget in self.rows_container.winfo_children():
            widget.destroy()
        
        # Movements
        for line in self.lines: 
            row_frame = ctk.CTkFrame(self.rows_container, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            # Peepare image path
            if line.wine_picture_path:
                image_path = line.wine_picture_path  
            else: 
                image_path = "assets/user_images/wines/default_wine.png"

            # Columns
            wine_properties = [
                line.code, image_path, line.name, line.vintage_year, line.origin, 
                line.quantity, f"€ {line.purchase_price}", f"€ {line.selling_price}"
            ]
            for i, wine_property in enumerate(wine_properties):
                # Text labels
                if wine_property != image_path: 
                    label = ctk.CTkLabel(
                        row_frame, 
                        text=wine_property,
                        text_color=Colours.TEXT_MAIN,
                        font=Fonts.TEXT_LABEL,
                        width=120,
                        wraplength=120,
                    )
                # Image label
                else:
                    label = ctk.CTkLabel(
                        row_frame, 
                        image=load_ctk_image(image_path),
                        text="",
                        width=120,
                        wraplength=120,
                    )
    
                label.grid(row=0, column=i, padx=5)            

    def on_header_click(self, event, col_index: int):
        """
        After clicking a header, add an arrow on its name and sort it.
        """
        # Get ctkLabel of the clicked header
        event_label = event.widget.master

        # Prevents an error when user click on label but not on the text
        if not (0 <= event.x <= event_label.winfo_width() and 0 <= event.y <= event_label.winfo_height()):
            return
        
        # Ignore picture header
        clean_text = event_label.cget("text").replace("↑", "").replace("↓", "")
        if clean_text == "PICTURE":
            return

        # Clean arrow in all labels
        for lbl in self.header_labels:
            lbl_text = lbl.cget("text").replace("↑", "").replace("↓", "")
            lbl.configure(text=lbl_text)

        # Add arrow depending on order
        arrow = "↓" if self.sort_reverse else "↑"
        event_label.configure(text=clean_text + arrow)

        # Sort rows
        self.sort_by(col_index)

    def sort_by(self, col_index):
        """
        Order rows based on the clicked header.
        """
        sorting_keys = {
            0: lambda l: l.code.upper(),
            1: None,
            2: lambda l: l.name.lower(),
            3: lambda l: l.vintage_year,
            4: lambda l: l.origin.lower(),
            5: lambda l: l.quantity,
            6: lambda l: l.purchase_price,
            7: lambda l: l.selling_price
        }
 
        # Sort
        self.lines.sort(key=sorting_keys[col_index], reverse=self.sort_reverse)
        
        # Toggle reverse mode
        self.sort_reverse = not self.sort_reverse
        
        # Refresh rows
        self.create_rows()
