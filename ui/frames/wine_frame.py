"""
Classes related with the wine section
"""

import customtkinter as ctk

from ui.components import Card, ButtonGoBack
from ui.forms.add_wine import AddWineForm
from ui.forms.manage_wine import ShowWineForm
from ui.style import Colours, Fonts
from db.models import Wine

class WineFrame(ctk.CTkScrollableFrame):
    """
    It contains all the components and logic related to wine CRUD
    """
    def __init__(self, root: ctk.CTkFrame, session, main_window, **kwargs):
        super().__init__(root, **kwargs)
        self.configure(
            fg_color = Colours.BG_SECONDARY,
            corner_radius=10,
            border_color=Colours.BORDERS,
            border_width=1,
        )
        self.session = session
        self.wine = session.query(Wine)
        self.main_window = main_window
        self.button_go_back = None
        self.create_components()
        
    def create_components(self) -> None:
        """
        Creates the wine section components
        """
        # Title
        title = ctk.CTkLabel(
            self,
            text="WINES",
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.TITLE
        )
        title.pack(pady=(20, 0))

        # Introduction
        text_intro = (
            "Add, edit, or remove wines from your winery's catalog to "
            + "keep your selection up to date."
        )
        introduction = ctk.CTkLabel(
            self,
            text=text_intro,
            text_color=Colours.TEXT_SECONDARY,
            justify="center",
            font=Fonts.TEXT_SECONDARY
        )
        introduction.pack(pady=15)
        
        # Frame cards
        frame_cards = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=10,
        )
        frame_cards.pack(pady=15)
        
        card_list = Card(
            frame_cards,
            image_path="assets/cards/wine_list.png",
            title="Manage Wine",
            on_click=self.manage_wine_section,
        )
        card_add = Card(
            frame_cards,
            title="Add Wine",
            image_path="assets/cards/add_wine2.png",
            on_click=self.show_add_wine_section,
        )
        card_edit = Card(
            frame_cards,
            image_path="assets/cards/coming_soon.png",
            title="Edit Wine",
            on_click=None,
        )


        # Place cards
        card_list.grid(row=0, column=0, pady=(0, 15))
        card_add.grid(row=0, column=1)
        card_edit.grid(row=1, column=0, padx=20)
        
    
    def show_subsection(self, text_title: str, form_class, **kwargs):
        """
        Clears body and display a subsection.
        Parameters:
            - text_title: Title of the section
            - form_class: Form to be displayed
            - kwargs: Additional arguments from the forms
        """
        # Clean previous menu
        self.clear_content()

        # Vertical expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add Go back button
        self.button_go_back = ButtonGoBack(
            self.main_window.root,
            command=self.main_window.show_wine_section
        )

        # Add title
        title = ctk.CTkLabel(
            self,
            text=text_title,
            text_color=Colours.PRIMARY_WINE,
            font=Fonts.SUBTITLE,
        )

        # Place button and title
        x = self.winfo_rootx() - self.main_window.root.winfo_rootx()
        y = self.winfo_rooty() - self.main_window.root.winfo_rooty()
        
        self.button_go_back.place(x=x, y=y)
        title.grid(row=0, column=0, pady=(20, 0), sticky="n")

        # Add form
        form = form_class(
            self,
            self.session,
            fg_color=Colours.BG_SECONDARY,
            **kwargs
        )
        form.grid(row=1, column=0, pady=(10, 0), sticky="nsew") 


    def show_add_wine_section(self) -> None:
        """
        Shows the form for adding a wine.
        """
        self.show_subsection(
            "ADD WINE",
            AddWineForm
        )
    
    def manage_wine_section(self) -> None:
        """
        Shows the form for removing a wine.
        """
        self.show_subsection(
            "WINE LIST",
            ShowWineForm,
        )
    
    def clear_content(self) -> None:
        """
        Removes any content in wine frame
        """
        for component in self.winfo_children():
            component.destroy()

    def destroy(self) -> None:
        """
        Override function to include the destruction of the button go back.
        """
        if self.button_go_back:
            self.button_go_back.destroy()
        super().destroy()

        
        