"""
GUI Query Handlers Module
Handles database query execution and result processing.
Uses centralized configuration from db.db_config for all database-related constants.
"""

from db.dbHandler import build_filter, build_cost_filters, execute_query
from db.db_config import (
    METRIC_TO_SQL, COMPARISON_OPERATORS, METRIC_LABELS, 
    UI_ANALYSIS_MAP, ANALYSIS_TO_FILTER_KEY, CONFIG_PARAM_DISPLAY
)
from utils import build_config_params_label
from plotting.treeview import plot_treeview


class QueryHandlersMixin:
    """Mixin class providing database query execution methods"""
    
    def choose_correct_query(self):
        """
        Simplified query routing:
        1. If "Query Selection" has items → use all_single_query.sql (query_id=3)
        2. Otherwise → use all_aggregated.sql (query_id=2)
        
        Both queries support filtering on any metric and display only selected analysis columns.
        """
        print("=" * 60)
        print("DEBUG: choose_correct_query")
        
        # Get user selections
        selected_queries = self.ms_query_selection.get_selected()
        selected_methods = self.ms_analysis_parameter.get_selected()
        selected_plot_types = self.ms_plot_type.get_selected()
        
        # Validate: Analysis Parameter is mandatory
        if not selected_methods or len(selected_methods) == 0:
            self.update_status("⚠️ Error: Please select an Analysis Parameter (Loss Factor / Q-Error / P-Error)")
            return
        
        # Determine analysis type
        if "Loss Factor Analysis" in selected_methods:
            analysis_type = "Loss Factor"
        elif "Q-Error Analysis" in selected_methods:
            analysis_type = "Q-Error"
        elif "P-Error Analysis" in selected_methods:
            analysis_type = "P-Error"
        else:
            # Should not reach here due to validation above, but keep as safety
            self.update_status("⚠️ Error: Please select a valid Analysis Parameter")
            return
        
        print(f"  Selected Analysis: {analysis_type}")
        print(f"  Selected Queries: {selected_queries}")
        
        # Route to appropriate query
        if selected_queries and len(selected_queries) > 0:
            # User selected specific queries → use single query (no aggregation)
            print(f"  -> Using All Single Query (query_id=3)")
            self.on_execute(query_id=3, analysis_type=analysis_type)
        else:
            # No specific queries → use aggregated query
            print(f"  -> Using All Aggregated Query (query_id=2)")
            self.on_execute(query_id=2, analysis_type=analysis_type)
        
        print("=" * 60)
    
    def on_execute(self, query_id=2, analysis_type="Loss Factor"):
        """
        Execute analysis query
        
        Args:
            query_id (int): Query identifier (1=Pläne, 2=Aggregated, 3=Single Query)
            analysis_type (str): Type of analysis for status message
        """
        selected_pg = self.ms_plan_generator.get_selected()
        selected_cp = self.ms_cardinality_provider.get_selected()
        selected_bpc = self.ms_build_plan_class.get_selected()
        selected_cf = self.msplus_cost_function.get_selected()
        selected_qg = self.ms_query_selection.get_selected()
        selected_plot_types = self.ms_plot_type.get_selected()
        
        # Determine X-Axis and Y-Axis based on query selection
        if selected_qg and len(selected_qg) > 0:
            # Query mode - use ps_qg for x-axis and metric for y-axis
            selected_x_axis = ["Query Graph: ps_qg"]
            # Y-axis depends on analysis type
            if analysis_type == "Loss Factor":
                selected_y_axis = ["lf"]
            elif analysis_type == "Q-Error":
                selected_y_axis = ["qerr"]
            elif analysis_type == "P-Error":
                selected_y_axis = ["perr"]
            else:
                selected_y_axis = ["lf"]  # default
        else:
            # Aggregated mode - use configuration parameters for x-axis
            selected_x_axis = ["Configuration Parameters"]
            selected_y_axis = ["Loss Factor"]

        pg_filter = build_filter("pg_name", selected_pg)
        cp_filter = build_filter("cp_name", selected_cp)
        bpc_filter = build_filter("bpc_name", selected_bpc)
        qg_filter = build_filter("ps_qg", selected_qg)
        cf_filter = build_cost_filters(selected_cf)
        
        # Simplified filter setup - both query_id=2 and query_id=3 use the same structure
        filters = {
            "PG_NAME_FILTER": pg_filter,
            "CP_NAME_FILTER": cp_filter,
            "BPC_NAME_FILTER": bpc_filter,
            "QUERY_NAME_FILTER": qg_filter
        }
        
        # Add detail metric filter if exists
        detail_filter_values = self.get_detail_filter_values()
        detail_metric_filter = self.build_detail_metric_filter(detail_filter_values)
        filters["DETAIL_METRIC_FILTER"] = detail_metric_filter
        
        # Set analysis type for column selection
        if analysis_type == "Loss Factor":
            filters["ANALYSIS_TYPE"] = "LF"
        elif analysis_type == "Q-Error":
            filters["ANALYSIS_TYPE"] = "QERR"
        elif analysis_type == "P-Error":
            filters["ANALYSIS_TYPE"] = "PERR"
        else:
            filters["ANALYSIS_TYPE"] = "LF"  # default
        
        # Add cost function filters
        filters.update(cf_filter)
        
        print(f"\nDEBUG: on_execute (query_id={query_id}, analysis_type={analysis_type})")
        print(f"  detail_metric_filter: {detail_metric_filter}")
        
        # Execute the query
        columns, result = execute_query(query_id, filters=filters)
        
        # Build parameter summary for display and export
        params_summary = self.build_params_summary(
            query_id=query_id,
            analysis_type=analysis_type,
            selected_pg=selected_pg,
            selected_cp=selected_cp,
            selected_bpc=selected_bpc,
            selected_cf=selected_cf,
            detail_filter_values=detail_filter_values
        )
        
        # Build config params summary for box plot x-axis label
        config_params = {
            'pg': selected_pg,
            'cp': selected_cp,
            'bpc': selected_bpc,
            'cf': selected_cf,
            'qg': selected_qg
        }
        
        # Check if a plot type is selected
        if selected_plot_types and len(selected_plot_types) > 0:
            # Plot type is selected, call plotting method
            plot_type = selected_plot_types[0]  # Take the first selected plot type
            x_axis = selected_x_axis[0] if selected_x_axis and len(selected_x_axis) > 0 else None
            y_axis = selected_y_axis[0] if selected_y_axis and len(selected_y_axis) > 0 else None
            
            # Get aggregation metric selection (e.g., avg_lf, max_qerr, etc.)
            # In query mode (query_id=3), use the metric column directly (lf, qerr, perr)
            if query_id == 3:
                # Query mode - use y_axis value as metric
                agg_metric = y_axis if y_axis else None
            else:
                # Aggregated mode - use selected aggregation
                selected_agg_metrics = self.ms_agg_metric.get_selected()
                agg_metric = selected_agg_metrics[0] if selected_agg_metrics and len(selected_agg_metrics) > 0 else None
                
                # Validation: Check if aggregation is required but not selected
                # The aggregation popover is enabled when its button state is 'normal'
                agg_is_enabled = str(self.ms_agg_metric.button.cget('state')) == 'normal'
                if not agg_metric and agg_is_enabled:
                    self.update_status("Please select an Aggregation when using the Plotting functionality")
                    self.after(100, self.restore_entry_focus)
                    return
            
            # Get metric selection (Highest/Lowest)
            selected_metrics = self.ms_metric.get_selected()
            metric = selected_metrics[0] if selected_metrics and len(selected_metrics) > 0 else None
            
            # Get number of data points to plot
            plot_number_str = self.plot_number_var.get().strip()
            plot_number = int(plot_number_str) if plot_number_str and plot_number_str.isdigit() else 5
            
            # Get box plot split configuration (if Box Plot is selected)
            box_plot_split = None
            if plot_type == "Box Plot":
                box_plot_split = self.get_box_plot_split_config()
                # Validate: Box Plot split selection is mandatory
                if not box_plot_split:
                    self.update_status("⚠️ Please select a Split Option for Box Plot")
                    self.after(100, self.restore_entry_focus)
                    return
            
            # Display plot in results frame with aggregation metric and config params
            self.display_plot_in_frame(columns, result, params_summary, plot_type, x_axis, y_axis, agg_metric, metric, plot_number, config_params, box_plot_split)
        else:
            # No plot type selected, show treeview (table) in results frame
            self.display_treeview_in_frame(columns, result, params_summary)
        
        # Update status and restore focus
        self.update_status(f"{analysis_type} query executed - {len(result)} results found")
        self.after(100, self.restore_entry_focus)
    
    def build_params_summary(self, query_id, analysis_type, selected_pg, selected_cp, selected_bpc, selected_cf, detail_filter_values=None):
        """
        Build a summary string of all query parameters for display and export
        
        Returns:
            str: Formatted parameter summary
        """
        parts = []
        parts.append(f"Analysis Type: {analysis_type}")
        parts.append(f"Plan Generators: {', '.join(selected_pg) if selected_pg else 'All'}")
        parts.append(f"Cardinality Providers: {', '.join(selected_cp) if selected_cp else 'All'}")
        parts.append(f"Build Plan Class: {', '.join(selected_bpc) if selected_bpc else 'All'}")
        
        # Cost functions
        cf_parts = []
        for key, values in selected_cf.items():
            if values:
                cf_name = key.replace('_', ' ').title()
                cf_parts.append(f"{cf_name}: {', '.join(values)}")
        if cf_parts:
            parts.append(f"Cost Functions: {' | '.join(cf_parts)}")
        else:
            parts.append("Cost Functions: All")
        
        return " | ".join(parts)
    
    def build_detail_metric_filter(self, filter_values):
        """
        Convert filter values to SQL HAVING clause condition for DuckDB.
        Uses centralized METRIC_TO_SQL and COMPARISON_OPERATORS from db_config.
        
        Args:
            filter_values (list): List of filter dictionaries from get_detail_filter_values()
                Each dict contains:
                - 'metric': Selected metric (e.g., 'avg_lf')
                - 'comparison': Comparison type
                - 'value': Numeric value
        
        Returns:
            str: SQL HAVING clause condition with multiple filters combined with AND
                 (e.g., "AVG(ps_loss_factor) > 10.0 AND MEDIAN(ps_loss_factor) < 50.0")
        """
        print(f"\nDEBUG: build_detail_metric_filter")
        print(f"  Input - filter_values: {filter_values}")
        
        # Validate inputs
        if not filter_values:
            print(f"  -> No filters provided, returning '1=1'")
            return "1=1"  # No filtering
        
        # Build SQL conditions for each filter
        conditions = []
        for i, filter_dict in enumerate(filter_values):
            metric = filter_dict.get('metric')
            comparison = filter_dict.get('comparison')
            value = filter_dict.get('value')
            
            # Skip incomplete filters
            if not metric or not comparison or value is None:
                print(f"  Filter {i+1}: Incomplete, skipping")
                continue
            
            # Get SQL expression from centralized config
            sql_metric = METRIC_TO_SQL.get(metric, metric)
            
            # Handle "between" comparison separately
            if comparison == "between":
                if isinstance(value, tuple) and len(value) == 2:
                    condition = f"{sql_metric} BETWEEN {value[0]} AND {value[1]}"
                    conditions.append(condition)
                    print(f"  Filter {i+1}: {metric} {comparison} {value[0]};{value[1]} -> {condition}")
                else:
                    print(f"  Filter {i+1}: Invalid 'between' value format, skipping")
                    continue
            else:
                # Get operator from centralized config
                operator = COMPARISON_OPERATORS.get(comparison, ">")
                condition = f"{sql_metric} {operator} {value}"
                conditions.append(condition)
                print(f"  Filter {i+1}: {metric} {comparison} {value} -> {condition}")
        
        # Combine all conditions with AND
        if conditions:
            result = " AND ".join(conditions)
            print(f"  -> Final SQL: {result}")
            return result
        else:
            print(f"  -> No valid conditions, returning '1=1'")
            return "1=1"
    
    def create_plot(self, columns, data, params_summary, plot_type, x_axis=None, y_axis=None, metric=None, plot_number=5):
        """
        Create a plot visualization based on the selected plot type
        
        Args:
            columns (list): Column names from query results
            data (list): Query result data
            params_summary (str): Parameter summary string
            plot_type (str): Type of plot ("Bar Chart", "Box Plot", "Graph", "Scatter Plot")
            x_axis (str): Column name for X-axis (optional)
            y_axis (str): Column name for Y-axis (optional)
            metric (str): Metric selection ("Highest" or "Lowest")
            plot_number (int): Number of data points to display (default: 5)
        """
        # Import plotting function from plotting module
        from plotting.plotting import create_plot_window
        
        # Call the plotting function
        create_plot_window(columns, data, params_summary, plot_type, x_axis, y_axis, metric, plot_number)

    def display_treeview_in_frame(self, columns, data, params_summary):
        """Display treeview table in the results frame"""
        import tkinter as tk
        from tkinter import ttk
        import pandas as pd
        from tkinter import filedialog, messagebox
        
        print(f"DEBUG: display_treeview_in_frame called with {len(data)} rows")
        
        # Store current results for fullscreen
        self.current_results_data = {
            'type': 'treeview',
            'columns': columns,
            'data': data,
            'params_summary': params_summary
        }
        
        # Clear the results container
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        print("DEBUG: Results container cleared")
        print(f"DEBUG: Container geometry: {self.results_container.winfo_width()}x{self.results_container.winfo_height()}")
        print(f"DEBUG: Container is visible: {self.results_container.winfo_ismapped()}")
        
        # Create treeview with scrollbars (no toolbar/export button in embedded view)
        tree_frame = ttk.Frame(self.results_container)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                           yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=15)
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Pack scrollbars and treeview
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        
        print("DEBUG: Treeview created and packed")
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        # Insert data
        for row in data:
            tree.insert("", "end", values=row)
        
        print(f"DEBUG: Inserted {len(data)} rows into treeview")
        
        # Force update to ensure widgets are rendered
        tree_frame.update_idletasks()
        self.results_container.update_idletasks()
        self.results_container.update()
        print(f"DEBUG: Tree frame size: {tree_frame.winfo_width()}x{tree_frame.winfo_height()}")
        print(f"DEBUG: Treeview size: {tree.winfo_width()}x{tree.winfo_height()}")
        print("DEBUG: display_treeview_in_frame completed")
    
    def display_plot_in_frame(self, columns, data, params_summary, plot_type, x_axis=None, y_axis=None, agg_metric=None, metric=None, plot_number=5, config_params=None, box_plot_split=None):
        """Display plot in the results frame"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from plotting.plotting import get_plot_config, create_bar_chart, create_box_plot, create_box_plot_single, create_box_plot_split, create_scatter_plot, create_line_graph
        import pandas as pd
        import tkinter as tk
        from tkinter import ttk
        
        print(f"DEBUG: display_plot_in_frame called - plot_type: {plot_type}, agg_metric: {agg_metric}, box_plot_split: {box_plot_split}")
        
        # Store current results for fullscreen
        self.current_results_data = {
            'type': 'plot',
            'columns': columns,
            'data': data,
            'params_summary': params_summary,
            'plot_type': plot_type,
            'x_axis': x_axis,
            'y_axis': y_axis,
            'agg_metric': agg_metric,
            'metric': metric,
            'plot_number': plot_number,
            'config_params': config_params,
            'box_plot_split': box_plot_split
        }
        
        # Clear the results container
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        print("DEBUG: Results container cleared for plot")
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=columns)
        
        # Get color palette
        from plotting.style_plot import get_color_palette
        colors = get_color_palette()
        
        # Create figure with smaller size for embedding
        fig, ax = plt.subplots(figsize=(8, 5))
        
        print(f"DEBUG: Creating {plot_type}")
        
        # Check if we have a valid aggregation metric selected
        if agg_metric and agg_metric in df.columns:
            column = agg_metric
            
            # Get readable label from centralized METRIC_LABELS config
            y_label = METRIC_LABELS.get(agg_metric, agg_metric)
            
            # Handle Box Plot differently - use ALL data, not sorted/filtered
            if plot_type == "Box Plot":
                # Build x-axis label from explicitly selected config parameters
                x_axis_label = build_config_params_label(config_params)
                title = f"Box Plot: {y_label}"
                
                # Check if split configuration is provided
                if box_plot_split and box_plot_split in df.columns:
                    # Use split box plot function with max_boxes limit
                    create_box_plot_split(ax, df, column, box_plot_split, title, y_label, colors, max_boxes=plot_number)
                else:
                    # Use all values for single box plot (no sorting/filtering)
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
            # No aggregation metric selected or not found in data - show placeholder
            message = f"Please select an Aggregation metric" if not agg_metric else f"Metric '{agg_metric}' not found in data"
            ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12, transform=ax.transAxes)
            ax.set_title(f"{plot_type} - No Metric Selected")
        
        print("DEBUG: Plot created, embedding in tkinter")
        
        # Create a frame with scrollbars for the plot
        plot_frame = ttk.Frame(self.results_container)
        plot_frame.pack(fill="both", expand=True)
        
        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(plot_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(plot_frame, orient="horizontal")
        
        # Create canvas for scrolling
        scroll_canvas = tk.Canvas(plot_frame, yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=scroll_canvas.yview)
        h_scrollbar.config(command=scroll_canvas.xview)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        scroll_canvas.pack(side="left", fill="both", expand=True)
        
        # Embed the matplotlib plot in the scrollable canvas
        canvas = FigureCanvasTkAgg(fig, master=scroll_canvas)
        canvas.draw()
        plot_widget = canvas.get_tk_widget()
        
        # Add the plot widget to the scrollable canvas
        scroll_canvas.create_window((0, 0), window=plot_widget, anchor="nw")
        
        # Update scroll region after widget is rendered
        plot_widget.update_idletasks()
        scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))
        
        print("DEBUG: Plot with scrollbars embedded")
        
        # Force update to ensure widgets are rendered
        plot_frame.update_idletasks()
        self.results_container.update_idletasks()
        self.results_container.update()
        
        plt.close(fig)  # Close the figure to free memory
        print("DEBUG: display_plot_in_frame completed")
    
    def _export_to_excel(self, columns, data, params_summary):
        """Export treeview data to Excel"""
        import pandas as pd
        from tkinter import filedialog, messagebox
        
        try:
            df = pd.DataFrame(data, columns=columns)
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel-Datei", "*.xlsx"), ("Alle Dateien", "*.*")]
            )
            if not filepath:
                return
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                if params_summary:
                    params_rows = [
                        ['Query Parameters:', params_summary],
                        ['', '']
                    ]
                    params_df = pd.DataFrame(params_rows)
                    params_df.to_excel(writer, sheet_name='Data', index=False, header=False)
                    df.to_excel(writer, sheet_name='Data', index=False, startrow=len(params_rows))
                else:
                    df.to_excel(writer, sheet_name='Data', index=False)
            
            messagebox.showinfo("Export erfolgreich", f"Datei gespeichert:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export fehlgeschlagen", f"Fehler beim Exportieren:\n{str(e)}")

