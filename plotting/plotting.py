# plotting.py
# This file contains plotting functionality using matplotlib
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from plotting.style_plot import get_color_palette, apply_plot_style


# ======================== PLOT CONFIGURATION MAPPINGS ========================

def get_plot_config(y_axis):
    """
    Get the plotting configuration based on the selected Y-axis.
    This makes it easy to add new Y-axis configurations.
    
    Args:
        y_axis (str): Selected Y-axis value
    
    Returns:
        dict: Configuration with 'column', 'label', 'top_n' keys, or None if not configured
    """
    # Define configurations for different Y-axis selections
    configs = {
        "Loss Factor": {
            "column": "avg_lf",
            "label": "Average Loss Factor",
            "top_n": 5,
            "sort_ascending": False  # Highest values first
        },
        "Q-Error": {
            "column": "avg_qerr",
            "label": "Average Q-Error",
            "top_n": 5,
            "sort_ascending": False
        },
        "P-Error": {
            "column": "avg_perr",
            "label": "Average P-Error",
            "top_n": 5,
            "sort_ascending": False
        },
        # Add more configurations here as needed
        # "Your Y-Axis Name": {
        #     "column": "column_name_in_data",
        #     "label": "Display Label",
        #     "top_n": 10,
        #     "sort_ascending": False
        # }
    }
    
    return configs.get(y_axis)


# ======================== PLOTTING FUNCTIONS ========================

def create_bar_chart(ax, df, x_col, y_col, title, y_label, colors):
    """
    Create a bar chart with custom colors
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame with data
        x_col: Column name for x-axis (or index if None)
        y_col: Column name for y-axis values
        title: Chart title
        y_label: Y-axis label
        colors: List of colors to use
    """
    # Determine x-axis values and labels
    if x_col and x_col in df.columns:
        # Use the specified column for x-axis
        x_labels = df[x_col].astype(str).tolist()
        x_positions = range(len(df))
        x_axis_label = x_col
    else:
        # Create generic labels if no x column specified
        x_labels = [f"#{i+1}" for i in range(len(df))]
        x_positions = range(len(df))
        x_axis_label = "Rank"
    
    y_values = df[y_col].tolist()
    
    # Create bars with different colors
    bars = ax.bar(x_positions, y_values, color=colors[:len(df)], width=0.6)
    
    # Set x-axis labels
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    
    # Styling
    ax.set_xlabel(x_axis_label, fontsize=12, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on top of bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Apply custom styling
    apply_plot_style(ax)
    plt.tight_layout()


def create_plot_window(columns, data, params_summary, plot_type, x_axis=None, y_axis=None):
    """
    Create a plot visualization window based on the selected plot type
    
    Args:
        columns (list): Column names from query results
        data (list): Query result data (list of tuples/lists)
        params_summary (str): Parameter summary string for display
        plot_type (str): Type of plot ("Bar Chart", "Box Plot", "Graph", "Scatter Plot")
        x_axis (str): Column name for X-axis (optional)
        y_axis (str): Column name for Y-axis (optional)
    """
    # Create new window
    plot_window = tk.Toplevel()
    plot_window.title(f"{plot_type} - {y_axis if y_axis else 'Plot'}")
    plot_window.geometry("1000x800")
    
    # Display parameter summary at the top
    if params_summary:
        params_frame = ttk.Frame(plot_window, relief="solid", borderwidth=1)
        params_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        params_label = ttk.Label(
            params_frame,
            text=params_summary,
            wraplength=980,
            justify="left",
            padding=10,
            font=("Arial", 9)
        )
        params_label.pack(fill="x")
    
    # Convert data to pandas DataFrame
    df = pd.DataFrame(data, columns=columns)
    
    # Get color palette
    colors = get_color_palette()
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(11, 7))
    
    # Check if we have a configuration for this Y-axis
    plot_config = get_plot_config(y_axis) if y_axis else None
    
    if plot_config and plot_config['column'] in df.columns:
        # We have a valid configuration - create the plot
        column = plot_config['column']
        top_n = plot_config['top_n']
        sort_ascending = plot_config['sort_ascending']
        
        # Get top N values
        df_sorted = df.nlargest(top_n, column) if not sort_ascending else df.nsmallest(top_n, column)
        
        # Determine title
        title = f"Top {top_n} {plot_config['label']}"
        
        # Create the appropriate plot type
        if plot_type == "Bar Chart":
            create_bar_chart(ax, df_sorted, x_axis, column, title, plot_config['label'], colors)
        else:
            # Placeholder for other plot types
            ax.text(0.5, 0.5, f"'{plot_type}' for '{y_axis}'\nnot yet implemented.\n\nUse 'Bar Chart' for now.",
                    ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_title(f"{plot_type} - {y_axis}")
    
    else:
        # No configuration found - show placeholder
        message = f"No plot configuration for Y-Axis: '{y_axis}'\n\n"
        message += f"Available data columns: {', '.join(df.columns[:5])}...\n"
        message += f"Data shape: {df.shape}\n\n"
        message += "Add configuration in get_plot_config() function."
        
        ax.text(0.5, 0.5, message,
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.set_title(f"{plot_type} - No Configuration")
    
    # Embed matplotlib figure in tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    # Add a close button
    close_button = ttk.Button(plot_window, text="Close", command=plot_window.destroy)
    close_button.pack(pady=5)
