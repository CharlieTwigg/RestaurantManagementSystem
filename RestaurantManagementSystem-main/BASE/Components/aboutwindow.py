# Import required GUI libraries
import tkinter as tk
from tkinter import ttk

# Import Windows DPI awareness settings
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)


class AboutWindow(tk.Toplevel):
    """A simple window displaying information about the application"""
    
    def __init__(self, parent):
        super().__init__(parent)

        # Configure window dimensions and position
        self.win_width = 360
        self.win_height = 250
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate center position for the window
        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = int(screen_height/2 - self.win_height/2)

        # Set window properties
        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.resizable(0, 0)  # Prevent window resizing
        self.title('About the application')

        # Create and display about text
        about_lbl = ttk.Label(
            self,
            wraplength=300,  # Wrap text at 300 pixels
            justify='left',
            padding=(5, 50, 0, 0),  # Add padding (left, top, right, bottom)
            font=("Helvetica Bold", 12),
            text = "Made by Charlie Twigg.")
        about_lbl.pack()
