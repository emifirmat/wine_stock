"""
Custom UI components and widgets.

This module provides reusable CustomTkinter components including specialized
entry fields, input containers, buttons, and composite widgets designed for
the wine stock management application.
"""
import calendar
import customtkinter as ctk
import datetime
import tkinter as tk
import re
from decimal import Decimal
from typing import Callable

from helpers import load_ctk_image
from ui.style import Colours, Fonts, Icons, Spacing, Rounding


class EntryInputMixin:
    """
    Mixin providing utility methods for entry widget management.
    
    Provides methods for setting width, clearing content, getting values,
    and updating text in entry widgets.
    """
    def set_entry_width(self, entry_width: int) -> None:
        """
        Set the width of the entry widget.
        
        Parameters:
            entry_width: Width to apply to the entry widget in pixels
        """
        self.entry.configure(width=entry_width)
    
    def clear(self) -> None:
        """
        Remove all text from the entry widget.
        """
        self.entry.delete(0, "end") 

    def get(self) -> str:
        """
        Get the current value of the entry widget.
        
        Returns:
            Text currently contained in the entry
        """
        return self.entry.get()

    def set_total_width(self, total_width: int) -> None:
        """
        Set total width of the input container for alignment.
        
        Creates an empty label to fill remaining width, ensuring
        consistent alignment across multiple input fields.
        
        Parameters:
            total_width: Total width of the input container in pixels
            
        Raises:
            ValueError: If total width is smaller than sum of components
            
        Requirements:
            - Class must inherit from CTkFrame
            - Class must define self.label, self.label_optional, and self.entry
        """
        # Ensure widgets are rendered before measuring
        self.update_idletasks()
        
        # Calculate widths
        label_width = self.label.winfo_width()
        label_asterisk_width = self.label_optional.winfo_width()
        entry_width = self.entry.winfo_width()
        empty_label_width = total_width - (label_width + entry_width + label_asterisk_width)

        if empty_label_width < 0:
            raise ValueError(
                "total_width must be greater than label_width + entry_width + labels_asterisk_width"
            )

        # Create empty label for alignment
        empty_label = ctk.CTkLabel(
            self, # frame that contains all ctk components
            text="",
            width=empty_label_width
        )
        empty_label.grid(row=0, column=3)

    def update_text_value(self, new_text: str) -> None:
        """
        Update the text in the entry widget.
        
        Parameters:
            new_text: New text to insert
        """
        self.entry.delete(0, ctk.END) 
        self.entry.insert(0, new_text)


class LabelWithBorder(ctk.CTkFrame):
    """
    Label with customizable border.
    
    CTkLabel doesn't support borders, so this wraps a label in a frame
    to achieve border styling.
    """
    def __init__(
        self, root, text: str, text_color: str, font: tuple, **kwargs
    ):
        """
        Initialize labeled frame with border.
        
        Parameters:
            root: Parent widget
            text: Label text content
            text_color: Text color in hex format
            font: Font tuple (family, size, weight)
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        
        self.label = ctk.CTkLabel(
            self,
            text=text,
            text_color=text_color,
            font=font,
        )
        self.label.pack(
            padx=Spacing.LABELS_X, pady=Spacing.LABELS_Y, expand=True, fill="both"
        )

    def configure_label(self, **kwargs):
        """ 
        Configure label attributes.
        
        Parameters:
            **kwargs: Keyword arguments passed to label.configure()
        """
        self.label.configure(**kwargs)


class TextEntry(ctk.CTkEntry):
    """
    Entry widget with maximum length validation.
    """
    def __init__(self, root, placeholder: str, max_len: int = 60, **kwargs):
        """
        Initialize text entry with length limit.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            max_len: Maximum allowed character length
            **kwargs: Additional CTkEntry keyword arguments
        """
        super().__init__(
            root, 
            placeholder_text=placeholder, 
            placeholder_text_color=Colours.TEXT_SECONDARY,
            **kwargs
        )

        self.max_len = max_len

        # Register validation function
        validate_cmd = self.register(self._validate_len) 

        self.configure(
            validate="key", # Every time user types, it will do a validation
            # %P is from Tkinter and means "new content after typing"
            validatecommand=(validate_cmd, "%P"),      
        )

    def _validate_len(self, text: str) -> bool:
        """
        Validate text length.
        
        Parameters:
            text: Current text in entry
            
        Returns:
            True if valid, False otherwise
        """
        return len(text) <= self.max_len


class IntEntry(ctk.CTkEntry):
    """
    Entry widget that only accepts integer values within a range.
    """
    def __init__(
        self, root, placeholder: str, from_: int | None = None, to: int | None = None, 
        textvariable: tk.StringVar | None = None, **kwargs
    ):
        """
        Initialize integer entry with optional range constraints.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            from_: Minimum allowed value (inclusive)
            to: Maximum allowed value (inclusive)
            textvariable: Optional Tk variable to bind
            **kwargs: Additional CTkEntry keyword arguments
        """
        super().__init__(
            root, 
            placeholder_text=placeholder, 
            placeholder_text_color=Colours.TEXT_SECONDARY,
            **kwargs
        )
        self.min_val = from_
        self.max_val = to
        
        # Register validation function
        validate_cmd = self.register(self._validate_value) 

        self.configure(
            validate="key", # Every time user types, it will do a validation
            # %P is from Tkinter and means "new content after typing"
            validatecommand=(validate_cmd, "%P"),
            textvariable=textvariable
        )       

    def _validate_value(self, text: str) -> bool:
        """
        Validate integer input and range.
        
        Parameters:
            text: Text entered by user
            
        Returns:
            True if valid, False otherwise   
        """
        if text == "":
            return True
        
        if text.isdigit():
            number = int(text)

            # Check minimum bound
            if self.min_val is not None and number < self.min_val:
                return False
            
            # Check maximum bound
            if self.max_val is not None and number > self.max_val:
                return False
            
            return True
        
        # Number is not an integer
        return False
    

class DecimalEntry(ctk.CTkEntry):
    """
    Entry widget that accepts decimal values within a range.
    """
    def __init__(
        self, root, placeholder: str, from_: int | None = None, to: int | None = None, 
        textvariable: tk.StringVar | None = None, **kwargs
    ):
        """
        Initialize decimal entry with optional range constraints.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            from_: Minimum allowed value (inclusive)
            to: Maximum allowed value (inclusive)
            textvariable: Optional Tk variable to bind
            **kwargs: Additional CTkEntry keyword arguments
        """
        super().__init__(
            root, 
            placeholder_text=placeholder, 
            placeholder_text_color=Colours.TEXT_SECONDARY,
            **kwargs
        )
        self.min_val = from_
        self.max_val = to

        # Register validation function
        validate_cmd = self.register(self._validate_value) 

        self.configure( 
            validate="key", 
            validatecommand=(validate_cmd, "%P"),
            textvariable=textvariable
        )       

    def _validate_value(self, text: str) -> bool:
        """
        Validate decimal input and range.
        
        Accepts formats like "123", "0.5", ".5", "5."
        
        Parameters:
            text: Text entered by user
            
        Returns:
            True if valid, False otherwise
        """
        
        if text == "" :
            return True

        # Accept only numbers and dot
        if not re.fullmatch(r"\d*\.?\d*", text):
            return False
        
        # Accept trailing dot (intermediate state)
        if text.endswith('.'):
            return True
     
        # Convert to Decimal 
        try:   
            number = Decimal(text)
        # Catch other symbols
        except (ValueError, TypeError):
            return False
        
        # Check minimum bound
        if self.min_val is not None and number < self.min_val:
            return False
        
        # Check maximum bound
        if self.max_val is not None and number > self.max_val:
            return False
        
        return True


class DateEntry(ctk.CTkEntry):
    """
    Entry widget with popup calendar for date selection.
    """
    def __init__(self, root, textvariable: tk.StringVar | None = None, **kwargs):
        """
        Initialize date entry with calendar popup.
        
        Parameters:
            root: Parent widget
            textvariable: Optional Tk variable to bind
            **kwargs: Additional CTkEntry keyword arguments
        """
        self.text_var = textvariable or tk.StringVar()
        
        super().__init__(root, textvariable=self.text_var, **kwargs)     

        self.year = None
        self.month = None
        self.frame_calendar = None

        # Show calendar on click
        self.bind("<Button-1>", self.open_calendar)

    def open_calendar(self, event: tk.Event | None = None) -> None:
        """
        Open calendar popup for date selection.
        
        Parameters:
            event: Triggering event (unused but required by bind)
        """
        # Get current date
        today = datetime.date.today()
        self.year = today.year
        self.month = today.month
        
        # Destroy any previous calendar
        self.close_calendar()

        # Create calendar frame
        self.frame_calendar = ctk.CTkFrame(
            self.winfo_toplevel(),
            fg_color=Colours.BG_MAIN,
            border_width=2,
            border_color=Colours.BORDERS,
            corner_radius=Rounding.CALENDAR,
        )
        
        # Position calendar below entry
        x = self.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
        y = self.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + self.winfo_height() + 5
        self.frame_calendar.place(x=x, y=y)
        self.frame_calendar.lift()
       
        # Build calendar UI
        self.build_calendar()
    
    def build_calendar(self) -> None:
        """
        Build calendar structure with navigation and day buttons.
        """
        # Clear previous calendar widgets
        for widget in self.frame_calendar.winfo_children():
            widget.destroy()

        calendar_ = calendar.monthcalendar(self.year, self.month)

        # Header with month and year
        header = ctk.CTkLabel(
            self.frame_calendar, 
            text=f"{calendar.month_name[self.month]} {self.year}",
            font=Fonts.TEXT_HEADER_CALENDAR
        )
        header.grid(row=0, column=2, columnspan=3, pady=Spacing.SMALL)

        # Navigation buttons
        buttons_config = [
            ("<<", 0, 0, (Spacing.SMALL, 0), self.prev_year),
            ("<", 0, 1, 0, self.prev_month),
            (">", 0, 5, 0, self.next_month),
            (">>", 0, 6, (0, Spacing.SMALL), self.next_year),
        ]

        for text, row, col, padx, command in buttons_config:
            ctk.CTkButton(
                self.frame_calendar,
                text=text,
                width=30,
                fg_color=Colours.BG_HOVER_NAV,
                text_color=Colours.TEXT_MAIN,
                hover_color=Colours.DROPDOWN_HOVER,
                command=command
            ).grid(row=row, column=col, padx=padx)

        # Days headers
        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            ctk.CTkLabel(
                self.frame_calendar, text=day
            ).grid(row=1, column=i, padx=2, pady=2)

        # Days buttons
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
                    
                    # Set padding for borders
                    if c == 0:
                        padx = (Spacing.SMALL, 1)
                    elif c == len(week) - 1:
                        padx = (1, Spacing.SMALL)
                    else:
                        padx = 1

                    pady = 1 if r != len(calendar_) + 1 else (1, Spacing.SMALL)
                    button.grid(row=r, column=c, padx=padx, pady=pady)

    def prev_month(self) -> None:
        """
        Navigate to previous month in calendar.
        """
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.build_calendar()

    def next_month(self) -> None:
        """
        Navigate to next month in calendar.
        """
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.build_calendar()

    def prev_year(self) -> None:
        """
        Navigate to previous year in calendar.
        """
        self.year -= 1
        self.build_calendar()

    def next_year(self):
        """
        Navigate to next year in calendar.
        """
        self.year += 1
        self.build_calendar()

    def select_date(self, day: int) -> None:
        """
        Handle date selection from calendar.
        
        Parameters:
            day: Selected day of the month
        """
        # Format and display selected date
        selected = datetime.date(self.year, self.month, day)
        self.text_var.set(selected.strftime("%d/%m/%Y"))
        
        # Close calendar
        self.close_calendar()

    def close_calendar(self) -> None:
        """
        Close the calendar popup if it exists.
        """
        if self.frame_calendar:
            self.frame_calendar.destroy()
            self.frame_calendar = None
    
    def destroy(self) -> None:
        """
        Destroy the entry and any associated calendar popup.
        """
        self.close_calendar()
        super().destroy()


class AutocompleteEntry(ctk.CTkEntry):
    """
    Entry widget with autocomplete suggestions from a list.
    """
    def __init__(self, root, placeholder: str, item_list: list[str], **kwargs):
        """
        Initialize autocomplete entry.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            item_list: List of items for autocomplete suggestions
            **kwargs: Additional CTkEntry keyword arguments
        """
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
        self.hovered_index = None
        
        self.bind("<KeyRelease>", self.show_suggestions)
        self.bind("<Button-1>", self.show_suggestions)

    def on_click_outside(self, event: tk.Event) -> None:
        """
        Close suggestion list when clicking outside.
        
        Parameters:
            event: Click event.
        """
        if not self.listbox_frame:
            return
        
        # Get click coordinates
        x = event.x_root
        y = event.y_root
        
        # Check if click was in entry
        entry_x = self.winfo_rootx()
        entry_y = self.winfo_rooty()
        entry_width = self.winfo_width()
        entry_height = self.winfo_height()
        
        in_entry = (entry_x <= x <= entry_x + entry_width and 
                    entry_y <= y <= entry_y + entry_height)
        
        # Check if click was in listbox
        if self.listbox_frame and self.listbox_frame.winfo_exists():
            listbox_x = self.listbox_frame.winfo_rootx()
            listbox_y = self.listbox_frame.winfo_rooty()
            listbox_width = self.listbox_frame.winfo_width()
            listbox_height = self.listbox_frame.winfo_height()
            
            in_listbox = (listbox_x <= x <= listbox_x + listbox_width and 
                        listbox_y <= y <= listbox_y + listbox_height)
        else:
            in_listbox = False
        
        # Close listbox if clicked outside
        if not in_entry and not in_listbox:
            self.destroy_listbox()

    def show_suggestions(self, event: tk.Event | None = None) -> None:
        """
        Display autocomplete suggestions based on input.
        
        Parameters:
            event: Triggering event (unused but required by bind)
        """
        typed = self.get().lower()

        # Clear previous listbox
        self.destroy_listbox()

        if not typed:
            return
     
        # Find matches (case-insensitive substring search)
        matches = [wine for wine in self.wine_list if typed in wine.lower()]

        if matches:
            # Create listbox container frame
            self.listbox_frame = tk.Frame(
                self.main_window,
                highlightbackground=Colours.BORDERS,
                highlightthickness=1
            )
            
            # Create listbox
            listbox_font = Fonts.TEXT_AUTOCOMPLETE
            self.listbox = tk.Listbox(
                self.listbox_frame,
                height=min(5, len(matches)),
                selectmode="single",
                font=listbox_font,
                bg=Colours.BG_MAIN,
                selectbackground=Colours.BG_HOVER_NAV,
                borderwidth=0,
                fg=Colours.TEXT_MAIN,
            )
            
            # Calculate ideal width according to matches length
            font_obj = tk.font.Font(font=listbox_font)
            longest_text_width = max(font_obj.measure(m) for m in matches)
            entry_width = self.winfo_width()
            max_width = int(self.main_window.winfo_width() * 0.6)
    
            # Listbox width should be from entry_width to max_width
            listbox_width = max(entry_width, min(longest_text_width + 24, max_width))

            # Calculate position relative to main window
            x = self.winfo_rootx() - self.main_window.winfo_rootx()
            y = self.winfo_rooty() - self.main_window.winfo_rooty() + self.winfo_height()
            
            # Position frame
            self.listbox_frame.place(
                x=x, 
                y=y, 
                width=listbox_width,
                height=min(150, len(matches) * 25)  # Max height 150px
            )
            
            # Populate listbox with matches
            for match in matches:
                self.listbox.insert(tk.END, match)
            
            # Pack listbox in frame
            self.listbox.pack(fill="both", expand=True)
            
            # Bring to front
            self.listbox_frame.lift()
            
            # Bind selection events
            self.listbox.bind("<<ListboxSelect>>", self.select_suggestion)
            self.listbox.bind("<Button-1>", lambda e: self.select_on_click(e))
            # Bind hover events
            self.listbox.bind("<Motion>", self.on_hover)
            self.listbox.bind("<Leave>", self.on_leave)

            # Global bind, click outside
            self.main_window.bind("<Button-1>", self.on_click_outside, add="+")

    def select_suggestion(self, event: tk.Event) -> None:
        """
        Insert selected suggestion into entry.
        
        Parameters:
            event: Selection event
        """
        if self.listbox and self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            
            # Update entry with selection
            self.delete(0, tk.END) 
            self.insert(0, selected)
            
            # Close listbox
            self.destroy_listbox()
    
    def select_on_click(self, event: tk.Event) -> None:
        """
        Select suggestion with single mouse click.
        
        Parameters:
            event: Click event
        """
        # Get clicked item index
        index = self.listbox.nearest(event.y)
        if index >= 0:
            # Update selection
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.select_suggestion(event)
    
    def destroy_listbox(self) -> None:
        """
        Destroy suggestion listbox and its frame.
        """
        if self.listbox_frame:
            self.main_window.unbind("<Button-1>")   
            self.listbox_frame.destroy()
            self.listbox_frame = None
            self.listbox = None
            self.hovered_index = None 

    def destroy(self) -> None:
        """
        Destroy the entry and any existing listbox.
        """
        self.destroy_listbox()
        super().destroy()

    def on_hover(self, event: tk.Event) -> None:
        """
        Highlight the item under the cursor when hovering.
        
        Parameters:
            event: Motion event
        """
        if not self.listbox:
            return

        index = self.listbox.nearest(event.y)
        if index != self.hovered_index:
            # Remove highlight from previous item
            if self.hovered_index is not None:
                self.listbox.itemconfig(self.hovered_index, bg=Colours.BG_MAIN)

            # Highlight current item
            self.listbox.itemconfig(index, bg=Colours.BG_HOVER_NAV)
            self.hovered_index = index


    def on_leave(self, event: tk.Event) -> None:
        """
        Restore background when leaving the listbox area.

        Parameters:
            event: Leave listbox event
        """
        if self.listbox and self.hovered_index is not None:
            self.listbox.itemconfig(self.hovered_index, bg=Colours.BG_MAIN)
            self.hovered_index = None


class BaseInput(ctk.CTkFrame):
    """
    Base frame for labeled input components.
    
    Provides consistent label layout with optional required indicator (asterisk).
    """
    def __init__(
        self, root, label_text: str, optional: bool = False, **kwargs
    ):
        """
        Initialize base input frame with label.
        
        Parameters:
            root: Parent widget
            label_text: Text for the input label
            optional: If True, field is optional (no asterisk shown)
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color="transparent")
        
        # Create label components
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
        self.label_optional.grid(row=0, column=1, padx=(0, Spacing.SMALL))

    def set_label_layout(self, label_width: int) -> None:
        """
        Set width and wraplength of the label.
        
        Parameters:
            label_width: Width in pixels for the label column
        """
        self.label.configure(width=label_width, wraplength=label_width)


class TextInput(BaseInput, EntryInputMixin):
    """
    Frame containing label and text entry component.
    """
    def __init__(
        self, root, placeholder: str | None = None, max_len: int = 60, **kwargs
    ):
        """
        Initialize text input.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            max_len: Maximum character length
            **kwargs: Additional BaseInput keyword arguments
        """
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
        
        self.entry.grid(row=0, column=2)


class IntInput(BaseInput, EntryInputMixin):
    """
    Frame containing label and integer entry component.
    """
    def __init__(
        self, root, placeholder: str | None = None, from_: int | None = None,
        to: int | None = None, textvariable: tk.Variable | None = None, **kwargs
    ):
        """
        Initialize integer input.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            from_: Minimum allowed value
            to: Maximum allowed value
            textvariable: Optional Tk variable to bind
            **kwargs: Additional BaseInput keyword arguments
        """
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
        
        self.entry.grid(row=0, column=2)


class DecimalInput(BaseInput, EntryInputMixin):
    """
    Frame containing label and decimal entry component.
    """
    def __init__(
        self, root, placeholder: str | None = None, from_: Decimal | None = None,
        to: Decimal | None = None, textvariable: tk.Variable | None = None, **kwargs
    ):
        """
        Initialize decimal input.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            from_: Minimum allowed value
            to: Maximum allowed value
            textvariable: Optional Tk variable to bind
            **kwargs: Additional BaseInput keyword arguments
        """
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
        
        self.entry.grid(row=0, column=2)


class AutocompleteInput(BaseInput, EntryInputMixin):
    """
    Frame containing label and autocomplete entry component.
    """
    def __init__(
        self, root, placeholder: str | None = None, 
        textvariable: tk.Variable | None = None, item_list: list[str] = [],
        **kwargs
    ):
        """
        Initialize autocomplete input.
        
        Parameters:
            root: Parent widget
            placeholder: Placeholder text
            textvariable: Optional Tk variable to bind
            item_list: List of items for autocomplete suggestions
            **kwargs: Additional BaseInput keyword arguments
        """
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
        
        self.entry.grid(row=0, column=2)


class DateInput(BaseInput, EntryInputMixin):
    """
    Frame containing label and date entry with calendar popup.
    """
    def __init__(
        self, root, textvariable: tk.Variable | None = None, **kwargs
    ):
        """
        Initialize date input.
        
        Parameters:
            root: Parent widget
            textvariable: Optional Tk variable to bind
            **kwargs: Additional BaseInput keyword arguments
        """
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
        Remove the selected date from the entry.
        """
        self.entry.configure(state="normal")
        self.entry.delete(0, "end") 
        self.entry.configure(state="readonly")


class DropdownInput(BaseInput):
    """
    Frame containing label and dropdown menu component.
    """
    def __init__(
        self, root, values: list[str], variable: tk.Variable | None = None, 
        command: Callable | None = None, **kwargs
    ):
        """
        Initialize dropdown input.
        
        Parameters:
            root: Parent widget
            values: List of dropdown options
            variable: Optional Tk variable to bind
            command: Callback executed when selection changes
            **kwargs: Additional BaseInput keyword arguments
        """
        super().__init__(root, **kwargs)
      
        self.dropdown = ctk.CTkOptionMenu(
            self,
            values=values,
            variable=variable,
            font=Fonts.TEXT_MAIN,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN,
            button_color=Colours.BG_HOVER_NAV,
            dropdown_font= Fonts.TEXT_DROPDOWN,
            dropdown_fg_color=Colours.BG_MAIN,
            dropdown_hover_color=Colours.BG_HOVER_NAV,
            dropdown_text_color=Colours.TEXT_MAIN,
            button_hover_color=Colours.DROPDOWN_HOVER,
            command=command
        )
        
        self.dropdown.grid(row=0, column=2)
    
    def get(self) -> str:
        """
        Get the currently selected dropdown value.
        
        Returns:
            Selected value as string
        """
        return self.dropdown.get()
    
    def set_to_first_value(self) -> None:
        """
        Set dropdown to its first available value.
        """
        return self.dropdown.set(self.dropdown.cget("values")[0])

    def set_to_value(self, text: str) -> None:
        """
        Set dropdown to specified value or first value if not found.
        
        Parameters:
            text: Value to set (case-insensitive)
        """
        values = self.dropdown.cget("values")
        
        # Handle empty text
        if not text:
            self.set_to_first_value()
            return
        
        # Try to match value (dropdowns usually use title case)
        formatted_text = text.title()
        if formatted_text in values: 
            self.dropdown.set(formatted_text)
        else:
            self.set_to_first_value()
        

    def configure_dropdown(self, **kwargs) -> None:
        """
        Configure dropdown attributes.
        
        Parameters:
            **kwargs: Keyword arguments passed to dropdown.configure()
        """
        self.dropdown.configure(**kwargs)

    def set_total_width(self, total_width: int) -> None:
        """
        Update the available dropdown options.
        
        Parameters:
            values: New list of dropdown options
   
        """
        # Wait for widgets to render
        self.update_idletasks()
        
        # Calculate widths
        label_width = self.label.winfo_width()
        label_asterisk_width = self.label_optional.winfo_width()
        dropdown_width = self.dropdown.winfo_width()
        empty_label_width = total_width - (label_width + dropdown_width + label_asterisk_width)

        if empty_label_width < 0:
            raise ValueError("total_width must be greater than label widths + dropdown width.")

        # Create empty label for alignment
        ctk.CTkLabel(
            self, 
            text="",
            width=empty_label_width
        ).grid(row=0, column=3)


class RadioInput(BaseInput):
    """
    Frame containing label and radio button components.
    """
    def __init__(
        self, root, item_list: list[tuple], variable: tk.Variable | None = None, 
        **kwargs
    ):
        """
        Initialize radio button input.
        
        Parameters:
            root: Parent widget
            item_list: List of tuples (display_text, value) for each radio button
            variable: Optional Tk variable to bind
            **kwargs: Additional BaseInput keyword arguments
        """
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
            
            self.radio.grid(row=0, column=index, padx=(0, 15))


class ToggleInput(BaseInput):
    """
    Frame containing label and toggle-style button group."
    """
    def __init__(
        self, root, item_list: list[tuple[str, str]],
        variable: tk.Variable | None = None, **kwargs
    ):
        """
        Initialize toggle button input.
        
        Parameters:
            root: Parent widget
            item_list: List of tuples (display_text, value) for each toggle option
            variable: Tk variable to store selected value
            **kwargs: Additional BaseInput keyword arguments
        """
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
                corner_radius=Rounding.TOGGLE,
                fg_color=Colours.BG_SECONDARY,
                text_color=Colours.TEXT_SECONDARY,
                hover_color=Colours.BG_HOVER_NAV,
                border_color=Colours.BORDERS,
                border_width=1,
                command=lambda v=value: self._select(v),
            )
            btn.pack(side="left", padx=Spacing.BUTTONS_X, pady=Spacing.BUTTONS_Y)
            self.buttons[btn] = value

        self._update_buttons()

    def _select(self, value: str) -> None:
        """
        Update variable and button states when selection changes.
        
        Parameters:
            value: Selected value
        """
        self.variable.set(value)
        self._update_buttons()

    def _update_buttons(self) -> None:
        """
        Update visual appearance of buttons based on selected value.
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
    Frame containing a title label and a value label.
    """
    def __init__(
        self, root, label_title_text: str, label_value_text: str = "",  
        text_variable: tk.Variable | None = None, **kwargs
    ):
        """
        Initialize double label component.
        
        Parameters:
            root: Parent widget
            label_title_text: Text for the title label
            label_value_text: Initial text for the value label
            text_variable: Optional Tk variable to bind to value label
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color="transparent")
        
        # Create labels
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
            corner_radius=Rounding.LABEL,
            textvariable=text_variable
        )

        # Place labels
        self.label_title.grid(
            row=0, column=0, sticky="w", padx=(0, Spacing.SMALL), pady=Spacing.LABELS_Y) 
        self.label_value.grid(row=0, column=1, padx=Spacing.LABELS_X, pady=Spacing.LABELS_Y)

    def bold_value_text(self) -> None:
        """
        Apply bold header font to value label.
        """
        self.label_value.configure(font=Fonts.TEXT_HEADER)

    def set_columns_layout(
        self, title_width: int, 
        value_width: int | None = None, anchor: str = "w"
    ) -> None: 
        """
        Set width and anchor for both labels.
        
        Parameters:
            title_width: Width of title label in pixels
            value_width: Width of value label in pixels (optional)
            anchor: Text anchor position (default: "w" for left)
        """ 
        self.label_title.configure(
            width=title_width, wraplength=title_width, anchor=anchor
        )
    
        if value_width:
            self.label_value.configure(
                width=value_width, wraplength=value_width, anchor=anchor
            )
    
    def configure_label_value(self, **kwargs) -> None:
        """
        Configure value label attributes.
        
        Parameters:
            **kwargs: Keyword arguments passed to label.configure()
        """
        self.label_value.configure(**kwargs)

    def set_total_width(self, total_width: int) -> None:
        """
        Set total width of double label for alignment.
        
        Creates an empty label to fill remaining width.
        
        Parameters:
            total_width: Total width in pixels
            
        Raises:
            ValueError: If total width is smaller than sum of components
        """
        # Ensure widgets are rendered
        self.update_idletasks()
        
        # Calculate widths
        title_width = self.label_title.winfo_width()
        value_width = self.label_value.winfo_width()
        empty_label_width = total_width - (title_width + value_width)

        if empty_label_width < 0:
            raise ValueError("total_width must be greater than label_width + value_width.")

        # Create empty label for aligment
        ctk.CTkLabel(
            self, # frame that contains all ctk components
            text="",
            width=empty_label_width,
        ).grid(row=0, column=2)


class ImageInput(BaseInput):
    """
    Frame containing label, file dialog button, and image preview.
    """
    def __init__(self, root, image_path: str | None = None, **kwargs):
        """
        Initialize image input with file selector and preview.
        
        Parameters:
            root: Parent widget
            image_path: Initial image path to display
            **kwargs: Additional BaseInput keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color="transparent")
        
        # Create file selection button
        self.button = ctk.CTkButton(
            self,
            text="Choose File",
            text_color=Colours.BG_MAIN,
            fg_color=Colours.PRIMARY_WINE,
            font=Fonts.TEXT_MAIN,
            corner_radius=Rounding.BUTTON,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            cursor="hand2",
            command=self.load_logo,
            width=170
        )

        # Create preview label
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
        self.button.grid(row=0, column=2, padx=Spacing.BUTTONS_X, pady=Spacing.BUTTONS_Y)
        self.label_preview.grid(row=0, column=3, padx=Spacing.LABELS_X, pady=Spacing.LABELS_Y)

    def load_logo(self) -> None:
        """
        Open file dialog and update preview with selected image.
        """
        self.temp_file_path = ctk.filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )

        self.show_preview()
    
    def show_preview(self) -> None:
        """
        Load and display the selected image in preview label.
        """
        new_image = load_ctk_image(self.temp_file_path) if self.temp_file_path else None    
        self.label_preview.configure(image=new_image)

    def get_new_path(self) -> str | None:
        """
        Get the selected file path.
        
        Returns:
            File path selected by user, or None if no file selected
        """
        return self.temp_file_path

    def clear(self) -> None:
        """
        Clear the preview image.
        """
        self.label_preview.configure(image=None)

    def set_total_width(self, total_width: int) -> None:
        """
        Set total width of image input for alignment.
        
        Creates an empty label to fill remaining width.
        
        Parameters:
            total_width: Total width in pixels
            
        Raises:
            ValueError: If total width is smaller than sum of components
        """
        # Wait for widgets to render
        self.update_idletasks()
        
        # Calculate widths
        label_width = self.label.winfo_width()
        label_asterisk_width = self.label_optional.winfo_width()
        label_preview_width = self.label_preview.winfo_width()
        button_width = self.button.winfo_width()
        empty_label_width = total_width - (label_width + label_preview_width + 
            label_asterisk_width + button_width + 25)

        if empty_label_width < 0:
            raise ValueError("total_width must be greater than sum of component widths.")

        # Create empty label for alignment
        empty_label = ctk.CTkLabel(
            self,
            text="",
            width=empty_label_width
        )
        empty_label.grid(row=0, column=4)

    def set_file_path(self, file_path: str) -> None:
        """
        Set file path and load preview.
        
        Parameters:
            file_path: Path to image file
        """
        self.temp_file_path = file_path
        self.show_preview()
        

class ClearSaveButtons(ctk.CTkFrame):
    """
    Frame with Clear and Save action buttons.
    """
    def __init__(
        self, root, btn_clear_function: Callable, 
        btn_save_function: Callable, **kwargs
    ):
        """
        Initialize button group.
        
        Parameters:
            root: Parent widget
            btn_clear_function: Callback for Clear button
            btn_save_function: Callback for Save button
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(fg_color="transparent")

        self.btn_clear_function = btn_clear_function
        self.btn_save_function = btn_save_function

        self.button_clear = ctk.CTkButton(
            self,
            text="Clear",
            fg_color=Colours.PRIMARY_WINE,
            text_color=Colours.BG_MAIN,
            font=Fonts.TEXT_MAIN,
            hover_color=Colours.BG_HOVER_BTN_CLEAR,
            corner_radius=Rounding.BUTTON,
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
            corner_radius=Rounding.BUTTON,
            state="disabled",
            command=self.save_on_click, 
        )
        
        self.button_clear.grid(
            row=0, column=0, padx=(0, Spacing.BUTTONS_X), pady=Spacing.BUTTONS_Y
        )
        self.button_save.grid(
            row=0, column=1, padx=Spacing.BUTTONS_X, pady=Spacing.BUTTONS_Y
        )

    def clear_on_click(self) -> None:
        """
        Execute Clear button callback.
        """
        self.btn_clear_function()

    def save_on_click(self) -> None:
        """
        Execute Save button callback.
        """
        self.btn_save_function()

    def enable_save_button(self) -> None:
        """
        Enable the Save button.
        """
        if self.button_save.cget("state") == "disabled":
            self.button_save.configure(state="normal", cursor="hand2")

    def disable_save_button(self) -> None:
        """
        Disable the save button.
        """
        self.button_save.configure(state="disabled", cursor="arrow")


class Card(ctk.CTkFrame):
    """
    Clickable card with image and title.
    """
    def __init__(
        self, root, title: str, image_path: str = "assets/cards/add_wine.png",
        on_click: Callable | None = None, **kwargs
    ):
        """
        Initialize card component.
        
        Parameters:
            root: Parent widget
            title: Card title text
            image_path: Path to card image
            on_click: Callback executed when card is clicked
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        # Frame
        self.configure(
            fg_color=Colours.BG_MAIN,
            border_width=1,
            border_color=Colours.BG_MAIN,
            corner_radius=Rounding.CARD,
            cursor="hand2",
            
        )
        self.on_click = on_click 
           
        # Create image button
        self.image = ctk.CTkButton(
            self,
            image=load_ctk_image(image_path, (150, 120)),
            text="",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            command=on_click,
        )

        # Create title button
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
        self.image.pack(padx=Spacing.LABELS_X, pady=Spacing.LABELS_Y)
        self.title.pack(padx=Spacing.LABELS_X, pady=(0, Spacing.LABELS_Y))

        # Add hover bindings
        self.add_binds()
       
    def add_binds(self) -> None:
        """
        Bind hover and click events to frame and children.
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
        Handle hover enter event.
        
        Parameters:
            event: Hover event (unused but required by bind)
        """
        self.configure(fg_color=Colours.BG_HOVER_NAV)
        for control in self.winfo_children():
            control.configure(fg_color=Colours.BG_HOVER_NAV)

    def frame_on_leave(self, event: tk.Event) -> None:
        """
        Handle hover leave event.
        
        Parameters:
            event: Hover event (unused but required by bind)
        """
        self.configure(fg_color=Colours.BG_MAIN)
        for control in self.winfo_children():
            control.configure(fg_color="transparent")


class NavLink(ctk.CTkButton):
    """
    Navigation link button with active state management.
    """
    def __init__(
        self, root, text: str = "", image: ctk.CTkImage | None = None, 
        command: Callable | None = None, **kwargs
    ):
        """
        Initialize navigation link.
        
        Parameters:
            root: Parent widget
            text: Link text
            image: Optional icon image
            command: Callback executed when clicked
            **kwargs: Additional CTkButton keyword arguments
        """
        super().__init__(root, **kwargs)
        self.configure(
            text=text,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.NAVLINK,
            image=image,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=Colours.BG_HOVER_NAV,
            corner_radius=Rounding.BUTTON,
            cursor="hand2",
            text_color_disabled=Colours.TEXT_MAIN,
            command=self.on_click
        )
        self.root = root
        self.callback = command

    def on_click(self) -> None:
        """
        Handle click event, updating active state and executing callback.
        """
        if self.callback is None:
            return

        # Deactivate other navlinks
        for widget in self.root.winfo_children():
            if isinstance(widget, NavLink) and widget.cget("state") == "disabled":
                widget.configure(
                    state="normal",
                    cursor="hand2",
                    font=Fonts.NAVLINK,
                    fg_color="transparent"
                )
        
        # Activate this navlink
        self.configure(
            state="disabled",
            cursor="arrow",
            font=Fonts.NAVLINK_ACTIVE,
            fg_color=Colours.BG_HOVER_NAV
        )

        self.callback()


class ButtonGoBack(ctk.CTkButton):
    """
    Button for navigating back to previous section.
    """
    def __init__(self, root, command: Callable, **kwargs):
        """
        Initialize go back button.
        
        Parameters:
            root: Parent widget
            command: Callback executed when clicked
            **kwargs: Additional CTkButton keyword arguments
        """
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
    Button displaying contextual menu with Show, Edit, and Delete actions.
    """
    def __init__(
        self, root, btn_name: str, on_show: Callable | None = None, 
        on_edit: Callable | None = None, on_delete: Callable | None = None, 
        **kwargs
    ):
        """
        Initialize action menu button.
        
        Parameters:
            root: Parent widget
            btn_name: Name used in menu action labels (e.g., "Wine", "Transaction")
            on_show: Callback for Show Details action
            on_edit: Callback for Edit action
            on_delete: Callback for Delete action
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(
            root, 
            fg_color="transparent", 
            cursor="hand2",
            **kwargs
        )

        # Callbacks
        self.btn_name = btn_name
        self.on_show = on_show
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.menu_visible = False
        self.menu_frame = None

        # Menu trigger button
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
        Toggle menu visibility.
        """
        if self.menu_visible:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self) -> None:
        """
        Create and display the contextual action menu.
        """
        self.menu_visible = True

        # Create menu container
        self.menu_frame = ctk.CTkFrame(
            self.winfo_toplevel(), # First Parent
            corner_radius=Rounding.FRAME,
            fg_color="white",
            border_color="#DDD",
            border_width=1
        )

        # Create action buttons
        if self.on_show:
            ctk.CTkButton(
                self.menu_frame,
                text="Show Details",
                image=Icons.SHOW,
                anchor="w",
                fg_color="transparent",
                text_color="black",
                hover_color="#F0E0E0",
                height=28,
                command=lambda: self._handle_action(self.on_show)
            ).pack(fill="x", padx=Spacing.BUTTONS_X, pady=(Spacing.BUTTONS_Y, 0))

        if self.on_edit:
            ctk.CTkButton(
                self.menu_frame,
                text=f"Edit {self.btn_name}",
                image=Icons.EDIT,
                anchor="w",
                fg_color="transparent",
                text_color="black",
                hover_color="#F0E0E0",
                height=28,
                command=lambda: self._handle_action(self.on_edit)
            ).pack(fill="x", padx=Spacing.BUTTONS_X, pady=Spacing.BUTTONS_Y)

        if self.on_delete:
            ctk.CTkButton(
                self.menu_frame,
                text=f"Delete {self.btn_name}",
                image=Icons.DELETE,
                anchor="w",
                fg_color="transparent",
                text_color="#C0392B",
                hover_color="#F8E5E5",
                height=28,
                command=lambda: self._handle_action(self.on_delete)
            ).pack(fill="x", padx=Spacing.BUTTONS_X, pady=(0, Spacing.BUTTONS_Y))

        # Position menu below button
        x = self.menu_button.winfo_rootx() - self.winfo_toplevel().winfo_rootx() - self.menu_button.winfo_width()
        y = self.menu_button.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + 30
        
        self.menu_frame.place(x=x, y=y)
        self.menu_frame.lift()

        # Bind click outside handler
        self.winfo_toplevel().bind("<Button-1>", self._check_click_outside, add="+")

    def hide_menu(self) -> None:
        """
        Destroy the menu if it exists.
        """
        if self.menu_frame:
            self.menu_frame.destroy()
            self.menu_frame = None
            self.menu_visible = False

            # Unbind click event
            try:
                self.winfo_toplevel().unbind("<Button-1>")
            except:
                pass

    def _handle_action(self, callback: Callable | None) -> None:
        """
        Execute action callback and close menu.
        
        Parameters:
            callback: Action callback function
        """
        self.hide_menu()
        if callback:
            callback()

    def destroy(self) -> None:
        """
        Destroy menu and frame.
        """    
        self.hide_menu()
        super().destroy()

    def _check_click_outside(self, event: tk.Event) -> None:
        """
        Check if click was outside menu and close if so.
        
        Parameters:
            event: Click event
        """
        if not self.menu_visible:
            return
            
        # Get clicked widget
        widget = event.widget
        
        # Check if click was inside menu or button
        is_inside_menu = False
        is_inside_button = False
        
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