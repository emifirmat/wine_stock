"""
Wine form for adding and editing wine records.

This module provides a comprehensive form for creating new wines or editing
existing wine records, including validation, image upload, and database
persistence with proper error handling.
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Callable, Any

from db.models import Wine, Colour, Style, Varietal
from helpers import deep_getattr
from ui.components import (TextInput, IntInput, DropdownInput, ImageInput,
    DecimalInput, ClearSaveButtons)
from ui.style import Colours, Fonts, Spacing
from validators import (
    validate_string, validate_dropdown, validate_year, validate_int, 
    validate_decimal
)


class AddWineForm(ctk.CTkFrame):
    """
    Form for adding or editing wine records.
    
    Provides inputs for all wine attributes including name, winery,
    characteristics, pricing, and stock levels. Supports both creation
    and editing modes with full validation.
    """
    def __init__(
        self, root: ctk.CTkFrame, session: Session, wine: Wine | None = None, 
        on_save: Callable | None = None, **kwargs
    ):
        """
        Initialise wine form in add or edit mode.
        
        Parameters:
            root: Parent frame container
            session: SQLAlchemy database session
            wine: Existing Wine instance for edit mode, None for add mode
            on_save: Callback executed after saving with Wine instance
            **kwargs: Additional CTkFrame keyword arguments
        """
        super().__init__(root, **kwargs)
        
        # DB instances
        self.session = session
        self.wine = wine
        self.on_save = on_save

        # Lookup dictionaries
        self.wine_colours_dict = self.get_wine_colours_dict()
        self.wine_styles_dict = self.get_wine_style_dict()
        
        # Components
        self.label_error = None
        self.inputs_dict = self.create_components()

    def create_components(self) -> dict[str, ctk.CTkBaseClass]:
        """
        Create and position all form inputs and buttons.
        
        Returns:
            Dictionary of input widgets keyed by field name
        """
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Create background frame
        frame_background = ctk.CTkFrame(self, fg_color = Colours.BG_FORM)
        frame_background.grid(
            row=1, column=0, 
            padx=Spacing.SECTION_X, pady=Spacing.SECTION_Y
        )
        frame_background.grid_columnconfigure(0, weight=1)

        # Create input components
        name = TextInput(frame_background, label_text="Name")
        
        winery = TextInput(frame_background, label_text="Winery")
        
        colour = DropdownInput(
            frame_background,
            label_text="Colour",
            values=[""] + list(self.wine_colours_dict.keys())
        )
        
        style = DropdownInput(
            frame_background,
            label_text="Style",
            values=[""] + list(self.wine_styles_dict.keys())
        )
        
        varietal = DropdownInput(
            frame_background,
            label_text="Varietal",
            values=[""] + [v.name.title() for v in self.session.query(Varietal).all()],
            optional=True
        )
        
        vintage_year = IntInput(
            frame_background,
            label_text="Vintage Year",
            from_=0,
            to=datetime.now().year
        )
        
        origin = TextInput(
            frame_background,
            label_text="Origin",
            optional=True
        )
        
        code = TextInput(frame_background, label_text="Code")
        
        wine_picture = ImageInput(
            frame_background,
            label_text="Wine Picture",
            optional=True
        )
        
        quantity = IntInput(
            frame_background,
            label_text="Stock" if self.wine else "Initial Stock",
            placeholder="In bottles",
        )
        
        min_stock = IntInput(
            frame_background,
            label_text="Min. Stock",
            placeholder="In bottles",
            optional=True
        )
        
        purchase_price = DecimalInput(
            frame_background,
            label_text="Purchase Price",
        )

        selling_price = DecimalInput(
            frame_background,
            label_text="Selling Price"
        )

        inputs_dict = {
            "name": name, 
            "winery": winery, 
            "colour.name": colour, 
            "style.name": style, 
            "varietal.name": varietal, 
            "vintage_year": vintage_year, 
            "origin": origin, 
            "code": code,
            "picture_path": wine_picture,
            "quantity": quantity,
            "min_stock": min_stock,
            "purchase_price": purchase_price,
            "selling_price": selling_price
        }

        # Position all inputs
        for index, input in enumerate(inputs_dict.values()):
            input.set_total_width(450)
            input.grid(
                row=index, column=0, 
                padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y
            )
                   
        # Create error message label
        self.label_error = ctk.CTkLabel(
            frame_background,
            fg_color="transparent",
            text="",
            text_color=Colours.ERROR,
            font=Fonts.TEXT_ERROR,
            width=450,
        )
        self.label_error.grid(
            row=len(inputs_dict), column=0, 
            padx=Spacing.LABEL_X, pady=Spacing.LABEL_Y)

        # Create action buttons
        frame_buttons = ClearSaveButtons(
            frame_background,
            btn_clear_function=self.on_click_clear,
            btn_save_function=self.save_values
        )
        frame_buttons.enable_save_button()
        frame_buttons.grid(
            row=len(inputs_dict) + 1, column=0, 
            padx=Spacing.SUBSECTION_X, pady=Spacing.SUBSECTION_Y
        )

        # Load existing data if in edit mode
        if self.wine:
            self.set_edition_mode(inputs_dict)
        
        return inputs_dict
    
    def get_wine_colours_dict(self) -> dict[str, Colour]:
        """
        Get dictionary of wine colours mapped to Colour instances.
        
        Returns:
            Dictionary with colour names (title case) as keys and Colour instances as values
        """
        wine_colours = self.session.query(Colour).all()
        return {colour.name.title(): colour for colour in wine_colours}

    def get_wine_style_dict(self) -> dict[str, Style]:
        """
        Get dictionary of wine styles mapped to Style instances.
        
        Returns:
            Dictionary with style names (title case) as keys and Style instances as values
        """
        wine_styles = self.session.query(Style).all()
        return {style.name.title(): style for style in wine_styles}

    def on_click_clear(self) -> None:
        """
        Ask for confirmation before clearing all inputs.
        """
        confirm_dialog = messagebox.askyesno(
                "Confirm",
                "Clearing the form will discard all current inputs. Continue?"
            )
        if confirm_dialog:
           self.clear_inputs()

    def clear_inputs(self) -> None: 
        """
        Clear all input fields, resetting dropdowns to first value.
        """
        for input_widget in self.inputs_dict.values():         
            if isinstance(input_widget, DropdownInput):
                input_widget.set_to_first_value()
            else:    
                input_widget.clear()

    def save_values(self) -> None:
        """
        Validate and save wine to database.
        
        Handles both creation and update modes, with validation, confirmation 
        dialogs, and proper error handling for database constraints.
        """
        # Validate all inputs
        wine_attributes = self.validate_inputs()
        if not wine_attributes:
            return
        
        self.label_error.configure(text="")

        # Warn if purchase price exceeds selling price
        if wine_attributes["purchase_price"] > wine_attributes["selling_price"]:
            save_message = (
                "The Purchase Price is higher than the Selling Price. " 
                "Do you want to save this wine?"
            )
        else:
            save_message = "Do you want to save this wine?"
        
        # Confirm save
        confirm_dialog = messagebox.askyesno("Confirm", save_message)
        if not confirm_dialog:
            return

        # Convert dropdown values to model instances
        wine_attributes["colour"] = Colour.get_name(
            self.session, name=wine_attributes["colour"]
        )
        wine_attributes["style"] = Style.get_name(
            self.session, name=wine_attributes["style"]
        )
        wine_attributes["varietal"] = Varietal.get_name(
            self.session, name=wine_attributes["varietal"]
        ) if wine_attributes["varietal"] else None
        
        try:
            if self.wine:
                # Update existing wine
                for attr, val in wine_attributes.items():
                    setattr(self.wine, attr, val)
            else:
                # Create new wine
                new_wine = Wine(**wine_attributes)
                self.session.add(new_wine)
        except TypeError as e:
            messagebox.showerror(
                "Error Saving",
                "Couldn't save the wine. Please contact the administrator. (code=1)"
            )
            print(f"TypeError: {e}")
            return

        # Commit to database
        try:
            self.session.commit()
        except IntegrityError as e:
            # Rollback failed transaction
            self.session.rollback()

            # Handle constraint violations
            error_msg = str(e.orig)
            if "UNIQUE constraint failed" in error_msg:
                self.label_error.configure(
                    text="The code already exists. Please choose another one."
                )
            else:
                messagebox.showerror(
                    "Error Saving",
                    "Couldn't save the wine. Please contact the administrator. (code=2)"
                )
                print(f"IntegrityError: {error_msg}")     
            return

        # Show success message
        messagebox.showinfo(
            "Wine Saved",
            "The wine has been successfully saved."
        )

        # Handle post-save actions
        if self.wine:
            # Edit mode: refresh parent view and close
            if self.on_save:
                self.on_save(self.wine)
            self.winfo_toplevel().destroy()
        else:
            # Add mode: clear form for next entry
            self.clear_inputs()
    
    def validate_inputs(self) -> dict[str, Any] | None:
        """
        Validate all input fields.
        
        Returns:
            Dictionary of validated field values, or None if validation fails
        """
        try:
            return {
                "name": validate_string("name", self.inputs_dict["name"].get()),
                "winery": validate_string("winery", self.inputs_dict["winery"].get()),
                "colour": validate_dropdown("colour", self.inputs_dict["colour.name"].get()),
                "style": validate_dropdown("style", self.inputs_dict["style.name"].get()),
                "varietal": self.inputs_dict["varietal.name"].get().lower(), # Optional           
                "vintage_year": validate_year("vintage year", self.inputs_dict["vintage_year"].get()),
                "origin": self.inputs_dict["origin"].get().strip(), # Optional
                "code": validate_string("code", self.inputs_dict["code"].get()),
                "picture_path": self.inputs_dict["picture_path"].get_new_path(), # Optional
                "quantity": validate_int(
                    "initial stock", self.inputs_dict["quantity"].get(), 
                    allowed_signs="positive"
                ),
                "min_stock": self.inputs_dict["min_stock"].get(),
                "purchase_price": validate_decimal(
                    "purchase price", self.inputs_dict["purchase_price"].get()
                ),
                "selling_price": validate_decimal(
                    "selling price", self.inputs_dict["selling_price"].get()
                )
            }
        
        except ValueError as ve:
            # Display validation error
            self.label_error.configure(text=str(ve))
            return None
        
    def set_edition_mode(self, inputs_dict: dict[str, ctk.CTkBaseClass]) -> None:
        """
        Populate form inputs with existing wine data for editing.
        
        Parameters:
            inputs_dict: Dictionary of input widgets to populate
        """
        for input_name, input_widget in inputs_dict.items():
            # Get value from wine instance
            value = deep_getattr(self.wine, input_name)
            
            # Populate based on input type
            if isinstance(input_widget, DropdownInput):
                input_widget.set_to_value(value)
            elif isinstance(input_widget, ImageInput):
                input_widget.set_file_path(value)
            else:
                # Text and numeric inputs
                input_widget.update_text_value(
                    new_text=value if value is not None else ""
                )