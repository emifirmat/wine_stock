"""
Classes to add features to the tables
"""
import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Callable, List, Dict


class SortMixin(ABC):
    """
    Mixin to add sorting capabilities to a table.

    Requirements:
        - The class must define filtered_lines: list
        - The class must define `header_labels: list[ctk.CTkLabel]`
        - Must implement get_sorting_keys()
    """
    def setup_sorting(self):
        """
        Call this in the table's __init__ after headers are set.
        """
        # Sorting data
        self.sort_reverse: bool = False
        self.last_sort: int | None = None
        self.sorting_keys: Dict[int, Callable] = self.get_sorting_keys()
     
    @abstractmethod
    def get_sorting_keys(self) -> Dict[int, Callable]:
        """
        Returns a dict of int-callables, one per column, to be used as sorting keys.
        Example: [1: lambda row: row.name, 2: lambda row: row.date]
        """        
        raise NotImplementedError
    
    def sort_table(self, event, col_index: int):
        """
        Sort triggered from a UI event.
        Parameters:
            - event: Triggered UI event
            - col_index: Index of the clicked header
            - headers: header labels that can be used for sorting
        """
        # Get ctkLabel of the clicked header
        event_label = event.widget.master

        # Prevents an error when user click on label but not on the text
        if (not (
            0 <= event.x <= event_label.winfo_width() 
            and 0 <= event.y <= event_label.winfo_height()
        )):
            return
        
        # Clean arrows and sort
        self.clean_arrows(event_label)
        self.sort_by(col_index)

    def clean_arrows(self, event_label: ctk.CTkLabel):
        """
        Clears the arrows in all the headers and set a new one for the clicked
        one. ↑ means sorted in ascending order, ↓ means sorted in descending order.
        Parameters:
            - event: Triggered UI event
            - col_index: Index of the clicked header
            - headers: header labels that can be used for sorting
        """
        # Ignore picture header
        clean_text = event_label.cget("text").replace("↑", "").replace("↓", "")
        
        # Clean arrow in all labels
        for lbl in self.header_labels:
            lbl_text = lbl.cget("text").replace("↑", "").replace("↓", "")
            lbl.configure(text=lbl_text)

        # Add arrow depending on order
        arrow = "↓" if self.sort_reverse else "↑"
        event_label.configure(text=clean_text + arrow)
    
    def sort_by(self, col_index: int, new_sort: bool = True):
        """
        Order lines by column index.
        """
        # Stop function is the header can't be used as sorting key
        if not self.sorting_keys[col_index]:
            return
        
        # Sort the list of filtered lines
        reverse = self.sort_reverse if new_sort else not self.sort_reverse
        self.filtered_lines.sort(key=self.sorting_keys[col_index], reverse=reverse)
        
        # Toggle reverse mode and save last sort
        if new_sort:
            self.sort_reverse = not self.sort_reverse
            self.last_sort = col_index  