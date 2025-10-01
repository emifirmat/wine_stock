"""
Table that contains lines with name, quantity, price and subtotal of a transaction
included by the user adter clicking on add line.
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from decimal import Decimal

from db.models import Wine
from ui.style import Colours, Fonts
from ui.components import DoubleLabel

class AddLineTable(ctk.CTkFrame):
    """
    A frame that contains the components of a table including the row number,
    name, quantity, price, and subtotal of a transaction with a remove button.
    """
    def __init__(self, root: ctk.CTkFrame, session, headers: list[str], 
        on_lines_change=None, **kwargs):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(
            fg_color=Colours.BG_MAIN,
        )
        
        # Include db instances
        self.session = session

        # Table data
        self.headers = headers
        self.line_counter = 0
        self.line_list = [] # It contains dicts
        self.total_var = tk.StringVar(value=f"€ 0.00")

        # Callback
        self.on_lines_change = on_lines_change

        # Add components
        self.create_components()

    def create_components(self):
        """
        Create Inputs and buttons.
        """
        # Headers
        row_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_header_frame.pack(fill="x", pady=2)
        
        widths = [50, 200, 100, 100, 100, 30]
        for i, (header, width) in enumerate(zip(self.headers, widths)):
            label = ctk.CTkLabel(
                row_header_frame, 
                text=header.upper(),
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                width=width,
                wraplength=width
            )
            label.grid(row=0, column=i, padx=(0, 10))

        # Total amount
        total = DoubleLabel(
            self,
            label_title_text="Total",
            text_variable=self.total_var
        )
        total.bold_value_text()
        total.pack(side="bottom", anchor="se")

    def add_new_transaction_line(self, wine_instance: Wine, transaction_type: str, 
            quantity: int, subtotal: Decimal):
        """
        It creates a new line with the data of the name, quantity, price, and 
        subtotal of a transaction added by the user, including a remove button. 
        It also updates the value in label_total.
        Inputs:
            - wine_instance: Object of the wine selected by the user
            - transaction_type: Can be "sale" or "purchase"
            - quantity: Amount of bottes selected by the user.
            - subtotal: Result of doing quantity x price.
        """

        # Update line counter
        self.line_counter += 1

        # Add transaction in the list
        if transaction_type == "sale":
            price = wine_instance.selling_price
        elif transaction_type == "purchase": 
            price = wine_instance.purchase_price
        
        self.line_list.append({
            "wine": wine_instance,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": price
        })

        # Create line components
        frame_line = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        column_line_number = ctk.CTkLabel(
            frame_line,
            text=f"{self.line_counter}.",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_LABEL,
            width=50,
            wraplength=50
        )

        column_name = ctk.CTkLabel(
            frame_line,
            text=wine_instance.name,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_LABEL,
            width=200,
            wraplength=200
        )

        column_line_number.grid(row=0, column=0, padx=(0, 10))
        column_name.grid(row=0, column=1, padx=(0, 10))

        for i, column_text in enumerate([quantity, f"€ {price}", 
            f"€ {subtotal}"], start=2
        ):
            label_column = ctk.CTkLabel(
                frame_line,
                text=column_text,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
                wraplength=100
            
            )
            label_column.grid(row=0, column=i, padx=(0, 10))

        button_remove = ctk.CTkButton(
            frame_line,
            text="X",
            fg_color=Colours.BTN_CLEAR,
            text_color=Colours.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            width=30,
            cursor="hand2",
            command=lambda: self.remove_line(frame_line, subtotal)
        )

        button_remove.grid(row=0, column=6, sticky="e", padx=(0, 20))
        frame_line.pack(pady=(0, 10))

        # Update total value
        self.update_total_value(subtotal)
    
    def remove_line(self, parent_frame: ctk.CTkFrame, subtotal: Decimal):
        """
        Removes the line where the button that triggered the event was clicked.
        Inputs:
            - parent_frame: Frame that contains enum, name, quantity, price and 
            subtotal.
            - subtotal: Result of doing quantity x price.
        """
        wine_name = parent_frame.winfo_children()[1].cget("text").lower().strip() 
        quantity = parent_frame.winfo_children()[2].cget("text")
        
        line_table_index = parent_frame.winfo_children()[0].cget("text")
        line_table_index = int(line_table_index.replace(".","")) - 1
        current_index = line_table_index
        
        # Refresh total value
        self.update_total_value(subtotal, substract=True)

        # Update rest of the lines indices (first 2 indices are headers and total)
        # As children are 0-based, and enum 1based, I don't need to add + 1
        for line in self.winfo_children()[line_table_index + 2:]:
            label_line_number = line.winfo_children()[0]
            if isinstance(label_line_number, ctk.CTkLabel):
                label_line_number.configure(
                    text=f"{current_index}."
                )
                current_index += 1

        # Remove line
        parent_frame.destroy()
        del self.line_list[line_table_index]
        self.line_counter -= 1
        
        # Callback disable save button if there are no more lines and reduce 
        # temp stock 
        if self.on_lines_change:
            self.on_lines_change(len(self.line_list), wine_name, int(quantity))

    def update_total_value(self, subtotal: Decimal, substract: bool = False):
        """
        Updates the tk variable "total_var" which updates the value of the 
        "total" label.
        Inputs:
            - subtotal: Result of doing quantity x price.
            - substract: Bool that indicates if subtotal should sum or substract
        """
        # Update total value
        current_total = Decimal(self.total_var.get().replace("€ ", ""))
        
        if not substract:
            new_total = current_total + subtotal
        else:
            new_total = current_total - subtotal
        
        self.total_var.set(f"€ {new_total}")
    
    def get_line_list(self) -> list[dict]:
        """
        Returns the list of transactions (lines) added in the table
        """
        return self.line_list
    
