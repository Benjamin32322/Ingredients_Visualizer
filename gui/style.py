# style.py
"""
Style configuration for the Ingredients Visualizer GUI
This module contains all TTK style definitions and theming for the application.
"""

from tkinter import ttk


def setup_application_styles(parent_widget):
    """
    Configure modern styling for the application
    
    Args:
        parent_widget: The parent widget (typically the main GUI class) that has access to ttk.Style()
    
    Returns:
        ttk.Style: The configured style object
    """
    style = ttk.Style()
    
    # Configure modern frame styles with borders
    style.configure("Card.TFrame", 
                   relief="solid", 
                   borderwidth=1, 
                   background="#f8f9fa")
    
    style.configure("Header.TFrame", 
                   relief="solid", 
                   borderwidth=2, 
                   background="#2c3e50")
    
    style.configure("Footer.TFrame", 
                   relief="solid", 
                   borderwidth=1, 
                   background="#34495e")
    
    # Configure label styles
    style.configure("Header.TLabel", 
                   background="#2c3e50", 
                   foreground="white", 
                   font=("Arial", 16, "bold"))
    
    style.configure("Title.TLabel", 
                   font=("Arial", 12, "bold"), 
                   foreground="#2c3e50")
    
    style.configure("Footer.TLabel", 
                   background="#34495e", 
                   foreground="white", 
                   font=("Arial", 9))
    
    # Configure button styles
    style.configure("Action.TButton", 
                   font=("Arial", 10, "bold"))
    
    return style


# Color palette constants for consistent theming
class Colors:
    """Color constants for the application theme"""
    # Primary colors
    PRIMARY_DARK = "#2c3e50"      # Dark blue-gray for headers
    SECONDARY_DARK = "#34495e"    # Slightly lighter for footers
    LIGHT_GRAY = "#f8f9fa"        # Light background for cards
    
    # Text colors
    WHITE = "white"
    BLACK = "black"
    GRAY = "gray"
    
    # Accent colors (for future use)
    SUCCESS = "#27ae60"
    WARNING = "#f39c12"
    ERROR = "#e74c3c"
    INFO = "#3498db"


class Fonts:
    """Font constants for the application"""
    # Header fonts
    HEADER_LARGE = ("Arial", 16, "bold")
    HEADER_MEDIUM = ("Arial", 12, "bold")
    HEADER_SMALL = ("Arial", 10, "bold")
    
    # Body fonts
    BODY_REGULAR = ("Arial", 10)
    BODY_SMALL = ("Arial", 9)
    
    # Monospace fonts (for code/data display)
    MONO_REGULAR = ("Courier", 10)
    MONO_SMALL = ("Courier", 9)


class StyleConfig:
    """Configuration class for easy style customization"""
    
    @staticmethod
    def get_frame_styles():
        """Get all frame style configurations"""
        return {
            "Card.TFrame": {
                "relief": "solid",
                "borderwidth": 1,
                "background": Colors.LIGHT_GRAY
            },
            "Header.TFrame": {
                "relief": "solid",
                "borderwidth": 2,
                "background": Colors.PRIMARY_DARK
            },
            "Footer.TFrame": {
                "relief": "solid",
                "borderwidth": 1,
                "background": Colors.SECONDARY_DARK
            }
        }
    
    @staticmethod
    def get_label_styles():
        """Get all label style configurations"""
        return {
            "Header.TLabel": {
                "background": Colors.PRIMARY_DARK,
                "foreground": Colors.WHITE,
                "font": Fonts.HEADER_LARGE
            },
            "Title.TLabel": {
                "font": Fonts.HEADER_MEDIUM,
                "foreground": Colors.PRIMARY_DARK
            },
            "Footer.TLabel": {
                "background": Colors.SECONDARY_DARK,
                "foreground": Colors.WHITE,
                "font": Fonts.BODY_SMALL
            }
        }
    
    @staticmethod
    def get_button_styles():
        """Get all button style configurations"""
        return {
            "Action.TButton": {
                "font": Fonts.HEADER_SMALL
            }
        }


def apply_custom_styles(style_object, custom_configs=None):
    """
    Apply custom style configurations to a ttk.Style object
    
    Args:
        style_object: ttk.Style() instance
        custom_configs: Optional dictionary of custom style configurations
    """
    # Apply default configurations
    frame_styles = StyleConfig.get_frame_styles()
    label_styles = StyleConfig.get_label_styles()
    button_styles = StyleConfig.get_button_styles()
    
    # Apply frame styles
    for style_name, config in frame_styles.items():
        style_object.configure(style_name, **config)
    
    # Apply label styles
    for style_name, config in label_styles.items():
        style_object.configure(style_name, **config)
    
    # Apply button styles
    for style_name, config in button_styles.items():
        style_object.configure(style_name, **config)
    
    # Apply any custom configurations
    if custom_configs:
        for style_name, config in custom_configs.items():
            style_object.configure(style_name, **config)