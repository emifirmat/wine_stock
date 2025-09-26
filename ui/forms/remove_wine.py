"""
Form that contains the components and methods to remove a wine
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox

from ui.components import DropdownInput, DoubleLabel
from ui.style import Colours, Fonts
from db.models import Wine

class RemoveWineForm(ctk.CTkFrame):
    """
    Contains all the components and logic related to Remove Wine.
    """
    def __init__(self, root: ctk.CTkFrame, session, **kwargs):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            height=500
        )
        
        self.session = session
        self.wine_names_dict = self.get_wine_names_dict()
        self.wine_names_list = list(self.wine_names_dict.keys())
        self.wine_name_var = tk.StringVar(value=self.get_first_wine_name_var())

        self.wine_code_var = tk.StringVar()

        self.dropdown_wine = None
        self.button_delete = None
        self.create_components()
        self.on_entry_change()

        #self.on_save = on_save   IDK if i will use it (it comes from settings)

    def get_first_wine_name_var(self) -> str:
        """
        Get the first wine name vaer.

        Returns:
            A string that represents the first wine name var.
        """
        return self.wine_names_list[0] if self.wine_names_list else ""

    def create_components(self) -> list:
        """
        Create Inputs and buttons.

        Returns:
            A list containing all the created inputs the form.
        """
        self.grid_columnconfigure(0, weight=1)

        # Add inputs
        self.dropdown_wine = DropdownInput(
            self,
            label_text="Wine",
            values=self.wine_names_list,
            variable=self.wine_name_var,
            command=self.on_entry_change, # It doesn't need variable trace
        )
        
        label_code = DoubleLabel(
            self,
            label_title_text="Code",
            text_variable=self.wine_code_var
        )

        self.dropdown_wine.grid(row=0, column=0, pady=15)
        label_code.grid(row=1, column=0, pady=15)
        
        # Buttons
        button_state = "normal" if self.wine_names_list else "disabled"
        self.button_delete = ctk.CTkButton(
            self,
            text="Remove",
            fg_color=Colours.BTN_CLEAR,
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=10,
            cursor="hand2",
            state=button_state,
            command=self.remove_wine,
        )
        self.button_delete.grid(row=3, column=0, columnspan=2, pady=20)

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

    def on_entry_change(self, *args) -> None:
        """
        When a wine is selected, the code label is updated.

        Inputs:
            *args: Additional parameters that tk variables require in the background.
        """
        # Get variable
        selected_wine_name = self.wine_name_var.get()
        
        # Update wine_code var
        if selected_wine_name != "":
            wine_instance = self.wine_names_dict[selected_wine_name]
            self.wine_code_var.set(wine_instance.code) 
        else:
            self.wine_code_var.set("") 
     
    def remove_wine(self) -> None:
        """
        Save typed values into the db
        """
        # Get selected wine instance
        selected_wine_name = self.wine_name_var.get()
        wine = self.wine_names_dict[selected_wine_name]
        
        # Ask for confirmation
        movements_count = len(wine.movements)
        if movements_count > 0:
            confirm_dialog_message = (
                f"There are {movements_count} stock movements related with the wine "
                +f"{selected_wine_name}. Do you want to remove them all?"
            )
            show_info_message = "The wine and stock movements have been successfully removed."
        else:
            confirm_dialog_message = (
                f"Do you want to remove the wine {selected_wine_name}?"
            )
            show_info_message = "The wine has been successfully removed."

        confirm_dialog = messagebox.askyesno(
            "Confirm Removal",
            confirm_dialog_message
        )
        if not confirm_dialog:
            return

        # Remove it from the DB    
        self.session.delete(wine)
        self.session.commit()

        # Remove it from the Dropdown
        self.wine_names_list.remove(selected_wine_name)
        self.dropdown_wine.update_values(self.wine_names_list)
        new_selected_wine_name = self.wine_names_list[0] if self.wine_names_list else ""
        self.wine_name_var.set(new_selected_wine_name)
        self.on_entry_change()

        # Disable button if all records are deleted
        if len(self.wine_names_list) == 0:
            self.button_delete.configure(
                state="disabled"
            )

        # Show a message
        messagebox.showinfo(
            "Wine Removed",
            show_info_message
        )

