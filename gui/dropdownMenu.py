import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class DropdownMenu(ttk.Frame):
    def __init__ (self, parent, header, items):
        super().__init__(parent)
        self.header = header
        self.items = items
        self.selected_items = []
        self.set_items(items)
        
    
    def set_items(self, items):
        pass  # Implementation