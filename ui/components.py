"""
Custom components useful for the app
"""
import customtkinter as ctk
import tkinter as tk
import re
from decimal import Decimal

from ui.style import Colours, Fonts, Icons
from helpers import load_ctk_image


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
            root, 
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
            root, 
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
      

class TextInput(ctk.CTkFrame):
    """
    A frame that contains a label and an entry components
    """
    def __init__(
        self, root, label_text: str, placeholder: str | None = None, 
        optional: bool = False,
        **kwargs
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

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            placeholder_text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_MAIN,
            width=300
        )
        
        # Place components
        self.label.grid(row=0, column=0, sticky="w") 
        self.label_optional.grid(row=0, column=1, padx=(0, 10))
        self.entry.grid(row=0, column=2)

    def clear(self):
        """Removes the text typed by the user"""
        self.entry.delete(0, "end") 

    def get(self):
        """Returns the value (Text) of Entry"""
        return self.entry.get()

class IntInput(ctk.CTkFrame):
    """
    A frame that contains a label and an integer entry components
    """
    def __init__(
        self, root, label_text: str, placeholder: str | None = None, from_=None,
        to=None, optional: bool = False, textvariable=None, **kwargs
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

        self.int_entry = IntEntry(
            self,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            from_=from_,
            to=to,
            textvariable=textvariable
        )
        
        # Place components
        self.label.grid(row=0, column=0, sticky="w") 
        self.label_optional.grid(row=0, column=1, padx=(0, 10))
        self.int_entry.grid(row=0, column=2)

    def clear(self):
        """Removes the text typed by the user"""
        self.int_entry.delete(0, "end") 

    def get(self):
        """Returns the value (integer) of IntEntry"""
        return self.int_entry.get()


class DecimalInput(ctk.CTkFrame):
    """
    A frame that contains a label and an decimal entry components
    """
    def __init__(
        self, root, label_text: str, placeholder: str | None = None, from_=None,
        to=None, optional: bool = False, textvariable=None, **kwargs
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

        self.decimal_entry = DecimalEntry(
            self,
            text_color=Colours.TEXT_MAIN, 
            font=Fonts.TEXT_MAIN,
            width=150,
            from_=from_,
            to=to,
            textvariable=textvariable
        )
        
        # Place components
        self.label.grid(row=0, column=0, sticky="w") 
        self.label_optional.grid(row=0, column=1, padx=(0, 10))
        self.decimal_entry.grid(row=0, column=2)

    def clear(self):
        """Removes the text typed by the user"""
        self.decimal_entry.delete(0, "end") 

    
    def get(self):
        """Returns the value (decimal) of DecimalEntry"""
        return self.decimal_entry.get()


class DropdownInput(ctk.CTkFrame):
    """
    A frame that contains a label and a dropdown components
    """
    def __init__(
        self, root, label_text: str, values: list[str], variable = None, 
        command = None, placeholder: str | None = None, optional: bool = False, 
        **kwargs
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
            command=command
        )
        
        # Place components
        self.label.grid(row=0, column=0, sticky="w")
        self.label_optional.grid(row=0, column=1, padx=(0, 10))
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
            font=Fonts.TEXT_MAIN,
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


class ImageInput(ctk.CTkFrame):
    """
    A frame that contains a text label, filedialog button, and image label components
    """
    def __init__(
        self, root, label_text: str, image_path: str | None = None, 
        placeholder: str | None = None, optional: bool = False, **kwargs
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
        self.label.grid(row=0, column=0, sticky="w")
        self.label_optional.grid(row=0, column=1, padx=(0, 15))
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



class Card(ctk.CTkFrame):
    """
    A card that contains a picture, a title, and a description
    """

    def __init__(
        self, root, title: str, image_path: str ="assets/cards/add_wine.png", description: str | None = None,
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

        # Add description (opt)
        if description:
            self.description = ctk.CTkLabel(
                self,
                text=description,
                text_color=Colours.TEXT_SECONDARY,
                font=Fonts.TEXT_SECONDARY,
                hover_color=Colours.BG_HOVER_NAV,
                command=on_click 
            )
            self.description.pack(pady=5)

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

