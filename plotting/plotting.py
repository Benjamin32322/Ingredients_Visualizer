# plotting.py
# This file contains plotting functionality using matplotlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from plotting.style_plot import get_color_palette, apply_plot_style


# ======================== PLOT CONFIGURATION MAPPINGS ========================

def _build_config_params_label_for_plot(config_params):
    """
    Build a label string from explicitly selected configuration parameters.
    Only includes parameters that were explicitly chosen by the user.
    
    Args:
        config_params (dict): Dictionary with keys 'pg', 'cp', 'bpc', 'cf', 'qg'
                              each containing a list of selected values
    
    Returns:
        str: Formatted label string for x-axis
    """
    if not config_params:
        return "All Configurations"
    
    label_parts = []
    
    # Plan Generator
    pg = config_params.get('pg', [])
    if pg and len(pg) > 0:
        label_parts.append(f"PG: {', '.join(pg)}")
    
    # Cardinality Provider
    cp = config_params.get('cp', [])
    if cp and len(cp) > 0:
        label_parts.append(f"CP: {', '.join(cp)}")
    
    # Build Plan Class
    bpc = config_params.get('bpc', [])
    if bpc and len(bpc) > 0:
        label_parts.append(f"BPC: {', '.join(bpc)}")
    
    # Query Graph (for query mode)
    qg = config_params.get('qg', [])
    if qg and len(qg) > 0:
        label_parts.append(f"Query: {', '.join(qg)}")
    
    # Cost Functions (from nested dict)
    cf = config_params.get('cf', {})
    if cf:
        for cf_key, cf_values in cf.items():
            if cf_values and len(cf_values) > 0:
                # Format the cost function name nicely
                cf_name = cf_key.replace('bpi_cf_', '').replace('wp_cf_', '').replace('_', ' ').title()
                label_parts.append(f"{cf_name}: {', '.join(cf_values)}")
    
    if label_parts:
        return '\n'.join(label_parts)
    else:
        return "All Configurations"


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
    if x_col == "Configuration Parameters" or x_col == "Query Graph: ps_qg":
        # Configuration parameter columns to display
        config_cols = ['pg_name', 'cp_name', 'bpc_name', 'bpi_cf_join_bundle', 
                      'bpi_cf_mat', 'bpi_cf_concat', 'wp_cf_host_id']
        
        # Add ps_qg at the top if in query mode
        if x_col == "Query Graph: ps_qg":
            config_cols = ['ps_qg'] + config_cols
        
        # Create multi-line labels for each data point
        x_labels = []
        for idx, row in df.iterrows():
            label_parts = []
            for col in config_cols:
                if col in df.columns:
                    value = row[col]
                    # Format the label nicely
                    col_display = col.replace('pg_name', 'PG').replace('cp_name', 'CP') \
                                    .replace('bpc_name', 'BP').replace('bpi_cf_join_bundle', 'Join Bundle') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Concat') \
                                    .replace('wp_cf_host_id', 'Host ID').replace('ps_qg', 'Query')
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
    if x_col == "Configuration Parameters" or x_col == "Query Graph: ps_qg":
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
    Create a box plot (legacy version for multiple boxes)
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame with data
        x_col: Column name for x-axis grouping (or "Configuration Parameters" for special handling)
        y_col: Column name for y-axis values
        title: Chart title
        y_label: Y-axis label
        colors: List of colors to use
    """
    if x_col == "Configuration Parameters" or x_col == "Query Graph: ps_qg":
        # For config params, create one box per row with config labels
        config_cols = ['pg_name', 'cp_name', 'bpc_name', 'bpi_cf_join_bundle', 
                      'bpi_cf_mat', 'bpi_cf_concat', 'wp_cf_host_id']
        
        # Add ps_qg at the top if in query mode
        if x_col == "Query Graph: ps_qg":
            config_cols = ['ps_qg'] + config_cols
        
        # Create labels for each configuration
        x_labels = []
        data_points = []
        for idx, row in df.iterrows():
            label_parts = []
            for col in config_cols:
                if col in df.columns:
                    value = row[col]
                    col_display = col.replace('pg_name', 'PG').replace('cp_name', 'CP') \
                                    .replace('bpc_name', 'BP').replace('bpi_cf_join_bundle', 'Join Bundle') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Concat') \
                                    .replace('wp_cf_host_id', 'Host ID').replace('ps_qg', 'Query')
                    label_parts.append(f"{col_display}: {value}")
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


def create_box_plot_single(ax, df, y_col, title, y_label, x_label, colors):
    """
    Create a single box plot using ALL values from the metric column.
    This is the proper box plot that shows quartiles, median, whiskers, and outliers.
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame with ALL data (not filtered)
        y_col: Column name for the metric values (e.g., 'avg_lf', 'lf')
        title: Chart title
        y_label: Y-axis label (e.g., "Average Loss Factor")
        x_label: X-axis label (configuration parameters string)
        colors: List of colors to use
    """
    # Get all values from the metric column
    values = df[y_col].dropna().tolist()
    
    if not values:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        return
    
    # Create the box plot with one box containing ALL values
    bp = ax.boxplot([values], labels=[x_label], patch_artist=True, showmeans=True, meanline=True)
    
    # Style the box
    bp['boxes'][0].set_facecolor(colors[0])
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][0].set_edgecolor('black')
    bp['boxes'][0].set_linewidth(1.5)
    
    # Style whiskers
    for whisker in bp['whiskers']:
        whisker.set_color('black')
        whisker.set_linewidth(1.5)
    
    # Style caps
    for cap in bp['caps']:
        cap.set_color('black')
        cap.set_linewidth(1.5)
    
    # Style median line
    for median in bp['medians']:
        median.set_color('red')
        median.set_linewidth(2)
    
    # Style mean line
    for mean in bp['means']:
        mean.set_color('green')
        mean.set_linewidth(2)
        mean.set_linestyle('--')
    
    # Style fliers (outliers)
    for flier in bp['fliers']:
        flier.set_marker('o')
        flier.set_markerfacecolor(colors[1] if len(colors) > 1 else 'red')
        flier.set_markeredgecolor('black')
        flier.set_markersize(6)
        flier.set_alpha(0.7)
    
    # Calculate and display statistics
    import numpy as np
    q1 = np.percentile(values, 25)
    median = np.median(values)
    q3 = np.percentile(values, 75)
    mean = np.mean(values)
    iqr = q3 - q1
    
    # Add statistics text box
    stats_text = f"n={len(values)}\nMedian={median:.2f}\nMean={mean:.2f}\nQ1={q1:.2f}\nQ3={q3:.2f}\nIQR={iqr:.2f}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right', bbox=props)
    
    # Labels and title
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    ax.set_xlabel("Configuration", fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Adjust x-axis label if it's multi-line
    if '\n' in x_label:
        ax.tick_params(axis='x', labelsize=8)
    
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
    if x_col == "Configuration Parameters" or x_col == "Query Graph: ps_qg":
        # Use index for x-values and add configuration labels
        x_values = range(len(df))
        x_axis_label = "Configuration Parameters"
        
        # Create multi-line labels
        config_cols = ['pg_name', 'cp_name', 'bpc_name', 'bpi_cf_join_bundle', 
                      'bpi_cf_mat', 'bpi_cf_concat', 'wp_cf_host_id']
        
        # Add ps_qg at the top if in query mode
        if x_col == "Query Graph: ps_qg":
            config_cols = ['ps_qg'] + config_cols
        
        x_labels = []
        for idx, row in df.iterrows():
            label_parts = []
            for col in config_cols:
                if col in df.columns:
                    value = row[col]
                    col_display = col.replace('pg_name', 'PG').replace('cp_name', 'CP') \
                                    .replace('bpc_name', 'BP').replace('bpi_cf_join_bundle', 'Join Bundle') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Concat') \
                                    .replace('wp_cf_host_id', 'Host ID').replace('ps_qg', 'Query')
                    label_parts.append(f"{col_display}: {value}")
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
                                    .replace('bpc_name', 'BP').replace('bpi_cf_join_bundle', 'Join Bundle') \
                                    .replace('bpi_cf_mat', 'Mat').replace('bpi_cf_concat', 'Concat') \
                                    .replace('wp_cf_host_id', 'Host ID')
                    label_parts.append(f"{col_display}: {value}")
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


def create_plot_window(columns, data, params_summary, plot_type, x_axis=None, y_axis=None, agg_metric=None, metric=None, plot_number=5, config_params=None):
    """
    Create a plot visualization window based on the selected plot type
    
    Args:
        columns (list): Column names from query results
        data (list): Query result data (list of tuples/lists)
        params_summary (str): Parameter summary string for display
        plot_type (str): Type of plot ("Bar Chart", "Box Plot", "Graph", "Scatter Plot")
        x_axis (str): Column name for X-axis (optional)
        y_axis (str): Column name for Y-axis (optional, kept for backward compatibility)
        agg_metric (str): Aggregation metric column name (e.g., "avg_lf", "max_qerr")
        metric (str): Metric selection ("Highest" or "Lowest", optional)
        plot_number (int): Number of data points to display (default: 5)
        config_params (dict): Configuration parameters for box plot x-axis label
    """
    # Create new window
    plot_window = tk.Toplevel()
    plot_window.title(f"{plot_type} - {agg_metric if agg_metric else 'Plot'}")
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
    
    # Check if we have a valid aggregation metric
    if agg_metric and agg_metric in df.columns:
        # We have a valid metric - create the plot
        column = agg_metric
        
        # Create a readable label from the metric name
        metric_labels = {
            "avg_lf": "Average Loss Factor",
            "median_lf": "Median Loss Factor",
            "max_lf": "Maximum Loss Factor",
            "min_lf": "Minimum Loss Factor",
            "avg_qerr": "Average Q-Error",
            "median_qerr": "Median Q-Error",
            "max_qerr": "Maximum Q-Error",
            "min_qerr": "Minimum Q-Error",
            "avg_perr": "Average P-Error",
            "median_perr": "Median P-Error",
            "max_perr": "Maximum P-Error",
            "min_perr": "Minimum P-Error",
            # Raw metrics for query mode
            "lf": "Loss Factor",
            "qerr": "Q-Error",
            "perr": "P-Error"
        }
        y_label = metric_labels.get(agg_metric, agg_metric)
        
        # Handle Box Plot differently - use ALL data
        if plot_type == "Box Plot":
            # Build x-axis label from config params
            x_axis_label = _build_config_params_label_for_plot(config_params)
            title = f"Box Plot: {y_label}"
            
            # Use all values for box plot
            create_box_plot_single(ax, df, column, title, y_label, x_axis_label, colors)
        else:
            # Other plot types - use sorted/filtered data
            # Determine sort order based on metric selection
            sort_ascending = (metric == "Lowest")
            
            # Get top N values
            df_sorted = df.nlargest(plot_number, column) if not sort_ascending else df.nsmallest(plot_number, column)
            
            # Determine title based on metric selection
            metric_text = metric if metric else "Highest"
            title = f"{metric_text} {plot_number} {y_label}"
            
            # Create the appropriate plot type
            if plot_type == "Bar Chart":
                create_bar_chart(ax, df_sorted, x_axis, column, title, y_label, colors)
            elif plot_type == "Scatter Plot":
                create_scatter_plot(ax, df_sorted, x_axis, column, title, y_label, colors)
            elif plot_type == "Graph":
                create_line_graph(ax, df_sorted, x_axis, column, title, y_label, colors)
            else:
                # Unknown plot type
                ax.text(0.5, 0.5, f"Plot type '{plot_type}' is not supported.\n\nAvailable types:\n- Bar Chart\n- Box Plot\n- Scatter Plot\n- Graph",
                        ha='center', va='center', fontsize=14, transform=ax.transAxes)
                ax.set_title(f"Unsupported Plot Type: {plot_type}")
    
    else:
        # No aggregation metric selected or not found in data
        message = f"Please select an Aggregation metric" if not agg_metric else f"Metric '{agg_metric}' not found in data\n\n"
        if agg_metric:
            message += f"Available data columns: {', '.join(df.columns[:10])}...\n"
            message += f"Data shape: {df.shape}"
        
        ax.text(0.5, 0.5, message,
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.set_title(f"{plot_type} - No Metric Selected")
    
    # Embed matplotlib figure in tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    # Create a toolbar frame for buttons
    toolbar = ttk.Frame(plot_window)
    toolbar.pack(side="bottom", fill="x", pady=5)
    
    # Export functions
    def export_to_pdf():
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF File", "*.pdf"), ("All Files", "*.*")]
            )
            if not filepath:
                return  # User cancelled
            
            # Save the figure as PDF
            fig.savefig(filepath, format='pdf', bbox_inches='tight', dpi=300)
            messagebox.showinfo("Export Successful", f"Plot saved as PDF:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def export_to_png():
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
            )
            if not filepath:
                return  # User cancelled
            
            # Save the figure as PNG
            fig.savefig(filepath, format='png', bbox_inches='tight', dpi=300)
            messagebox.showinfo("Export Successful", f"Plot saved as PNG:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    # Add export buttons
    btn_export_pdf = ttk.Button(toolbar, text="Export as PDF", command=export_to_pdf)
    btn_export_pdf.pack(side="left", padx=5)
    
    btn_export_png = ttk.Button(toolbar, text="Export as PNG", command=export_to_png)
    btn_export_png.pack(side="left", padx=5)
    
    # Add a close button
    close_button = ttk.Button(toolbar, text="Close", command=plot_window.destroy)
    close_button.pack(side="right", padx=5)
