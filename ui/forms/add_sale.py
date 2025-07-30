"""
Form that contain the inputs and methods to add a new sale
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from datetime import datetime
from decimal import Decimal
from PIL import Image

from ui.components import (TextInput, IntInput, Card, DropdownInput, ImageInput,
    DoubleLabel)
from ui.style import Colours, Fonts, Icons
from helpers import generate_favicon, load_image_from_file, load_ctk_image
from models import Shop, Wine, Colour, Style, StockMovement

class AddSaleForm(ctk.CTkScrollableFrame):
    """
    Contains all the components and logic related to ADD a Sale.
    """
    def __init__(
            self, root: ctk.CTkFrame, session, **kwargs
        ):
        # Set up form frame
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            scrollbar_button_color=Colours.BG_HOVER_NAV,
            height=500
        )
        
        # Include db instances
        self.session = session
        self.wine_names_dict = self.get_wine_names_dict()
        self.wine_names_list = list(self.wine_names_dict.keys())
        
        # TK variables
        self.wine_name_var = tk.StringVar(value=self.wine_names_list[0])
        self.quantity_var = tk.IntVar(value=1)
        self.total_var = tk.StringVar(value=f"€ 0.00")
        # Listen to any change on their values
        self.quantity_var.trace_add("write", self.on_entry_change)

        self.subtotal_value = None
        self.line_counter = 0
        self.line_list = [] # It contains dicts

        # Add components
        self.dropdown_wine = None
        self.textbox_quantity = None
        self.label_subtotal = None
        self.frame_lines = None
        self.button_clear = None
        self.button_save = None
        self.inputs_dict = self.create_components()
        self.on_entry_change() # Initial subtotal label update

    def get_wine_names_dict(self) -> dict[str:int]:
        """
        Get a list of wine names with their instances.
        Returns:
            A dict of wine names with their instance as value.
        """
        wines = Wine.all_ordered(self.session)
        return {
            f"{wine.name.title()}": wine for wine in wines
        }

    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==Add Components==
        # =Inputs section=
        self.dropdown_wine = DropdownInput(
            self,
            label_text="Wine",
            values=self.wine_names_list,
            variable=self.wine_name_var,
            command=self.on_entry_change, # It doesn't need variable trace
        )
        
        self.textbox_quantity = IntInput(
            self,
            label_text="Quantity (Bottles)",
            from_=0,
            textvariable=self.quantity_var
        )
        self.label_subtotal = DoubleLabel(
            self,
            label_title_text="Subtotal",
            label_value_text=None
        )
        
        button_add_line = ctk.CTkButton(
            self,
            text="Add Line",
            fg_color="#88B04B",
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            corner_radius=10,
            cursor="hand2",
            command=self.add_new_wine_line 
        )
        # Save inputs for later
        inputs_dict = {
            "wine": self.dropdown_wine, 
            "quantity": self.textbox_quantity, 
        }

        self.dropdown_wine.grid(row=0, column=0, pady=20, sticky="w", columnspan=2)
        self.textbox_quantity.grid(row=1, column=0, sticky="w")
        self.label_subtotal.grid(row=1, column=1, sticky="w")
        button_add_line.grid(row=2, column=0, columnspan=2, pady=20)

        # =Lines section=
        self.frame_lines = ctk.CTkFrame(
            self,
            fg_color=Colours.BG_MAIN
        )
        
        frame_headers = ctk.CTkFrame(
            self.frame_lines,
            fg_color="transparent"
        )

        header_invisible = ctk.CTkLabel(
            frame_headers,
            text=" ",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_HEADER,
            #anchor="w",
            width=30,
            
        )
        header_invisible.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        header_name = ctk.CTkLabel(
            frame_headers,
            text="Name",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_HEADER,
            #anchor="w",
            width=300,
            
        )
        header_name.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        for i, header in enumerate(["Quantity", "Price", "Subtotal"], start=2):
            label_header = ctk.CTkLabel(
                frame_headers,
                text=header,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_HEADER,
                #anchor="w",
                width=100,
                
            )

            label_header.grid(row=0, column=i, padx=(0, 20))
        
        header_invisible = ctk.CTkLabel(
            frame_headers,
            text=" ",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_HEADER,
            #anchor="w",
            width=30,
        )
        header_invisible.grid(row=0, column=6, sticky="w", padx=(0, 20))

        frame_headers.pack(pady=(10))

        total = DoubleLabel(
            self.frame_lines,
            label_title_text="Total",
            text_variable=self.total_var
        )
        total.label_value.configure(font=Fonts.TEXT_HEADER)
        total.pack(side="bottom", anchor="se")

        self.frame_lines.grid(row=3, column=0, columnspan=2)

        # =Buttons=
        frame_buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        button_clear = ctk.CTkButton(
            frame_buttons,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=10,
            cursor="hand2",
            command=self.clear_inputs,
        )
        self.button_save = ctk.CTkButton(
            frame_buttons,
            text="Save",
            fg_color=Colours.BTN_SAVE,
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            corner_radius=10,
            state="disabled",
            command=self.save_values, 
        )
        frame_buttons.grid(row=4, column=0, pady=20, columnspan=2)
        button_clear.grid(row=0, column=0)
        self.button_save.grid(row=0, column=1, padx=20)

        return inputs_dict

    def clear_inputs(self) -> None:
        """
        Clear the text typed or selected image by the user on the inputs.
        It doesn't clear dropdowns
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Clearing the form will discard all current inputs and added lines. Continue?"
        )
        if not confirm_dialog:
            return
        
        for input in self.inputs_dict.values():         
            # Still dropdown doesn't have an empty value, so it makes no sense to
            # Change its value to the first item.
            if type(input) is not DropdownInput:
                input.clear()

        # Remove all lines
        self.remove_all_lines()

    def remove_all_lines(self):
        """
        Remove all lines added by the user.
        """
        # Remove all lines
        for line in self.frame_lines.winfo_children()[2:]:
            # Access to line_number button to remove all lines
            label_line_button = line.winfo_children()[-1]
            if isinstance(label_line_button, ctk.CTkButton):
                # Click button
                label_line_button.invoke()

        # Disable save button
        self.button_save.configure(state="disabled", cursor="arrow")

    def save_values(self) -> None:
        """
        Save added lines into the db
        """
        confirm_dialog = messagebox.askyesno(
            "Confirm",
            "Do you want to save this sale?"
        )
        if not confirm_dialog:
            return

        # Iterate over each line
        for line in self.line_list:
            movement = StockMovement(
                wine=line["wine"],
                transaction_type=line["transaction_type"],
                quantity=line["quantity"],
                price=line["price"]
            )
            # Save it in the DB    
            self.session.add(movement)
        
        self.session.commit()

        # Show a message
        messagebox.showinfo(
            "Lines Saved",
            "All added lines from the wine sale have been successfully saved."
        )

        # Clear all lines
        self.remove_all_lines()

    def on_entry_change(self, *args) -> None:
        """
        When a wine is selected or the quantity is changed, variables are updated
        """
        # Get variables
        selected_wine_name = self.wine_name_var.get()
        quantity = self.get_quantity_var()
        
        # Get wine price
        wine_instance = self.wine_names_dict[selected_wine_name]
        selling_price = wine_instance.selling_price
        
        # Get subtotal
        self.subtotal_value = quantity * selling_price
        
        # Update subtotal label
        self.label_subtotal.update_value_text(f"€ {self.subtotal_value}")

    def get_quantity_var(self) -> int:
        """
        Returns the quantity typed by the user or 0 if it is empty.
        """
        try:
            return self.quantity_var.get()
        except:
            # Catch empty entry and update process
            return 0 

    def add_new_wine_line(self):
        """
        It creates a new line in frame_lines, with the data of the inputs and a 
        remove button. It also updates the value in label_total.
        """
        # Has to Save the lien and clear input fields  
        
        # # Get variables
        selected_wine_name = self.wine_name_var.get()
        quantity = self.get_quantity_var()
        
        # Get wine price
        wine_instance = self.wine_names_dict[selected_wine_name]
        selling_price = wine_instance.selling_price

        # Update line counter
        self.line_counter += 1

        # Create line components
        frame_line = ctk.CTkFrame(
            self.frame_lines,
            fg_color="transparent"
        )

        column_line_number = ctk.CTkLabel(
            frame_line,
            text=f"{self.line_counter}.",
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_LABEL,
            width=50,
            
        )

        column_name = ctk.CTkLabel(
            frame_line,
            text=selected_wine_name,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_LABEL,
            width=300,
        )

        self.line_list.append({
            "wine": self.wine_names_dict[selected_wine_name],
            "transaction_type": "sale",
            "quantity": quantity,
            "price": selling_price
        })

        column_line_number.grid(row=0, column=0, padx=(0, 20))
        column_name.grid(row=0, column=1, padx=(0, 20))

        for i, column_text in enumerate([quantity, f"€ {selling_price}", 
            f"€ {self.subtotal_value}"], start=2
        ):
            label_column = ctk.CTkLabel(
                frame_line,
                text=column_text,
                text_color=Colours.TEXT_MAIN,
                font=Fonts.TEXT_LABEL,
                width=100,
            
            )
            label_column.grid(row=0, column=i, padx=(0, 20))

        subtotal_value_copy = self.subtotal_value
        button_remove = ctk.CTkButton(
            frame_line,
            text="X",
            fg_color=Colours.BTN_CLEAR,
            text_color=Colours.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            width=30,
            cursor="hand2",
            command=lambda: self.remove_line(
                frame_line, 
                subtotal_value_copy, 
            )
        )

        button_remove.grid(row=0, column=6, sticky="e", padx=(0, 20))
        frame_line.pack(pady=(0, 10))

        # Update total value
        self.update_total_value()
        # Enable save button
        if self.button_save.cget("state") == "disabled":
            self.button_save.configure(state="normal", cursor="hand2")

    def update_total_value(self, substract_value: Decimal | None = None):
        """
        Update the total var to keep consistency with operations.
        """
        # Update total value
        current_total = Decimal(self.total_var.get().replace("€ ", ""))
        
        if not substract_value:
            new_total = current_total + self.subtotal_value
        else:
            new_total = current_total - substract_value
        
        self.total_var.set(f"€ {new_total}")


    def remove_line(self, parent_frame, subtotal) -> None:
        """
        Removes the line where the button that triggered the event was clicked
        """
        # Update line counter
        self.line_counter -= 1
        
        # Refresh total value
        self.update_total_value(subtotal)
        
        # Remove line
        line_index = parent_frame.winfo_children()[0].cget("text")
        line_index = int(line_index.replace(".","")) - 1
        parent_frame.destroy()

        # Refresh counter on following lines
        current = 1
        
        # Get lines (Skipped [0]=headers and [1]=total)
        line_list = self.frame_lines.winfo_children()[2:]
        for child in line_list:
            # Access to line_number label and update text
            label_line_number = child.winfo_children()[0]
            if isinstance(label_line_number, ctk.CTkLabel):
                label_line_number.configure(
                    text=f"{current}."
                )
                current += 1

        # Remove line from list of dicts
        del self.line_list[line_index]
            
        # Disable save button is there are no more lines
        if self.line_counter == 0:
            self.button_save.configure(state="disabled", cursor="arrow")

