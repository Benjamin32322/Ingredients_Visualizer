# style_plot.py
# Plotting style configuration and color palette

# Custom color palette
COLOR_PALETTE = [
    '#fcc72d',  # Yellow/Gold
    '#ea6d3d',  # Orange
    '#e03a3c',  # Red
    '#cb1f73',  # Magenta/Pink
    '#383a6b'   # Dark Blue
]

# Individual color definitions for easy access
COLOR_YELLOW = '#fcc72d'
COLOR_ORANGE = '#ea6d3d'
COLOR_RED = '#e03a3c'
COLOR_MAGENTA = '#cb1f73'
COLOR_DARK_BLUE = '#383a6b'


def get_color_palette():
    """
    Get the custom color palette for plotting
    
    Returns:
        list: List of hex color codes
    """
    return COLOR_PALETTE


def get_color(index):
    """
    Get a specific color from the palette by index
    
    Args:
        index (int): Index of the color (0-4)
    
    Returns:
        str: Hex color code
    """
    return COLOR_PALETTE[index % len(COLOR_PALETTE)]


def apply_plot_style(ax=None):
    """
    Apply custom styling to a matplotlib axes object
    
    Args:
        ax: Matplotlib axes object (optional)
    """
    import matplotlib.pyplot as plt
    
    if ax is None:
        ax = plt.gca()
    
    # Set grid style
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Set spine colors
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')
        spine.set_linewidth(0.8)
    
    return ax
