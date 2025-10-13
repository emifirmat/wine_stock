"""
Custom components useful for the app
"""
import calendar
import customtkinter as ctk
import datetime
import tkinter as tk
import re
from decimal import Decimal
from typing import Callable

from helpers import load_ctk_image, resource_path, generate_colored_icon
from db.models import Wine
from ui.style import Colours, Fonts, Icons


class EntryInputMixin:
    """
    Mixin that provides utility methods for handling entry widgets.
    """
    def set_entry_width(self, entry_width: int) -> None:
        """
        Sets the width of the entry widget.
        Parameters:
            - entry_width: The width to apply to the entry widget.
        """
        self.entry.configure(
            width=entry_width
        )
    
    def clear(self) -> None:
        """
        Removes the current text from the entry widget.
        """
        self.entry.delete(0, "end") 

    def get(self) -> str:
        """
        Returns the current value of the entry widget.
        Returns:
            str: The text currently contained in the entry
        """
        return self.entry.get()

    def set_input_width(self, input_width: int) -> None:
        """
        Sets the total width of the input for alignment purposes.
        Creates an empty label to fill the remaining width.
        Parameters:
            - input_width: Total width of the input container.
        Raises:
            ValueError: If the total width is smaller than the sum of its components.
        Requirements:
            - The class must inherit from CTkFrame.
            - The class must define `self.label`, `self.label_optional`, and 
            `self.entry`.
            
        """
        # Ensure widgets are rendered before measuring
        self.update_idletasks()
        
        # Calculate widths
        label_width = self.label.winfo_width()
        label_asterisk_width = self.label_optional.winfo_width()
        entry_width = self.entry.winfo_width()
        empty_label_width = input_width - (label_width + entry_width + label_asterisk_width)

        if empty_label_width < 0:
            raise ValueError("input_width must be greater than label_width + entry_width")

        # Create empty label for aligment
        empty_label = ctk.CTkLabel(
            self, # frame that contains all ctk components
            text="",
            width=empty_label_width
        )
        empty_label.grid(row=0, column=3)


class FixedSizeToplevel(ctk.CTkToplevel):
    """
    A toplevel window that retains its original width and height even if resized
    by the user.
    """
    def __init__(self, root, width: int, height: int, **kwargs):
        super().__init__(root, **kwargs)
        self.original_width = width
        self.original_height = height
        self.geometry(f"{width}x{height}")

        self.resizable(False, False)
        self.bind("<Configure>", self.on_configure)

    def on_configure(self, event: tk.Event) -> None:
        """
        Restores the window size if it was changed by the user.
        Parameters:
            - event: The configure event triggered by resizing.
        """
        if event.width != self.original_width or event.height != self.original_height:
            self.after(
                10, 
                lambda: self.geometry(
                    f"{self.original_width}x{self.original_height}+{self.winfo_x()}+{self.winfo_y()}"
                )
            )

class TextEntry(ctk.CTkEntry):
    """
    An entry widget with a maximum length validation.
    """
    def __init__(self, root, placeholder:str, max_len: int = 60, **kwargs):
        super().__init__(
            root, 
            placeholder_text=placeholder, 
            placeholder_text_color=Colours.TEXT_SECONDARY,
            **kwargs)

        self.max_len = max_len

        # Register a tkinter function, to validate field
        validate_cmd = self.register(self._validate_len) 

        self.configure(
            validate="key", # Every time user types, it will validate
            # Pass tk function and input contet as argument to valdiate_integer.
            # %P is from Tkinter and means "new content after typing"
            validatecommand=(validate_cmd, "%P") ,      
        )

    def _validate_len(self, text: str) -> bool:
        """
        Validates that the input text does not exceed the maximum allowed length.

        Parameters:
            - text: The current text in the entry.

        Returns:
            - bool: True if valid, False otherwise.
        """
        return len(text) <= self.max_len


class IntEntry(ctk.CTkEntry):
    """
    An entry widget that only accepts integer values.
    """
    def __init__(self, root, placeholder: str, from_: int | None = None, 
        to: int | None = None, textvariable: tk.StringVar | None = None, **kwargs
    ):
        super().__init__(root, 
            placeholder_text=placeholder, 
            placeholder_text_color=Colours.TEXT_SECONDARY,
            **kwargs
        )
        self.min_val = from_
        self.max_val = to
        # Register a tkinter function, to validate field
        validate_cmd = self.register(self._validate_value) 

        self.configure(
            validate="key", # Every time user types, it will validate
            # Pass tk function and input contet as argument to valdiate_integer.
            # %P is from Tkinter and means "new content after typing"
            validatecommand=(validate_cmd, "%P") ,
            textvariable=textvariable
        )       

    def _validate_value(self, text: str) -> bool:
        """
        Validates that the input is an integer within the allowed range.

        Parameters:
            - text: Text typed by the user
        Returns:
            - bool: True if valid, False otherwise.
            
        """
        if text == "":
            return True
        if text.isdigit():
            number = int(text)
            # Number is lower than min
            if self.min_val and number < self.min_val:
                return False
            # Number is higher than max
            if self.max_val and number > self.max_val:
                return False
            # Number is in range
            return True
        # Number is not an integer
        return False
    
class DecimalEntry(ctk.CTkEntry):
    """
    An entry widget that accepts decimal values within a specified range.
    """
    def __init__(self, root, placeholder: str, from_: int | None = None, 
        to: int | None = None, textvariable: tk.StringVar | None = None, **kwargs
    ):
        super().__init__(
            root, 
            placeholder_text=placeholder, 
            placeholder_text_color=Colours.TEXT_SECONDARY,
            **kwargs
        )
        self.min_val = from_
        self.max_val = to
        # Register a tkinter function, to validate field
        validate_cmd = self.register(self._validate_value) 

        self.configure( 
            validate="key", # Every time user types, it will validate
            # Pass tk function and input contet as argument to valdiate_integer.
            # %P is from Tkinter and means "new content after typing"
            validatecommand=(validate_cmd, "%P") ,
            textvariable=textvariable
        )       

    def _validate_value(self, text: str) -> bool:
        """
        Validates that the input is a decimal number within the allowed range.

        Parameters:
            - text: The text entered by the user.
        Returns:
            - bool: True if valid, False otherwise.
        """
        
        if text == "" :
            return True

        # Accept only numbers and dor ("123", "0.5", ".5", "5.")
        if not re.fullmatch(r"\d*\.?\d*", text):
            return False
        
        # Accept edge cases of dot
        if text.endswith('.'):
            return True
     
        # Catch other weird symbols
        try:   
            number = Decimal(text)
        except (ValueError, TypeError):
            return False
        
        # Number is lower than min
        if self.min_val and number < self.min_val:
            return False
        # Number is higher than max
        if self.max_val and number > self.max_val:
            return False
        # Number is in range
        return True


class DateEntry(ctk.CTkEntry):
    """
    An entry widget that allows users to select a date from a pop-up calendar.
    """
    def __init__(self, root, textvariable: str | None = None, **kwargs):
        self.text_var = textvariable or tk.StringVar()
        
        super().__init__(root, textvariable=textvariable, **kwargs)     

        self.year = None
        self.month = None
        self.frame_calendar = None

        # Show calendar on click
        self.bind("<Button-1>", self.open_calendar)

    def open_calendar(self, event: tk.Event | None = None) -> None:
        """
        Opens a calendar pop-up for selecting a date.
        Parameters:
            - event: The triggering event.
        """
        # Get current date details
        today = datetime.date.today()
        self.year = today.year
        self.month = today.month
        
        # Destroy any previous calendar (important)
        self.close_calendar()

        # Create a calendar frame
        self.frame_calendar = ctk.CTkFrame(
            self.winfo_toplevel(),
            fg_color=Colours.BG_MAIN,
            border_width=2,
            border_color=Colours.BORDERS,
        )
        
        # Locate calendar
        x = self.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
        y = self.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + self.winfo_height() + 5
        self.frame_calendar.place(x=x, y=y)
        self.frame_calendar.lift()
       
        # Build calendar
        self.build_calendar()
    
    def build_calendar(self) -> None:
        """
        Builds the structure of the calendar, including navigation and day buttons.
        """
        for widget in self.frame_calendar.winfo_children():
            widget.destroy()

        calendar_ = calendar.monthcalendar(self.year, self.month)

        # Header (middle position)
        header = ctk.CTkLabel(
            self.frame_calendar, 
            text=f"{calendar.month_name[self.month]} {self.year}",
            font=Fonts.TEXT_HEADER_CALENDAR
        )
        header.grid(row=0, column=2, columnspan=3, pady=5)

        # Navigation buttons (besides header)
        year_prev_btn = ctk.CTkButton(
            self.frame_calendar, 
            text="<<", 
            width=30, 
            fg_color=Colours.BG_HOVER_NAV,
            text_color=Colours.TEXT_MAIN,
            hover_color=Colours.DROPDOWN_HOVER,
            command=self.prev_year
        )
        month_prev_btn = ctk.CTkButton(
            self.frame_calendar, 
            text="<", 
            width=30, 
            fg_color=Colours.BG_HOVER_NAV,
            text_color=Colours.TEXT_MAIN,
            hover_color=Colours.DROPDOWN_HOVER,
            command=self.prev_month
        )         
        month_next_btn = ctk.CTkButton(
            self.frame_calendar, 
            text=">", 
            width=30, 
            fg_color=Colours.BG_HOVER_NAV,
            text_color=Colours.TEXT_MAIN,
            hover_color=Colours.DROPDOWN_HOVER,
            command=self.next_month
        )
        year_next_btn = ctk.CTkButton(
            self.frame_calendar, 
            text=">>", 
            width=30, 
            fg_color=Colours.BG_HOVER_NAV,
            text_color=Colours.TEXT_MAIN,
            hover_color=Colours.DROPDOWN_HOVER,
            command=self.next_year
        )
        year_prev_btn.grid(row=0, column=0, padx=(5, 0))
        month_prev_btn.grid(row=0, column=1)
        month_next_btn.grid(row=0, column=5)
        year_next_btn.grid(row=0, column=6, padx=(0, 5))

        # Days
        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            label = ctk.CTkLabel(self.frame_calendar, text=day)
            label.grid(row=1, column=i, padx=2, pady=2)

        # Days of the month (start from 2 because 1 is days)
        for r, week in enumerate(calendar_, start=2):
            for c, day in enumerate(week):
                if day != 0:
                    button = ctk.CTkButton(
                        self.frame_calendar, 
                        text=str(day), 
                        width=40, 
                        height=25,
                        fg_color=Colours.BG_SECONDARY,
                        text_color=Colours.TEXT_SECONDARY,
                        hover_color=Colours.BG_HOVER_NAV,
                        command=lambda d=day: self.select_date(d)
                    )
                    # Set pads for borders
                    if c == 0:
                        padx = (3, 1)
                    elif c == len(week) - 1:
                        padx = (1, 3)
                    else:
                        padx = 1
                    pady = 1 if r != len(calendar_) + 1 else (1, 3)
                    button.grid(row=r, column=c, padx=padx, pady=pady)

    def prev_month(self) -> None:
        """
        Displays the previous month in the calendar.
        """
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.build_calendar()

    def next_month(self) -> None:
        """
        Displays the next month in the calendar.
        """
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.build_calendar()

    def prev_year(self) -> None:
        """
        Displays the previous year in the calendar.
        """
        self.year -= 1
        self.build_calendar()

    def next_year(self):
        """
        Displays the next year in the calendar.
        """
        self.year += 1
        self.build_calendar()

    def select_date(self, day: int) -> None:
        """
        Handles date selection from the calendar.
        Parameters:
            - day: The day selected by the user.
        """
        # Get date and show it on the input
        selected = datetime.date(self.year, self.month, day)
        self.text_var.set(selected.strftime("%d/%m/%Y"))
        # Destroy calendar
        self.close_calendar()

    def close_calendar(self) -> None:
        """Closes the calendar pop-up if it exists."""
        if self.frame_calendar:
            self.frame_calendar.destroy()
            self.frame_calendar = None
    
    def destroy(self) -> None:
        """
        Destroys the entry and any associated calendar pop-up.
        """
        self.close_calendar()
        super().destroy()

class AutocompleteEntry(ctk.CTkEntry):
    """
    An entry widget that provides autocomplete suggestions from a wine list.
    """
    def __init__(self, root, placeholder: str, item_list: list[str], **kwargs):
        super().__init__(
            root, 
            placeholder_text=placeholder, 
            placeholder_text_color=Colours.TEXT_SECONDARY,
            **kwargs
        )
        self.root = root
        self.wine_list = item_list
        self.listbox = None
        self.listbox_frame = None
        self.main_window = self.winfo_toplevel()
        
        self.bind("<KeyRelease>", self.show_suggestions)
        self.bind("<Button-1>", self.show_suggestions)

    def on_click_outside(self, event: tk.Event) -> None:
        """
        Closes the suggestion list when clicking outside the entry or listbox.
        Parameters:
            - event: The triggering event.
        """
        if self.listbox_frame:
            # Get click's coordinates
            x = event.x_root
            y = event.y_root
            
            # Check if the click was in the entry
            entry_x = self.winfo_rootx()
            entry_y = self.winfo_rooty()
            entry_width = self.winfo_width()
            entry_height = self.winfo_height()
            
            in_entry = (entry_x <= x <= entry_x + entry_width and 
                       entry_y <= y <= entry_y + entry_height)
            
            # Check if the click was in the listbox
            if self.listbox_frame and self.listbox_frame.winfo_exists():
                listbox_x = self.listbox_frame.winfo_rootx()
                listbox_y = self.listbox_frame.winfo_rooty()
                listbox_width = self.listbox_frame.winfo_width()
                listbox_height = self.listbox_frame.winfo_height()
                
                in_listbox = (listbox_x <= x <= listbox_x + listbox_width and 
                            listbox_y <= y <= listbox_y + listbox_height)
            else:
                in_listbox = False
            
            # Destroy listbox if not in entry or listbox
            if not in_entry and not in_listbox:
                self.destroy_listbox()

    def show_suggestions(self, event: tk.Event | None = None) -> None:
        """
        Displays autocomplete suggestions based on user input.

        Parameters:
            - event: The triggering event.
        """
        typed = self.get().lower()

        # Clean previous listbox
        self.destroy_listbox()

        if not typed:
            return
     
        matches = [wine for wine in self.wine_list if typed in wine.lower()]
    
        if matches:
            # Create temporary frame for the listbox
            self.listbox_frame = tk.Frame(
                self.main_window,
                highlightbackground=Colours.BORDERS,
                highlightthickness=1
            )
            
            # Create listbox
            self.listbox = tk.Listbox(
                self.listbox_frame,
                height=min(5, len(matches)),
                selectmode="single",
                font=Fonts.TEXT_AUTOCOMPLETE,
                bg=Colours.BG_MAIN,
                selectbackground=Colours.BG_HOVER_NAV,
                borderwidth=0
            )
            
            # Calculate position relative to main window (top level)
            x = self.winfo_rootx() - self.main_window.winfo_rootx()
            y = self.winfo_rooty() - self.main_window.winfo_rooty() + self.winfo_height()
            
            # Place frame
            self.listbox_frame.place(
                x=x, 
                y=y, 
                width=self.winfo_width(),
                height=min(150, len(matches) * 25)  # Max height 150px
            )
            
            # Add matches in listbox
            for match in matches:
                self.listbox.insert(tk.END, match)
            
            # Fill frame with listbox
            self.listbox.pack(fill="both", expand=True)
            
            # Put listbox frame at front
            self.listbox_frame.lift()
            
            # Bind selection
            self.listbox.bind("<<ListboxSelect>>", self.select_suggestion)
            self.listbox.bind("<Button-1>", lambda e: self.select_on_click(e))

            # Global bind, click outside
            self.main_window.bind("<Button-1>", self.on_click_outside, add="+")
        
    def select_suggestion(self, event: tk.Event) -> None:
        """
        Inserts the selected suggestion into the entry.
        Parameters:
            - event: The triggering event.
        """
        if self.listbox and self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            # Clean entry 
            self.delete(0, tk.END) 
            # Add selected suggestion in entry
            self.insert(0, selected)
            # Clean listbox
            self.destroy_listbox()
    
    def select_on_click(self, event: tk.Event) -> None:
        """
        Selects a suggestion with a single mouse click.
        Parameters:
            - event: The triggering event.
        """
        # Get index of the clicked event
        index = self.listbox.nearest(event.y)
        if index >= 0:
            # Clear previous selections
            self.listbox.selection_clear(0, tk.END)
            # Set current selection
            self.listbox.selection_set(index)
            self.select_suggestion(event)
    
    def destroy_listbox(self) -> None:
        """
        Destroys the suggestion listbox and its frame.
        """
        if self.listbox_frame:
            self.main_window.unbind("<Button-1>")   
            self.listbox_frame.destroy()
            self.listbox_frame = None
            self.listbox = None

    def destroy(self) -> None:
        """
        Destroys the entry and any existing listbox..
        """
        self.destroy_listbox()
        super().destroy()


class BaseInput(ctk.CTkFrame):
    """
    Base frame for labeled input components.

    Parameters:
        - root: Parent frame.
        - label_text: Label text for the input.
        - optional: If True, the field is optional (no asterisk shown).
        - **kwargs: Additional keyword arguments passed to CTkFrame.
    """
    def __init__(
        self, root, label_text: str, optional: bool = False, **kwargs
    ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color="transparent",
        )
        
        # Create components
        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            text_color=Colours.TEXT_SECONDARY,
            font=Fonts.TEXT_LABEL,
            width=90,
            wraplength=90,
            anchor="w"
        )

        self.asterisk = "*" if not optional else ""
        self.label_optional = ctk.CTkLabel(
            self,
            text=self.asterisk,
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TEXT_LABEL,
            width=10,
            anchor="w"
        )
        
        # Place components
        self.label.grid(row=0, column=0, sticky="w") 
        self.label_optional.grid(row=0, column=1, padx=(0, 5))

    def set_label_layout(self, label_width: int) -> None:
        """
        Set the width and wraplength of the label.
        Parameters:
            - label_width: Width of the column label.
        """
        self.label.configure(
            width=label_width, wraplength=label_width
        )


class TextInput(BaseInput, EntryInputMixin):
    """
    A frame that contains a label and text entry component.
    """
    def __init__(self, root, placeholder: str | None = None, max_len: int = 60, 
        **kwargs):
        
        super().__init__(root, **kwargs)
        
        self.entry = TextEntry(
            self,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN,
            placeholder=placeholder,
            font=Fonts.TEXT_MAIN,
            width=300,
            max_len = max_len,
        )
        
        # Place components
        self.entry.grid(row=0, column=2)


class IntInput(BaseInput, EntryInputMixin):
    """
    A frame that contains a label and an integer entry component.
    """
    def __init__(
        self, root, placeholder: str | None = None, from_: int | None = None,
        to: int | None = None, textvariable: tk.Variable | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)

        self.entry = IntEntry(
            self,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            from_=from_,
            to=to,
            textvariable=textvariable,
            placeholder=placeholder,
        )
        
        # Place components
        self.entry.grid(row=0, column=2)


class DecimalInput(BaseInput, EntryInputMixin):
    """
    A frame that contains a label and an decimal entry component.
    """
    def __init__(
        self, root, placeholder: str | None = None, from_: Decimal | None = None,
        to: Decimal | None = None, textvariable: tk.Variable | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)

        self.entry = DecimalEntry(
            self,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            from_=from_,
            to=to,
            textvariable=textvariable,
            placeholder=placeholder,
        )
        
        # Place components
        self.entry.grid(row=0, column=2)


class AutoCompleteInput(BaseInput, EntryInputMixin):
    """
    A frame that contains a label and an AutoComplete entry component.
    Parameters:
        - root: Parent widget.
        - placeholder: Placeholder text for the entry.
        - textvariable: Optional Tk variable to bind the entry to.
        - item_list: List of items used for autocomplete.
        - **kwargs: Additional keyword arguments passed to BaseInput.
    """
    def __init__(
        self, root, placeholder: str | None = None, 
        textvariable: tk.Variable | None = None, item_list: list = [],
        **kwargs
    ):
        super().__init__(root, **kwargs)

        self.entry = AutocompleteEntry(
            self,
            item_list=item_list,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            textvariable=textvariable,
            placeholder=placeholder,
        )
        
        # Place components
        self.entry.grid(row=0, column=2)


class DateInput(BaseInput, EntryInputMixin):
    """
    A frame that contains a label and an date entry components
    """
    def __init__(
        self, root, textvariable: tk.Variable | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)

        self.entry = DateEntry(
            self,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            textvariable=textvariable,
            state="readonly"
        )

        self.entry.grid(row=0, column=2)

    def clear(self) -> None:
        """
        Removes the text typed by the user.
        """
        self.entry.configure(state="normal")
        self.entry.delete(0, "end") 
        self.entry.configure(state="readonly")


class DropdownInput(BaseInput):
    """
    A frame that contains a label and a dropdown components
    """
    def __init__(
        self, root, values: list[str], variable: tk.Variable | None = None, 
        command: Callable | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)
      
        self.dropdown = ctk.CTkOptionMenu(
            self,
            values=values,
            variable=variable,
            font=Fonts.TEXT_MAIN,
            fg_color=Colours.BG_MAIN,
            text_color=Colours.TEXT_MAIN,
            button_color=Colours.BG_HOVER_NAV,
            dropdown_fg_color=Colours.BG_MAIN,
            dropdown_hover_color=Colours.BG_HOVER_NAV,
            dropdown_text_color=Colours.TEXT_MAIN,
            button_hover_color=Colours.DROPDOWN_HOVER,
            command=command
        )
        
        # Place components
        self.dropdown.grid(row=0, column=2)
    
    def get(self) -> str:
        """
        Returns the selected value of Dropdown.
        """
        return self.dropdown.get()
    
    def set_to_first_value(self) -> None:
        """
        Sets the dropdown to its first available value.
        """
        return self.dropdown.set(self.dropdown.cget("values")[0])

    def update_values(self, values: list[str]) -> None:
        """
        Updates the available values of the dropdown.

        Inputs:
            - Values: New list of values that will be available in the dropdown.
        """
        self.dropdown.configure(values=values)

    def set_input_width(self, input_width: int):
        """
        Sets the total with of the dropdown used for aligment. 
        It creates an empty label to cover the remaning width.
        Parameters:
            - input_width: Total width of the input.
   
        """
        # Wait for the program to render widgets before gettign info
        self.update_idletasks()
        
        # Calculate widths
        label_width = self.label.winfo_width()
        label_asterisk_width = self.label_optional.winfo_width()
        dropdown_width = self.dropdown.winfo_width()
        empty_label_width = input_width - (label_width + dropdown_width + label_asterisk_width)

        if empty_label_width < 0:
            raise ValueError("input_width should be higher than labels width + dropdown width")

        # Create empty label for aligment
        empty_label = ctk.CTkLabel(
            self, # frame that contains all ctk components
            text="",
            width=empty_label_width
        )
        empty_label.grid(row=0, column=3)


class RadioInput(BaseInput):
    """
    A frame that contains a label and Radio Buttons components.
    Parameters:
        - root: Parent widget.
        - variable: Optional Tk variable to bind the entry to.
        - item_list: List of items representing each radio button. The item is a 
        tuple (text, value).
        - **kwargs: Additional keyword arguments passed to BaseInput.
    """
    def __init__(
        self, root, item_list: list[tuple], variable: tk.Variable | None = None, 
        **kwargs
    ):
        super().__init__(root, **kwargs)

        for index, item_ in enumerate(item_list, start=2):
            self.radio = ctk.CTkRadioButton(
                self,
                text=item_[0],
                value=item_[1],
                variable=variable,
                fg_color=Colours.BTN_ACTIVE,
                hover_color=Colours.BG_HOVER_BTN_SAVE,
                text_color=Colours.TEXT_MAIN, 
                font=Fonts.TEXT_MAIN,
                border_width_checked=8,
                border_color=Colours.BORDERS,
                width=50,
            )
            
            # Place component
            self.radio.grid(row=0, column=index, padx=(0, 15))


class ToggleInput(BaseInput):
    """
    A frame that contains a label and toggle-style buttons 
    for selecting one of multiple options.
    Parameters:
        - root: Parent widget.
        - variable: Tk variable to store the selected value.
        - item_list: List of tuples (text, value) for each toggle option.
        - **kwargs: Additional keyword arguments passed to BaseInput.
    """
    def __init__(
        self, root, item_list: list[tuple], variable: tk.Variable | None = None, 
        **kwargs
    ):
        super().__init__(root, **kwargs)
        self.variable = variable
        self.buttons = {}

        frame_toggles = ctk.CTkFrame(self, fg_color="transparent")
        frame_toggles.grid(row=0, column=2)

        for text, value in item_list:
            btn = ctk.CTkButton(
                frame_toggles,
                text=text,
                width=90,
                height=30,
                corner_radius=8,
                fg_color=Colours.BG_SECONDARY,
                text_color=Colours.TEXT_SECONDARY,
                hover_color=Colours.BG_HOVER_NAV,
                border_color=Colours.BORDERS,
                border_width=1,
                command=lambda v=value: self._select(v),
            )
            btn.pack(side="left", padx=5)
            self.buttons[btn] = value

        self._update_buttons()

    def _select(self, value: str):
        """
        Updates variable and button states.
        """
        self.variable.set(value)
        self._update_buttons()

    def _update_buttons(self):
        """
        Updates the visual appearance based on selected value.
        """
        for btn, val in self.buttons.items():
            if self.variable.get() == val:
                btn.configure(
                    fg_color=Colours.PRIMARY_WINE,
                    text_color="white",
                    border_color=Colours.PRIMARY_WINE,
                )
            else:
                btn.configure(
                    fg_color=Colours.BG_SECONDARY,
                    text_color=Colours.TEXT_SECONDARY,
                    border_color=Colours.BORDERS,
                )

        
class DoubleLabel(ctk.CTkFrame):
    """
    A frame that contains a title label and a value label.
    """
    def __init__(
        self, root, label_title_text: str, label_value_text: str = "",  
        text_variable: tk.Variable | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color="transparent",
        )
        
        # Create components
        self.label_title = ctk.CTkLabel(
            self,
            text=label_title_text,
            text_color=Colours.TEXT_SECONDARY,
            font=Fonts.TEXT_LABEL,
        )
    
        self.label_value = ctk.CTkLabel(
            self,
            text=label_value_text or None,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_LABEL,
            fg_color=Colours.BG_MAIN,
            corner_radius=10,
            textvariable=text_variable
        )

        # Place components
        self.label_title.grid(row=0, column=0, sticky="w", padx=(0, 10)) 
        self.label_value.grid(row=0, column=1)

    def update_value_text(self, new_text: str) -> None:
        """
        Update the text of the value label.

        Inputs:
            new_text = New text to include in the label_value.
        """
        self.label_value.configure(
            text=new_text
        )

    def bold_value_text(self) -> None:
        """
        Make the value label use the bold header font.
        """
        self.label_value.configure(font=Fonts.TEXT_HEADER)

    def set_columns_layout(self, title_width: int, value_width: int, anchor: str):
        """
        Set the width and anchor of both the title label and the value label.
        Parameters:
            - title_width: Width of the label_title column.
            - value_width: Width of the label_value column.
            - anchor: Position of the text.
        """
        self.label_title.configure(
            width=title_width, wraplength=title_width, anchor=anchor
        )
        self.label_value.configure(
            width=value_width, wraplength=value_width, anchor=anchor
        )


class ImageInput(BaseInput):
    """
    A frame that contains a text label, a file dialog button, and an image preview
    label.
    """
    def __init__(
        self, root, image_path: str | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color="transparent",
        )
        
        # Create components
        self.button = ctk.CTkButton(
            self,
            text="Choose File",
            text_color=Colours.BG_MAIN,
            fg_color=Colours.PRIMARY_WINE,
            font=Fonts.TEXT_MAIN,
            corner_radius=10,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            cursor="hand2",
            command=self.load_logo,
            width=170
        )

        image = load_ctk_image(image_path) if image_path else None
        self.label_preview = ctk.CTkLabel(
            self,
            image=image,
            text="",
            width=100,
            height=80,
            fg_color=Colours.BG_MAIN,               
        )
        
        self.temp_file_path = None

        # Place components
        self.button.grid(row=0, column=2, padx=5)
        self.label_preview.grid(row=0, column=3, padx=(15, 0))

    def load_logo(self) -> None:
        """
        Shows file dialog to the user and update the preview image.
        """
        self.temp_file_path = ctk.filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )

        # Show preview
        new_image = load_ctk_image(self.temp_file_path) if self.temp_file_path else None    
        self.label_preview.configure(
            image=new_image
        )

    def get_new_path(self) -> str | None:
        """
        Returns the temporary file path selected by the user, or None.
        """
        return self.temp_file_path

    def clear(self) -> None:
        """
        Sets the preview image to None
        """
        self.label_preview.configure(
            image=None
        )

    def set_input_width(self, input_width: int) -> None:
        """
        Sets the total width of the image input used for alignment.
        It creates an empty label to cover the remaining width.
        Parameters:
            - input_width: Total width of the input.
        """
        # Wait for the program to render widgets before gettign info
        self.update_idletasks()
        
        # Calculate widths
        label_width = self.label.winfo_width()
        label_asterisk_width = self.label_optional.winfo_width()
        label_preview_width = self.label_preview.winfo_width()
        button_width = self.button.winfo_width()
        empty_label_width = input_width - (label_width + label_preview_width + 
            label_asterisk_width + button_width + 25)

        if empty_label_width < 0:
            raise ValueError("input_width should be higher than labels width.")

        # Create empty label for aligment
        empty_label = ctk.CTkLabel(
            self, # frame that contains all ctk components
            text="",
            width=empty_label_width
        )
        empty_label.grid(row=0, column=4)

class ClearSaveButtons(ctk.CTkFrame):
    """
    A frame with Clear and Save buttons.

    Parameters:
        root: Parent widget.
        btn_clear_function: Callback executed when Clear is clicked.
        btn_save_function: Callback executed when Save is clicked.
        **kwargs: Additional keyword arguments passed to CTkFrame.
    """
    def __init__(self, root, btn_clear_function: Callable, 
    btn_save_function: Callable, **kwargs):
        super().__init__(root, **kwargs)
        self.configure(
            root,
            fg_color="transparent"
        )

        self.btn_clear_function = btn_clear_function
        self.btn_save_function = btn_save_function

        self.button_clear = ctk.CTkButton(
            self,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=10,
            cursor="hand2",
            command=self.clear_on_click,
        )
        self.button_save = ctk.CTkButton(
            self,
            text="Save",
            fg_color=Colours.BTN_SAVE,
            text_color=Colours.TEXT_BUTTON,
            font=Fonts.TEXT_BUTTON,
            hover_color=Colours.BG_HOVER_BTN_SAVE,
            corner_radius=10,
            state="disabled",
            command=self.save_on_click, 
        )
        
        self.button_clear.grid(row=0, column=0)
        self.button_save.grid(row=0, column=1, padx=20)

    def clear_on_click(self) -> None:
        """
        Executes callback function for the Clear button.
        """
        self.btn_clear_function()

    def save_on_click(self) -> None:
        """
        Executes callback function for the Save button.
        """
        self.btn_save_function()

    def enable_save_button(self) -> None:
        """
        Enables the Save button.
        """
        if self.button_save.cget("state") == "disabled":
            self.button_save.configure(state="normal", cursor="hand2")

    def disable_save_button(self) -> None:
        """
        Disables the save button.
        """
        self.button_save.configure(state="disabled", cursor="arrow")


class Card(ctk.CTkFrame):
    """
    A card that contains an image and a title button.
    """
    def __init__(
        self, root, title: str, image_path: str = "assets/cards/add_wine.png",
        on_click: Callable | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)
        # Frame
        self.configure(
            fg_color=Colours.BG_MAIN,
            border_width=1,
            border_color=Colours.BG_MAIN,
            corner_radius=10,
            cursor="hand2",
            
        )
        self.on_click = on_click 
           
        # Create components (They work better as buttons rather than labels)
        self.image = ctk.CTkButton(
            self,
            image=load_ctk_image(image_path, (150, 120)),
            text="",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            command=on_click,
        )
        self.title = ctk.CTkButton(
            self,
            text=title,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.SUBTITLE,
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            width=120,
            height=50,
            command=on_click,  
        )
        self.image.pack(pady=(5,0))
        self.title.pack(pady=5)

        # Add binds
        self.add_binds()
       
    def add_binds(self) -> None:
        """
        Add bindings so the whole frame behaves as a single clickable control.
        """
        if self.on_click:
            self.bind("<Button-1>", self.frame_clicked)
        for control in self.winfo_children():
            control.bind("<Enter>", self.frame_on_enter)
            control.bind("<Leave>", self.frame_on_leave)

    def frame_clicked(self, event: tk.Event) -> None:
        """
        Click event handler: call the callback if provided.
        """
        self.on_click()

    def frame_on_enter(self, event: tk.Event) -> None:
        """
        Hover enter: change hover color for frame and children.
        """
        self.configure(fg_color=Colours.BG_HOVER_NAV)
        for control in self.winfo_children():
            control.configure(fg_color=Colours.BG_HOVER_NAV)

    def frame_on_leave(self, event: tk.Event) -> None:
        """
        Hover leave: restore original colors.
        """
        self.configure(fg_color=Colours.BG_MAIN)
        for control in self.winfo_children():
            control.configure(fg_color="transparent")


class NavLink(ctk.CTkButton):
    """
    A button that behaves as a navigation link.

    Parameters:
        root: Parent widget.
        text: Button text.
        image: Optional icon image.
        command: Callback executed when clicked.
        **kwargs: Additional CTkButton keyword arguments.
    """
    def __init__(
        self, root, text: str = "", image: ctk.CTkImage | None = None, 
        command: Callable | None = None, **kwargs
    ):
        super().__init__(root, **kwargs)
        # Frame
        self.configure(
            root,
            text=text,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.NAVLINK,
            image=image,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            corner_radius=10,
            cursor="hand2",
            text_color_disabled=Colours.TEXT_MAIN,
            command=self.on_click
        )
        self.root = root
        self.callback = command

    def on_click(self) -> None:
        """
        Disable previously active navlink and execute callback.
        """
        # Do nothing if there is no function
        if self.callback is None:
            return

        # Set other navlinks enabled
        for widget in self.root.winfo_children():
            if isinstance(widget, NavLink) and widget.cget("state") == "disabled":
                widget.configure(
                    state="normal",
                    cursor="hand2",
                    font=Fonts.NAVLINK,
                    fg_color="transparent"
                )
        
        self.configure(
            state="disabled",
            cursor="arrow",
            font=Fonts.NAVLINK_ACTIVE,
            fg_color=Colours.BG_HOVER_NAV
        )

        self.callback()


class ButtonGoBack(ctk.CTkButton):
    """
    Button to go back to the previous section.
    """
    def __init__(self, root, command: Callable, **kwargs):
        super().__init__(root, **kwargs)
       
        self.configure(
            image=Icons.GO_BACK,
            fg_color=Colours.BG_SECONDARY, # I can't use transparent here
            text="",
            hover_color=Colours.BG_SECONDARY,
            anchor="w",
            cursor="hand2",
            width=20,
            height=30,
            command=command
        )

        self.bind("<Enter>", lambda e: self.configure(image=Icons.GO_BACK_HOVER))
        self.bind("<Leave>", lambda e: self.configure(image=Icons.GO_BACK))
        

class ActionMenuButton(ctk.CTkFrame):
    """
    Button that shows a contextual menu with actions (Show, Edit, Delete).

    Parameters:
        root: Parent widget.
        on_show: Callback executed when 'Show Details' is selected.
        on_edit: Callback executed when 'Edit' is selected.
        on_delete: Callback executed when 'Delete' is selected.
        **kwargs: Additional CTkFrame keyword arguments.
    """
    def __init__(self, root, on_show, on_edit, on_delete, **kwargs):
        super().__init__(
            root, 
            fg_color="transparent", 
            cursor="hand2",
            **kwargs
        )

        # Callbacks
        self.on_show = on_show
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.menu_visible = False
        self.menu_frame = None

        # Button
        self.menu_button = ctk.CTkButton(
            self,
            text="",
            text_color=Colours.TEXT_BUTTON,
            image=Icons.DOTS,
            width=25,
            height=25,
            fg_color="transparent",
            hover_color="#EEE5E5",
            command=self.toggle_menu
        )
        self.menu_button.pack(expand=True)

    def toggle_menu(self) -> None:
        """
        Shows or hides the menu.
        """
        if self.menu_visible:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self) -> None:
        """
        Shows and creates the contextual menu with actions.
        """
        self.menu_visible = True

        # Frame container of the menu
        self.menu_frame = ctk.CTkFrame(
            self.winfo_toplevel(), # First Parent
            corner_radius=8,
            fg_color="white",
            border_color="#DDD",
            border_width=1
        )

        # Action buttons
        btn_show_detail = ctk.CTkButton(
            self.menu_frame,
            text="Show Details",
            image=Icons.SHOW,
            anchor="w",
            fg_color="transparent",
            text_color="black",
            hover_color="#F0E0E0",
            height=28,
            command=lambda: self._handle_action(self.on_show)
        )
        btn_show_detail.pack(fill="x", padx=5, pady=(3, 0))

        btn_edit = ctk.CTkButton(
            self.menu_frame,
            text="Edit Wine",
            image=Icons.EDIT,
            anchor="w",
            fg_color="transparent",
            text_color="black",
            hover_color="#F0E0E0",
            height=28,
            command=lambda: self._handle_action(self.on_edit)
        )
        btn_edit.pack(fill="x", padx=5, pady=(3, 0))

        btn_delete = ctk.CTkButton(
            self.menu_frame,
            text="Delete Wine",
            image=Icons.DELETE,
            anchor="w",
            fg_color="transparent",
            text_color="#C0392B",
            hover_color="#F8E5E5",
            height=28,
            command=lambda: self._handle_action(self.on_delete)
        )
        btn_delete.pack(fill="x", padx=5, pady=(3, 3))

        # Place the menu under the clicked button
        x = self.menu_button.winfo_rootx() - self.winfo_toplevel().winfo_rootx() - self.menu_button.winfo_width()
        y = self.menu_button.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + 30
        
        self.menu_frame.place(x=x, y=y)
        self.menu_frame.lift()

        # Bind click outside to close menu
        self.winfo_toplevel().bind("<Button-1>", self._check_click_outside, add="+")

    def hide_menu(self) -> None:
        """
        Destroys the menu if exists.
        """
        if self.menu_frame:
            self.menu_frame.destroy()
            self.menu_frame = None
            self.menu_visible = False

            # Unbind the click event
            try:
                self.winfo_toplevel().unbind("<Button-1>", self._check_click_outside)
            except:
                pass

    def _handle_action(self, callback: Callable | None) -> None:
        """
        Destroys the menu and executes the triggered function through a callback.
        """
        
        self.hide_menu()
        if callback:
            callback()

    def destroy(self) -> None:
        """
        Destroys any existing menu before destroying itself.
        """    
        # Destroy existing menu frame
        self.hide_menu()

        super().destroy()

    def _check_click_outside(self, event: tk.Event) -> None:
        """
        Checks if click was outside the menu and closes it.
        """
        if not self.menu_visible:
            return
            
        # Get the widget that was clicked
        widget = event.widget
        
        # Check if click was inside menu_frame or menu_button
        is_inside_menu = False
        is_inside_button = False
        
        # Check if clicked widget is the menu or a child of it
        if self.menu_frame and widget.winfo_exists():
            try:
                parent = widget
                while parent:
                    if parent == self.menu_frame:
                        is_inside_menu = True
                        break
                    if parent == self.menu_button:
                        is_inside_button = True
                        break
                    parent = parent.master if hasattr(parent, 'master') else None
            except:
                pass
        
        # Close menu if clicked outside (but not on the button itself)
        if not is_inside_menu and not is_inside_button:
            self.hide_menu()

        
