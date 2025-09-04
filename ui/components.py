"""
Custom components useful for the app
"""
import customtkinter as ctk
import tkinter as tk
from decimal import Decimal
from typing import Callable

from helpers import load_ctk_image, resource_path
from models import Wine
from ui.style import Colours, Fonts, Icons


class TextEntry(ctk.CTkEntry):
    """
    Entry component with a max_length validation
    """
    def __init__(self, root, max_len: int = 60, **kwargs):
        super().__init__(root, **kwargs)
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
        return len(text) <= self.max_len





class IntEntry(ctk.CTkEntry):
    """
    Entry component that only accepts integers.
    """
    def __init__(self, root, from_: int = None, to: int = None, 
        textvariable = None, **kwargs):
        super().__init__(root, **kwargs)
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
        After typing, it check if the text is an integer between min and max.

        Input:
            text: Text typed by the user
        Returns:
            True: The text is valid and in range
            False: The text is invalid or out of range
        """
        if text =="":
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
    Entry component that accepts decimal values.
    """
    """
    Entry component that only accepts integers.
    """
    def __init__(self, root, from_: int = None, to: int = None, 
        textvariable = None, **kwargs
    ):
        super().__init__(root, **kwargs)
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
        After typing, it check if the text is a decimal number between min and max.

        Input:
            text: Text typed by the user
        Returns:
            True: The text is valid and in range
            False: The text is invalid or out of range
        """
        
        if text == "" :
            return True
        # Reject letters and extra points
        if text.isalpha() or text.count('.') > 1:
            return False
        # Accept a dot, but don't convert to decimal yet
        if text[-1] == ".":
            return True
        # Catch other weird symbols
        try:   
            number = Decimal(text)
        except:
            return False
        
        # Number is lower than min
        if self.min_val and number < self.min_val:
            return False
        # Number is higher than max
        if self.max_val and number > self.max_val:
            return False
        # Number is in range
        return True


class AutocompleteEntry(ctk.CTkEntry):
    """
    An entry that contains an autocomplete feature according to the wine list.
    Autcomplete is formed by a frame that contains a listbox.
    """
    def __init__(self, root, wine_list, **kwargs):
        super().__init__(root, **kwargs)
        self.root = root
        self.wine_list = wine_list
        self.listbox = None
        self.listbox_frame = None
        self.main_window = self.winfo_toplevel()
        
        self.bind("<KeyRelease>", self.show_suggestions)
        self.bind("<Button-1>", self.show_suggestions)

    def on_click_outside(self, event):
        """Clicks out of the inbox and entry"""
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
            
            # check if the click was in the listbox
            if self.listbox_frame and self.listbox_frame.winfo_exists():
                listbox_x = self.listbox_frame.winfo_rootx()
                listbox_y = self.listbox_frame.winfo_rooty()
                listbox_width = self.listbox_frame.winfo_width()
                listbox_height = self.listbox_frame.winfo_height()
                
                in_listbox = (listbox_x <= x <= listbox_x + listbox_width and 
                            listbox_y <= y <= listbox_y + listbox_height)
            else:
                in_listbox = False
            
            # destroy listbox if not in entry or listbox
            if not in_entry and not in_listbox:
                self.destroy_listbox()

    def show_suggestions(self, event=None):
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
        

    def select_suggestion(self, event):
        """
        Get the selected element from listbox and update entry.
        """
        if self.listbox and self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            # Clean entry 
            self.delete(0, tk.END) 
            # Add selected suggestion in entry
            self.insert(0, selected)
            # Clean listbox
            self.destroy_listbox()
    
    def select_on_click(self, event):
        """Select with one click"""
        # Get index of the clicked event
        index = self.listbox.nearest(event.y)
        if index >= 0:
            # Clear previous selections
            self.listbox.selection_clear(0, tk.END)
            # Set current selection
            self.listbox.selection_set(index)
            self.select_suggestion(event)
    
    def destroy_listbox(self):
        """Destroy listbox and its frame"""
        if self.listbox_frame:
            self.main_window.unbind("<Button-1>")
            
            self.listbox_frame.destroy()
            self.listbox_frame = None
            self.listbox = None

    def destroy(self):
        """
        Destroys the entry with the listbox if exists.
        """
        self.destroy_listbox()
        super().destroy()


class BaseInput(ctk.CTkFrame):
    """
    A frame that contains 2 labels (name and *), used as base for inputs with
    entries
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
            width=100
        )

        self.asterisk = "*" if not optional else ""
        self.label_optional = ctk.CTkLabel(
            self,
            text=self.asterisk,
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TEXT_LABEL,
        )
        
        # Place components
        self.label.grid(row=0, column=0, sticky="w") 
        self.label_optional.grid(row=0, column=1, padx=(0, 10))

class TextInput(BaseInput):
    """
    A frame that contains a label and an entry components
    """
    def __init__(self, root, placeholder: str | None = None, max_len: int = 60, 
        **kwargs):
        
        super().__init__(root, **kwargs)
        
        self.entry = TextEntry(
            self,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN,
            placeholder_text=placeholder,
            placeholder_text_color=Colours.TEXT_SECONDARY,
            font=Fonts.TEXT_MAIN,
            width=300,
            max_len = max_len
        )
        
        # Place components
        self.entry.grid(row=0, column=2)

    def clear(self):
        """Removes the text typed by the user"""
        self.entry.delete(0, "end") 

    def get(self):
        """Returns the value (Text) of Entry"""
        return self.entry.get()

class IntInput(BaseInput):
    """
    A frame that contains a label and an integer entry components
    """
    def __init__(
        self, root, placeholder: str | None = None, from_: int = None,
        to: int | None = None, textvariable=None, **kwargs
    ):
        super().__init__(root, **kwargs)

        self.int_entry = IntEntry(
            self,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            from_=from_,
            to=to,
            textvariable=textvariable
        )
        
        # Place components
        self.int_entry.grid(row=0, column=2)

    def clear(self):
        """Removes the text typed by the user"""
        self.int_entry.delete(0, "end") 

    def get(self):
        """Returns the value (integer) of IntEntry"""
        return self.int_entry.get()


class DecimalInput(BaseInput):
    """
    A frame that contains a label and an decimal entry components
    """
    def __init__(
        self, root, placeholder: str | None = None, from_: int | None = None,
        to: int | None =None, textvariable=None, **kwargs
    ):
        super().__init__(root, **kwargs)

        self.decimal_entry = DecimalEntry(
            self,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            from_=from_,
            to=to,
            textvariable=textvariable
        )
        
        # Place components
        self.decimal_entry.grid(row=0, column=2)

    def clear(self):
        """Removes the text typed by the user"""
        self.decimal_entry.delete(0, "end") 

    
    def get(self):
        """Returns the value (decimal) of DecimalEntry"""
        return self.decimal_entry.get()

class AutoCompleteInput(BaseInput):
    """
    A frame that contains a label and an AutoComplete entry components
    """
    def __init__(
        self, root, placeholder: str | None = None, textvariable=None, 
        wine_list=list[Wine], **kwargs
    ):
        super().__init__(root, **kwargs)

        self.autocomplete_entry = AutocompleteEntry(
            self,
            wine_list=wine_list,
            fg_color=Colours.BG_SECONDARY,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            textvariable=textvariable,
        )
        
        # Place components
        self.autocomplete_entry.grid(row=0, column=2)

    def clear(self):
        """Removes the text typed by the user"""
        self.autocomplete_entry.delete(0, "end") 


class DropdownInput(BaseInput):
    """
    A frame that contains a label and a dropdown components
    """
    def __init__(
        self, root, values: list[str], variable = None, command = None, 
        placeholder: str | None = None, **kwargs
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
    
    def get(self):
        """Returns the selected value of DropDown"""
        return self.dropdown.get()

    def update_values(self, values: list) -> None:
        """
        Updates the available values of the dropdown.

        Inputs:
            Values: New list of values that will be available in the dropdown
        """
        self.dropdown.configure(values=values)

   
class DoubleLabel(ctk.CTkFrame):
    """
    A frame that contains a label for title and a label for showing a value
    """
    def __init__(
        self, root, label_title_text: str, label_value_text: str = "",  
        text_variable: str | None = None, **kwargs
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
        Update the text of the label_value.

        Inputs:
            New Text = New text to include in label_value.
        """
        self.label_value.configure(
            text=new_text
        )


class ImageInput(BaseInput):
    """
    A frame that contains a text label, filedialog button, and image label components
    """
    def __init__(
        self, root, image_path: str | None = None, placeholder: str | None = None, 
        **kwargs
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
            fg_color=Colours.BG_MAIN,               
        )
        
        self.temp_file_path = None

        # Place components
        self.button.grid(row=0, column=2, padx=15)
        self.label_preview.grid(row=0, column=3, padx=(15, 0))

    def load_logo(self) -> None:
        """
        Show filedialog to user, and show a preview
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
        Returns temp_file_path if the user picked one, else None.
        """
        return self.temp_file_path

    def clear(self):
        """Sets the preview image to None"""
        self.label_preview.configure(
            image=None
        )

class ClearSaveButtons(ctk.CTkFrame):
    """
    A frame with clear and save buttons
    """
    def __init__(self, root, btn_clear_function, btn_save_function, **kwargs):
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

    def clear_on_click(self):
        """
        Execute callback function for clear button
        """
        self.btn_clear_function()

    def save_on_click(self):
        """
        Execute callback function for save button
        """
        self.btn_save_function()

    def enable_save_button(self):
        """
        Enables save button
        """
        if self.button_save.cget("state") == "disabled":
            self.button_save.configure(state="normal", cursor="hand2")

    def disable_save_button(self):
        """
        Disables save button
        """
        self.button_save.configure(state="disabled", cursor="arrow")


class Card(ctk.CTkFrame):
    """
    A card that contains a picture, a title, and a description
    """

    def __init__(
        self, root, title: str, image_path: str ="assets/cards/add_wine.png",
        on_click=None, **kwargs
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
       
    def add_binds(self):
        """
        Add bind to the components to work as a one thing
        """
        if self.on_click:
            self.bind("<Button-1>", self.frame_clicked)
        for control in self.winfo_children():
            control.bind("<Enter>", self.frame_on_enter)
            control.bind("<Leave>", self.frame_on_leave)

    def frame_clicked(self, event):
        """
        Click event triggered: Callback
        """
        self.on_click()

    def frame_on_enter(self, event):
        """
        Hover on enter event trigered: Change hover color
        """
        self.configure(fg_color=Colours.BG_HOVER_NAV)
        for control in self.winfo_children():
            control.configure(fg_color=Colours.BG_HOVER_NAV)

    def frame_on_leave(self, event):
        """
        Hover on leave event trigered: Change hover colour
        """
        self.configure(fg_color=Colours.BG_MAIN)
        for control in self.winfo_children():
            control.configure(fg_color="transparent")


class NavLink(ctk.CTkButton):
    """
    A button that works as a navigator link.
    """
    def __init__(
        self, root, text: str = "", image: ctk.CTkImage = None, 
        command: Callable = None, **kwargs
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

    def on_click(self):
        """Disable active button and execute callback"""
        
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
    """ Button to go back to the precious section"""
    def __init__(self, root, command, **kwargs):
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
        