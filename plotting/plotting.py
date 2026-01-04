# plotting.py
# This file contains plotting functionality using matplotlib
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from plotting.style_plot import get_color_palette, apply_plot_style


# ======================== PLOT CONFIGURATION MAPPINGS ========================

def get_plot_config(y_axis, metric=None, top_n=5):
    """
    Get the plotting configuration based on the selected Y-axis.
    This makes it easy to add new Y-axis configurations.
    
    Args:
        y_axis (str): Selected Y-axis value
        metric (str): Metric selection ("Highest" or "Lowest", optional)
        top_n (int): Number of data points to display (default: 5)
    
    Returns:
        dict: Configuration with 'column', 'label', 'top_n', 'sort_ascending' keys, or None if not configured
    """
    # Determine sort order based on metric
    # Default to "Highest" (descending) if not specified
    if metric == "Lowest":
        sort_ascending = True
    else:
        sort_ascending = False
    
    # Define configurations for different Y-axis selections
    configs = {
        "Loss Factor": {
            "column": "avg_lf",
            "label": "Average Loss Factor",
            "top_n": top_n,
            "sort_ascending": sort_ascending
        },
        "Q-Error": {
            "column": "avg_qerr",
            "label": "Average Q-Error",
            "top_n": top_n,
            "sort_ascending": sort_ascending
        },
        "P-Error": {
            "column": "avg_perr",
            "label": "Average P-Error",
            "top_n": top_n,
            "sort_ascending": sort_ascending
        },
        # Add more configurations here as needed
        # "Your Y-Axis Name": {
        #     "column": "column_name_in_data",
        #     "label": "Display Label",
        #     "top_n": top_n,
        #     "sort_ascending": sort_ascending
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
        x_col: Column name for x-axis (or "Configuration Parameters" for special handling)
        y_col: Column name for y-axis values
        title: Chart title
        y_label: Y-axis label
        colors: List of colors to use
    """
    # Check if we should display configuration parameters
    if x_col == "Configuration Parameters":
        # Configuration parameter columns to display
        config_cols = ['pg_name', 'cp_name', 'bpc_name', 'bpi_cf_join_bundle', 
                      'bpi_cf_mat', 'bpi_cf_concat', 'wp_cf_host_id']
        
        # Create multi-line labels for each data point
        x_labels = []
        for idx, row in df.iterrows():
            label_parts = []
            for col in config_cols:
                if col in df.columns:
                    value = row[col]
                    # Format the label nicely
                    col_display = col.replace('pg_name', 'Plan Gen').replace('cp_name', 'Card Prov') \
                                    .replace('bpc_name', 'Build Plan').replace('bpi_cf_join_bundle', 'Join Bundle') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Concat') \
                                    .replace('wp_cf_host_id', 'Host ID')
                    label_parts.append(f"{col_display}: {value}")
            x_labels.append('\n'.join(label_parts))
        
        x_positions = range(len(df))
        x_axis_label = "Configuration Parameters"
    elif x_col and x_col in df.columns:
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
    if x_col == "Configuration Parameters":
        # For config params, use smaller font and vertical alignment
        ax.set_xticklabels(x_labels, rotation=0, ha='center', fontsize=7, multialignment='left')
    else:
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


def create_box_plot(ax, df, x_col, y_col, title, y_label, colors):
    """
    Create a box plot
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame with data
        x_col: Column name for x-axis grouping (or "Configuration Parameters" for special handling)
        y_col: Column name for y-axis values
        title: Chart title
        y_label: Y-axis label
        colors: List of colors to use
    """
    if x_col == "Configuration Parameters":
        # For config params, create one box per row with config labels
        config_cols = ['pg_name', 'cp_name', 'bpc_name', 'bpi_cf_join_bundle', 
                      'bpi_cf_mat', 'bpi_cf_concat', 'wp_cf_host_id']
        
        # Create labels for each configuration
        x_labels = []
        data_points = []
        for idx, row in df.iterrows():
            label_parts = []
            for col in config_cols:
                if col in df.columns:
                    value = row[col]
                    col_display = col.replace('pg_name', 'PG').replace('cp_name', 'CP') \
                                    .replace('bpc_name', 'BPC').replace('bpi_cf_join_bundle', 'JB') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Con') \
                                    .replace('wp_cf_host_id', 'Host')
                    label_parts.append(f"{col_display}:{value}")
            x_labels.append('\n'.join(label_parts))
            data_points.append([row[y_col]])  # Single value as list for boxplot
        
        bp = ax.boxplot(data_points, labels=x_labels, patch_artist=True)
        
        # Color each box
        for patch, color in zip(bp['boxes'], colors[:len(data_points)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # Adjust label size for config params
        ax.tick_params(axis='x', labelsize=7)
        ax.set_xlabel("Configuration Parameters", fontsize=12, fontweight='bold')
        
    elif x_col and x_col in df.columns:
        # Group by x_col and create box plot for each group
        groups = df.groupby(x_col)[y_col].apply(list)
        bp = ax.boxplot(groups.values, labels=groups.index.astype(str), patch_artist=True)
        
        # Color each box
        for patch, color in zip(bp['boxes'], colors[:len(groups)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_xlabel(x_col, fontsize=12, fontweight='bold')
    else:
        # Single box plot for all data
        bp = ax.boxplot([df[y_col].tolist()], labels=['All Data'], patch_artist=True)
        bp['boxes'][0].set_facecolor(colors[0])
        bp['boxes'][0].set_alpha(0.7)
        ax.set_xlabel("", fontsize=12, fontweight='bold')
    
    # Styling
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Apply custom styling
    apply_plot_style(ax)
    plt.tight_layout()


def create_scatter_plot(ax, df, x_col, y_col, title, y_label, colors):
    """
    Create a scatter plot
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame with data
        x_col: Column name for x-axis (or "Configuration Parameters" for special handling)
        y_col: Column name for y-axis values
        title: Chart title
        y_label: Y-axis label
        colors: List of colors to use
    """
    if x_col == "Configuration Parameters":
        # Use index for x-values and add configuration labels
        x_values = range(len(df))
        x_axis_label = "Configuration Parameters"
        
        # Create multi-line labels
        config_cols = ['pg_name', 'cp_name', 'bpc_name', 'bpi_cf_join_bundle', 
                      'bpi_cf_mat', 'bpi_cf_concat', 'wp_cf_host_id']
        x_labels = []
        for idx, row in df.iterrows():
            label_parts = []
            for col in config_cols:
                if col in df.columns:
                    value = row[col]
                    col_display = col.replace('pg_name', 'PG').replace('cp_name', 'CP') \
                                    .replace('bpc_name', 'BPC').replace('bpi_cf_join_bundle', 'JB') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Con') \
                                    .replace('wp_cf_host_id', 'Host')
                    label_parts.append(f"{col_display}:{value}")
            x_labels.append('\n'.join(label_parts))
        
        ax.set_xticks(x_values)
        ax.set_xticklabels(x_labels, rotation=0, ha='center', fontsize=7)
        
    elif x_col and x_col in df.columns:
        x_values = df[x_col]
        x_axis_label = x_col
    else:
        x_values = range(len(df))
        x_axis_label = "Index"
    
    y_values = df[y_col]
    
    # Create scatter plot with gradient colors
    scatter = ax.scatter(x_values, y_values, c=range(len(df)), 
                        cmap=plt.cm.colors.ListedColormap(colors[:len(df)]),
                        s=100, alpha=0.7, edgecolors='black', linewidth=1.5)
    
    # Styling
    ax.set_xlabel(x_axis_label if x_col != "Configuration Parameters" else x_axis_label, 
                  fontsize=12, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Apply custom styling
    apply_plot_style(ax)
    plt.tight_layout()


def create_line_graph(ax, df, x_col, y_col, title, y_label, colors):
    """
    Create a line graph
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame with data
        x_col: Column name for x-axis (or "Configuration Parameters" for special handling)
        y_col: Column name for y-axis values
        title: Chart title
        y_label: Y-axis label
        colors: List of colors to use
    """
    if x_col == "Configuration Parameters":
        # Use index for x-values and add configuration labels
        x_values = range(len(df))
        x_axis_label = "Configuration Parameters"
        
        # Create multi-line labels
        config_cols = ['pg_name', 'cp_name', 'bpc_name', 'bpi_cf_join_bundle', 
                      'bpi_cf_mat', 'bpi_cf_concat', 'wp_cf_host_id']
        x_labels = []
        for idx, row in df.iterrows():
            label_parts = []
            for col in config_cols:
                if col in df.columns:
                    value = row[col]
                    col_display = col.replace('pg_name', 'PG').replace('cp_name', 'CP') \
                                    .replace('bpc_name', 'BPC').replace('bpi_cf_join_bundle', 'JB') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Con') \
                                    .replace('wp_cf_host_id', 'Host')
                    label_parts.append(f"{col_display}:{value}")
            x_labels.append('\n'.join(label_parts))
        
        ax.set_xticks(x_values)
        ax.set_xticklabels(x_labels, rotation=0, ha='center', fontsize=7)
        
    elif x_col and x_col in df.columns:
        x_values = df[x_col]
        x_axis_label = x_col
    else:
        x_values = range(len(df))
        x_axis_label = "Rank"
    
    y_values = df[y_col]
    
    # Create line plot
    ax.plot(x_values, y_values, color=colors[0], linewidth=2.5, marker='o', 
            markersize=8, markerfacecolor=colors[1], markeredgecolor='black', 
            markeredgewidth=1.5)
    
    # Add value labels at each point
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        ax.text(x, y, f'{y:.2f}', ha='center', va='bottom', 
                fontsize=9, fontweight='bold')
    
    # Styling
    ax.set_xlabel(x_axis_label, fontsize=12, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # Apply custom styling
    apply_plot_style(ax)
    plt.tight_layout()


def create_plot_window(columns, data, params_summary, plot_type, x_axis=None, y_axis=None, metric=None, plot_number=5):
    """
    Create a plot visualization window based on the selected plot type
    
    Args:
        columns (list): Column names from query results
        data (list): Query result data (list of tuples/lists)
        params_summary (str): Parameter summary string for display
        plot_type (str): Type of plot ("Bar Chart", "Box Plot", "Graph", "Scatter Plot")
        x_axis (str): Column name for X-axis (optional)
        y_axis (str): Column name for Y-axis (optional)
        metric (str): Metric selection ("Highest" or "Lowest", optional)
        plot_number (int): Number of data points to display (default: 5)
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
    plot_config = get_plot_config(y_axis, metric, plot_number) if y_axis else None
    
    if plot_config and plot_config['column'] in df.columns:
        # We have a valid configuration - create the plot
        column = plot_config['column']
        top_n = plot_config['top_n']
        sort_ascending = plot_config['sort_ascending']
        
        # Get top N values
        df_sorted = df.nlargest(top_n, column) if not sort_ascending else df.nsmallest(top_n, column)
        
        # Determine title based on metric selection
        metric_text = metric if metric else "Highest"
        title = f"{metric_text} {top_n} {plot_config['label']}"
        
        # Create the appropriate plot type
        if plot_type == "Bar Chart":
            create_bar_chart(ax, df_sorted, x_axis, column, title, plot_config['label'], colors)
        elif plot_type == "Box Plot":
            create_box_plot(ax, df_sorted, x_axis, column, title, plot_config['label'], colors)
        elif plot_type == "Scatter Plot":
            create_scatter_plot(ax, df_sorted, x_axis, column, title, plot_config['label'], colors)
        elif plot_type == "Graph":
            create_line_graph(ax, df_sorted, x_axis, column, title, plot_config['label'], colors)
        else:
            # Unknown plot type
            ax.text(0.5, 0.5, f"Plot type '{plot_type}' is not supported.\n\nAvailable types:\n- Bar Chart\n- Box Plot\n- Scatter Plot\n- Graph",
                    ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_title(f"Unsupported Plot Type: {plot_type}")
    
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
