"""
Mixins for adding features to table components.

This module provides reusable mixins that can be added to table classes
to extend their functionality with sorting, filtering, and other features.
"""
import customtkinter as ctk
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Callable


class SortMixin(ABC):
    """
    Mixin adding column sorting capabilities to tables.
    
    Provides methods for sorting table data by column with visual indicators
    (arrows) showing sort direction. Supports toggling between ascending and
    descending order.
    
    Requirements:
        - Class must define filtered_lines: list
        - Class must define header_labels: list[ctk.CTkLabel]
        - Class must implement get_sorting_keys()
    """
    def setup_sorting(self) -> None:
        """
        Initialize sorting state variables.
        
        Call this in the table's __init__ after headers are created.
        """
        self.sort_reverse: bool = False
        self.last_sort: int | None = None
        self.sorting_keys: dict[int, Callable] = self.get_sorting_keys()
     
    @abstractmethod
    def get_sorting_keys(self) -> dict[int, Callable]:
        """
        Get sorting key functions for each sortable column.
        
        Returns dictionary mapping column indices to functions that extract
        the sort key from a row object.
        
        Returns:
            Dictionary where keys are column indices and values are callables
            that take a row object and return a sortable value
            
        Example:
            {
                0: lambda row: row.name,
                1: lambda row: row.date,
                2: lambda row: row.quantity
            }
        """        
        raise NotImplementedError("Subclasses must implement get_sorting_keys()")
    
    def sort_table(self, event: tk.Event, col_index: int) -> None:
        """
        Sort table by column when header is clicked.
        
        Parameters:
            event: Click event from header label
            col_index: Index of clicked column header
        """
        # Get label that was clicked
        event_label = event.widget.master

        # Verify click was within label bounds (prevent edge case issues)
        if not (
            0 <= event.x <= event_label.winfo_width() and 
            0 <= event.y <= event_label.winfo_height()
        ):
            return
        
        # Update arrow indicators and perform sort
        self.clean_arrows(event_label)
        self.sort_by(col_index)

    def clean_arrows(self, event_label: ctk.CTkLabel) -> None:
        """
        Clear sort arrows from all headers and add arrow to clicked header.
        
        Arrow indicators: ↑ = ascending order, ↓ = descending order
        
        Parameters:
            event_label: Header label that was clicked
        """
        # Remove arrows from clicked label
        clean_text = event_label.cget("text").replace("↑", "").replace("↓", "")
        
        # Remove arrows from all header labels
        for lbl in self.header_labels:
            lbl_text = lbl.cget("text").replace("↑", "").replace("↓", "")
            lbl.configure(text=lbl_text)

        # Add arrow to clicked label based on sort direction
        arrow = "↓" if self.sort_reverse else "↑"
        event_label.configure(text=clean_text + arrow)
    
    def sort_by(self, col_index: int, new_sort: bool = True) -> None:
        """
        Sort filtered lines by specified column.
        
        Parameters:
            col_index: Index of column to sort by
            new_sort: If True, toggle sort direction; if False, keep current direction
        """
        # Skip if column is not sortable
        if col_index not in self.sorting_keys or not self.sorting_keys[col_index]:
            return
        
        # Determine sort direction
        reverse = self.sort_reverse if new_sort else not self.sort_reverse
        
        # Sort the filtered data
        self.filtered_lines.sort(
            key=self.sorting_keys[col_index], reverse=reverse
        )
        
        # Update sort state
        if new_sort:
            self.sort_reverse = not self.sort_reverse
            self.last_sort = col_index  