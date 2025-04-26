# Import the main application window class
from mainwindow import MainWindow

# Import Windows DPI awareness settings
from ctypes import windll
# Enable DPI awareness for better display scaling
windll.shcore.SetProcessDpiAwareness(1)

# Main entry point of the application
if __name__ == "__main__":
    # Create and run the main application window
    app = MainWindow()
    app.mainloop()
