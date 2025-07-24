"""
Custom components useful for the app
"""
import customtkinter as ctk

from ui.style import Colours, Fonts, Icons


class TextInput(ctk.CTkFrame):
    """
    A frame that contains a label and an entry components
    """
    def __init__(self, root, label_text: str, placeholder: str | None = None, **kwargs):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color="transparent",
        )
        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            text_color=Colours.TEXT_MAIN,
            font=Fonts.TEXT_MAIN,
            width=100
        )
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            placeholder_text_color=Colours.TEXT_SECONDARY,
            font=Fonts.TEXT_MAIN,
            width=300
        )
        
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="w") 
        self.entry.grid(row=0, column=1)


class Card(ctk.CTkFrame):
    """
    A card that contains a picture, a title, and a description
    """

    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color="transparent",
        )