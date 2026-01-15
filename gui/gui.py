import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from db.dbHandler import get_values_for_dropdown, build_filter, build_cost_filters, execute_query
from gui.multiSelect import PopoverMultiSelect, MultiSelectPlus
from gui.style import setup_application_styles
from gui.responsiveness import ResponsivenessMixin
from gui.query_handlers import QueryHandlersMixin
from plotting.treeview import plot_treeview



class GUI(ResponsivenessMixin, QueryHandlersMixin, tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ingredients Visualizer - Advanced Database Query Interface")
        
        # Track scheduled after callbacks for cleanup
        self._after_ids = []
        self._is_closing = False
        
        # Configure window
        self.attributes("-fullscreen", True)
        
        # Define window size for non-fullscreen mode
        width, height = 1400, 900
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self._default_geometry = f"{width}x{height}+{x}+{y}"
        self.geometry(self._default_geometry)

        # Bind Escape to exit fullscreen and restore size
        def _exit_fullscreen(event=None):
            self.attributes("-fullscreen", False)
            self.geometry(self._default_geometry)
        self.bind("<Escape>", _exit_fullscreen)

        # Handle window state changes to ensure consistent sizing
        def _handle_window_state_change():
            """Monitor window state and ensure consistent sizing"""
            if self._is_closing:
                return  # Stop if window is closing
            
            try:
                current_state = self.state()
                if hasattr(self, '_last_state'):
                    # If we're coming back from minimized state and not in fullscreen
                    if (self._last_state == "iconic" and 
                        current_state == "normal" and 
                        not self.attributes("-fullscreen")):
                        self.geometry(self._default_geometry)
                self._last_state = current_state
                # Schedule next check
                after_id = self.after(100, _handle_window_state_change)
                self._after_ids.append(after_id)
            except tk.TclError:
                # Window is being destroyed
                pass
        
        # Initialize state tracking
        self._last_state = self.state()
        
        # Override iconify to exit fullscreen first
        original_iconify = self.iconify
        def _iconify_with_fullscreen_exit():
            """Exit fullscreen before minimizing"""
            if self.attributes("-fullscreen"):
                self.attributes("-fullscreen", False)
                self.geometry(self._default_geometry)
            original_iconify()
        self.iconify = _iconify_with_fullscreen_exit
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start monitoring window state
        after_id = self.after(100, _handle_window_state_change)
        self._after_ids.append(after_id)

        # Configure modern styling
        self.setup_styles()
        
        # Create main layout structure
        self.create_layout_structure()
        
        # Build all components
        self.build_header()
        self.build_main_content()
        self.build_footer()
        
        # Initialize focus management
        self.setup_focus_management()
    
    def on_closing(self):
        """Handle window close event properly"""
        self._is_closing = True
        
        # Cancel all scheduled after callbacks
        for after_id in self._after_ids:
            try:
                self.after_cancel(after_id)
            except:
                pass
        
        # Destroy the window and quit the application
        self.destroy()
        self.quit()

    def setup_styles(self):
        """Configure modern styling for the application"""
        self.style = setup_application_styles(self)

    def create_layout_structure(self):
        """Create the main layout structure with header, content area, and footer"""
        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header section
        self.header_frame = ttk.Frame(self.main_container, style="Header.TFrame")
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        # Footer section - pack before content so it gets space
        self.footer_frame = ttk.Frame(self.main_container, style="Footer.TFrame")
        self.footer_frame.pack(fill="x", side="bottom")
        
        # Main content area - pack after footer
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create left and right columns for the 4 main frames
        self.left_column = ttk.Frame(self.content_frame)
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.right_column = ttk.Frame(self.content_frame)
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Configure main grid (left column, right column, execute button)
        self.content_frame.grid_columnconfigure(0, weight=1, uniform="cols")
        self.content_frame.grid_columnconfigure(1, weight=1, uniform="cols")
        self.content_frame.grid_rowconfigure(0, weight=1)  # Main frames row
        self.content_frame.grid_rowconfigure(1, weight=0)  # Execute button row
        
        # Configure left column - equal rows
        self.left_column.grid_rowconfigure(0, weight=1, uniform="left_rows")
        self.left_column.grid_rowconfigure(1, weight=1, uniform="left_rows")
        self.left_column.grid_columnconfigure(0, weight=1)
        
        # Configure right column - Plotting smaller, Results larger
        self.right_column.grid_rowconfigure(0, weight=1)  # Plotting - smaller (less space)
        self.right_column.grid_rowconfigure(1, weight=8)  # Results - much larger (more space)
        self.right_column.grid_columnconfigure(0, weight=1)

    def build_header(self):
        """Build the application header"""
        # Main title
        self.header_title = ttk.Label(
            self.header_frame,
            text="🗂️ Ingredients Visualizer",
            style="Header.TLabel"
        )
        self.header_title.pack(side="left", padx=20, pady=15)
        
        # Subtitle
        self.header_subtitle = ttk.Label(
            self.header_frame,
            text="Advanced Database Query and Visualization Tool",
            style="Header.TLabel",
            font=("Arial", 12)
        )
        self.header_subtitle.pack(side="left", padx=(0, 20), pady=15)
        

    def build_main_content(self):
        """Build the main content area with three organized sections"""
        # Create the three main sections with cards
        self.create_query_configuration_section()
        self.create_analysis_tools_section()
        self.create_detail_filters_section()
        self.create_results_section()
        self.create_execute_button_section()

    def create_query_configuration_section(self):
        """Create the query configuration section (top-left)"""
        self.first_frame = ttk.LabelFrame(
            self.left_column,
            text="⚙️ Query Configuration",
            style="Card.TFrame",
            padding=20
        )
        self.first_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        self.build_first_frame()

    def create_analysis_tools_section(self):
        """Create the plotting section (top-right)"""
        self.second_frame = ttk.LabelFrame(
            self.right_column,
            text="📊 Plotting",
            style="Card.TFrame",
            padding=20
        )
        self.second_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        self.build_second_frame()

    def create_detail_filters_section(self):
        """Create the detail filters section (bottom-left)"""
        self.third_frame = ttk.LabelFrame(
            self.left_column,
            text="🔧 Detailed Query Configuration",
            style="Card.TFrame",
            padding=20
        )
        self.third_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        
        self.build_third_frame()

    def create_results_section(self):
        """Create the results information section (bottom-right)"""
        self.results_frame = ttk.LabelFrame(
            self.right_column,
            text="📈 Results & Information",
            style="Card.TFrame",
            padding=20
        )
        self.results_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        
        self.build_results_info_section()

    def create_execute_button_section(self):
        """Create the execute button section (centered, bottom)"""
        self.execute_frame = ttk.LabelFrame(
            self.content_frame,
            text="⚡ Execute",
            style="Card.TFrame",
            padding=15
        )
        self.execute_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Create the execute button with bigger font (font configured in style.py)
        self.execute_button = ttk.Button(
            self.execute_frame,
            text="🚀 Execute Query",
            command=self.choose_correct_query,
            style="Action.TButton"
        )
        self.execute_button.pack(expand=True, ipadx=40, ipady=12)

    def build_footer(self):
        """Build the application footer"""
        # Status information
        self.status_label = ttk.Label(
            self.footer_frame,
            text="Ready - Select your query parameters and analysis tools",
            style="Footer.TLabel"
        )
        self.status_label.pack(side="left", padx=20, pady=15)
        
        # Version and credits
        self.credits_label = ttk.Label(
            self.footer_frame,
            text="© 2025 Ingredients Visualizer v1.0 | Advanced Query Interface",
            style="Footer.TLabel"
        )
        self.credits_label.pack(side="right", padx=20, pady=15)
    
    # ----------------- Query Configuration Section -----------------------------------------------------------------
    
    def build_first_frame(self):
        """Build the query configuration section with enhanced layout"""
        
        # Create a canvas and scrollbar for scrolling
        self.first_canvas = tk.Canvas(self.first_frame, highlightthickness=0)
        self.first_scrollbar = ttk.Scrollbar(self.first_frame, orient="vertical", command=self.first_canvas.yview)
        self.first_scrollable_frame = ttk.Frame(self.first_canvas)
        
        # Configure the canvas
        self.first_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.first_canvas.configure(scrollregion=self.first_canvas.bbox("all"))
        )
        
        # Create window with padding on the right to space widgets from scrollbar
        self.first_canvas.create_window((0, 0), window=self.first_scrollable_frame, anchor="nw", width=self.first_canvas.winfo_reqwidth())
        self.first_canvas.configure(yscrollcommand=self.first_scrollbar.set)
        
        # Pack the scrollbar close to right border and canvas with space for widgets
        self.first_scrollbar.pack(side="right", fill="y", padx=(0, 1))
        self.first_canvas.pack(side="left", fill="both", expand=True)
        
        # Update canvas window width when canvas is resized
        def _configure_canvas(event):
            # Set the width of the scrollable frame to match canvas width minus scrollbar width and spacing
            canvas_width = event.width - 15  # Account for scrollbar width and spacing
            self.first_canvas.itemconfig(self.first_canvas.find_withtag("all")[0], width=canvas_width)
        
        self.first_canvas.bind("<Configure>", _configure_canvas)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            self.first_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.first_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Section description
        description_label = ttk.Label(
            self.first_scrollable_frame, 
            text="Configure your database query parameters:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))

        # Plan Generator section
        pg_label = ttk.Label(self.first_scrollable_frame, text="🎯 Plan Generator:", font=("Arial", 10, "bold"))
        pg_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_plan_generator = PopoverMultiSelect(
            self.first_scrollable_frame,
            header="Select Plan Generator",
            items=get_values_for_dropdown("plan_generator", "pg_name"),
            width=35
        )
        self.ms_plan_generator.pack(fill="x", pady=(0, 10))

        # Cardinality Provider section
        cp_label = ttk.Label(self.first_scrollable_frame, text="📊 Cardinality Provider:", font=("Arial", 10, "bold"))
        cp_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_cardinality_provider = PopoverMultiSelect(
            self.first_scrollable_frame,
            header="Select Cardinality Provider",
            items=get_values_for_dropdown("card_provider", "cp_name"),
            width=35
        )
        self.ms_cardinality_provider.pack(fill="x", pady=(0, 10))

        # Build Plan Class section
        bpc_label = ttk.Label(self.first_scrollable_frame, text="🏗️ Build Plan Class:", font=("Arial", 10, "bold"))
        bpc_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_build_plan_class = PopoverMultiSelect(
            self.first_scrollable_frame,
            header="Select Build Plan Class",
            items=get_values_for_dropdown("build_plan_class", "bpc_name"),
            width=35
        )
        self.ms_build_plan_class.pack(fill="x", pady=(0, 10))

        # Cost Function section
        cf_label = ttk.Label(self.first_scrollable_frame, text="💰 Cost Function Parameters:", font=("Arial", 10, "bold"))
        cf_label.pack(anchor="w", pady=(5, 2))

        self.ms_cf_mat = PopoverMultiSelect(
            self.first_scrollable_frame,
            header="bpi_cf_mat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_mat"),
            width=35
        )
        
        self.ms_cf_concat = PopoverMultiSelect(
            self.first_scrollable_frame,
            header="bpi_cf_concat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_concat"),
            width=35
        )
        
        self.ms_cf_join_bundle = PopoverMultiSelect(
            self.first_scrollable_frame,
            header="bpi_cf_join_bundle",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_join_bundle"),
            width=35
        )
        
        self.ms_cf_host_id = PopoverMultiSelect(
            self.first_scrollable_frame,
            header="wp_cf_host_id",
            items=get_values_for_dropdown("work_package", "wp_cf_host_id"),
            width=35
        )

        self.msplus_cost_function = MultiSelectPlus(
            self.first_scrollable_frame,
            header="Advanced Cost Function Configuration",
            items=[
                self.ms_cf_mat,
                self.ms_cf_concat,
                self.ms_cf_join_bundle,
                self.ms_cf_host_id
            ],
            width=35
        )
        self.msplus_cost_function.pack(fill="x", pady=(0, 15))

    # ----------------- Plotting Section -----------------------------------------------------------------------------
    
    def build_second_frame(self):
        """Build the plotting section with plot type selection and axis configuration"""
        
        # Use a simple frame without scrollbar
        self.second_scrollable_frame = ttk.Frame(self.second_frame)
        self.second_scrollable_frame.pack(fill="both", expand=True)
        
        # Section description
        description_label = ttk.Label(
            self.second_scrollable_frame, 
            text="Configure your plot visualization:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Plot Type section
        plot_type_label = ttk.Label(self.second_scrollable_frame, text="📊 Plot Type:", font=("Arial", 10, "bold"))
        plot_type_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_plot_type = PopoverMultiSelect(
            self.second_scrollable_frame,
            header="Select Plot Type",
            items=["Bar Chart", "Box Plot", "Graph", "Scatter Plot"],
            width=35
        )
        self.ms_plot_type.pack(fill="x", pady=(0, 10))
        
        # Bind to update dependent controls when plot type changes
        original_plot_type_close = self.ms_plot_type._close
        def plot_type_close_with_update():
            original_plot_type_close()
            self.update_plot_type_dependent_controls()
        self.ms_plot_type._close = plot_type_close_with_update
        
        # Metric section
        metric_label = ttk.Label(self.second_scrollable_frame, text="📈 Metric:", font=("Arial", 10, "bold"))
        metric_label.pack(anchor="w", pady=(5, 2))
        
        # Create a horizontal frame for metric selectors and number input
        metric_frame = ttk.Frame(self.second_scrollable_frame)
        metric_frame.pack(fill="x", pady=(0, 15))
        
        # Aggregation metric selector on the left (avg, median, etc.)
        agg_metric_frame = ttk.Frame(metric_frame)
        agg_metric_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.ms_agg_metric = PopoverMultiSelect(
            agg_metric_frame,
            header="Select Aggregation",
            items=[],  # Start with empty items, will be populated based on Analysis Parameter
            width=18
        )
        self.ms_agg_metric.pack(fill="x")
        
        # Highest/Lowest metric selector in the middle
        metric_select_frame = ttk.Frame(metric_frame)
        metric_select_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        self.ms_metric = PopoverMultiSelect(
            metric_select_frame,
            header="Select Metric",
            items=["Highest", "Lowest"],
            width=18
        )
        self.ms_metric.pack(fill="x")
        
        # Number input on the right - aligned vertically with popovers
        number_input_frame = ttk.Frame(metric_frame)
        number_input_frame.pack(side="left", fill="y", padx=(5, 0))
        
        self.plot_number_var = tk.StringVar(value="5")
        self.plot_number_var.trace_add("write", lambda *args: self.validate_plot_number_input())
        self.plot_number_entry = ttk.Entry(number_input_frame, textvariable=self.plot_number_var, width=10)
        self.plot_number_entry.pack(fill="both", expand=True)
        
        # Bind events to ensure Entry remains responsive
        self.plot_number_entry.bind("<Button-1>", self.on_entry_click)
        self.plot_number_entry.bind("<FocusIn>", self.on_entry_focus)
        self.plot_number_entry.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
    # ------------------------------ Detail Filters Section --------------------------------------------------------

    def build_third_frame(self):
        """Build the detail filters section with dynamic filter rows and scrollbar"""
        
        # Create a canvas and scrollbar for scrolling
        self.third_canvas = tk.Canvas(self.third_frame, highlightthickness=0)
        self.third_scrollbar = ttk.Scrollbar(self.third_frame, orient="vertical", command=self.third_canvas.yview)
        self.third_scrollable_frame = ttk.Frame(self.third_canvas)
        
        # Configure the canvas
        self.third_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.third_canvas.configure(scrollregion=self.third_canvas.bbox("all"))
        )
        
        # Create window with padding on the right to space widgets from scrollbar
        self.third_canvas.create_window((0, 0), window=self.third_scrollable_frame, anchor="nw", width=self.third_canvas.winfo_reqwidth())
        self.third_canvas.configure(yscrollcommand=self.third_scrollbar.set)
        
        # Pack the scrollbar close to right border and canvas with space for widgets
        self.third_scrollbar.pack(side="right", fill="y", padx=(0, 1))
        self.third_canvas.pack(side="left", fill="both", expand=True)
        
        # Update canvas window width when canvas is resized
        def _configure_canvas(event):
            # Set the width of the scrollable frame to match canvas width minus scrollbar width and spacing
            canvas_width = event.width - 15  # Account for scrollbar width and spacing
            self.third_canvas.itemconfig(self.third_canvas.find_withtag("all")[0], width=canvas_width)
        
        self.third_canvas.bind("<Configure>", _configure_canvas)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            self.third_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.third_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Section description
        description_label = ttk.Label(
            self.third_scrollable_frame, 
            text="Configure query parameters and filters:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))

        # Analysis Parameter section
        analysis_label = ttk.Label(self.third_scrollable_frame, text="🔍 Analysis Parameter:", font=("Arial", 10, "bold"))
        analysis_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_analysis_parameter = PopoverMultiSelect(
            self.third_scrollable_frame,
            header="* Select Analysis Parameter",
            items=["Loss Factor Analysis", "Q-Error Analysis", "P-Error Analysis"],
            width=35
        )
        self.ms_analysis_parameter.pack(fill="x", pady=(0, 10))
        
        # Bind to update aggregation items when analysis parameter changes
        original_close = self.ms_analysis_parameter._close
        def close_with_update():
            original_close()
            self.update_aggregation_items()
        self.ms_analysis_parameter._close = close_with_update
        
        # Query Selection section (permanently visible)
        query_label = ttk.Label(
            self.third_scrollable_frame, 
            text="📋 Query Selection:", 
            font=("Arial", 10, "bold")
        )
        query_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_query_selection = PopoverMultiSelect(
            self.third_scrollable_frame,
            header="Select Query",
            items=get_values_for_dropdown("query_graph", "qg_name"),
            width=35
        )
        self.ms_query_selection.pack(fill="x", pady=(0, 10))
        
        # Bind to update aggregation availability when query selection changes
        original_query_close = self.ms_query_selection._close
        def query_close_with_update():
            original_query_close()
            self.update_aggregation_availability()
        self.ms_query_selection._close = query_close_with_update
        
        # Filter configuration label
        filter_label = ttk.Label(
            self.third_scrollable_frame, 
            text="Filter Configuration:",
            font=("Arial", 10, "bold")
        )
        filter_label.pack(anchor="w", pady=(5, 2))

        # Container for all filter rows
        self.filter_rows_container = ttk.Frame(self.third_scrollable_frame)
        self.filter_rows_container.pack(fill="x", pady=(0, 10))
        
        # List to store filter row widgets (initialize only once)
        if not hasattr(self, 'filter_rows'):
            self.filter_rows = []
            
            # Add the first filter row
            self.add_filter_row()
        
        # Add button container (centered)
        button_container = ttk.Frame(self.third_scrollable_frame)
        button_container.pack(fill="x", pady=(5, 10))
        
        # Create a sub-container to center both buttons
        buttons_frame = ttk.Frame(button_container)
        buttons_frame.pack(anchor="center")
        
        # "+" button to add new filter rows
        add_button = ttk.Button(
            buttons_frame,
            text="+ Add Filter",
            command=self.add_filter_row,
            width=15
        )
        add_button.pack(side="left", padx=5)
        
        # "-" button to remove last filter row
        delete_button = ttk.Button(
            buttons_frame,
            text="− Remove Filter",
            command=self.remove_last_filter_row,
            width=15
        )
        delete_button.pack(side="left", padx=5)
        
    def add_filter_row(self):
        """Add a new filter row with metric, comparison, and value widgets"""
        from gui.multiSelect import PopoverMultiSelect
        
        # Create a frame for this filter row
        row_frame = ttk.Frame(self.filter_rows_container)
        row_frame.pack(fill="x", pady=5)
        
        # Create a dictionary to store widgets for this row
        row_widgets = {}
        
        # Column 1: Filter Metrics (PopoverMultiSelect)
        metric_frame = ttk.Frame(row_frame)
        metric_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Determine which metrics to show based on query selection mode
        selected_queries = self.ms_query_selection.get_selected() if hasattr(self, 'ms_query_selection') else []
        if selected_queries and len(selected_queries) > 0:
            # Query mode - use raw metrics
            all_metrics = ["lf", "qerr", "perr"]
        else:
            # Aggregated mode - use aggregated metrics
            all_metrics = ["avg_lf", "median_lf", "max_lf", "min_lf", "avg_qerr", "median_qerr", "max_qerr", "min_qerr", "avg_perr", "median_perr", "max_perr", "min_perr"]
        
        metric_select = PopoverMultiSelect(
            metric_frame,
            header="Select Metric",
            items=all_metrics,
            width=20,
            height=6
        )
        metric_select.pack(fill="x")
        row_widgets['metric_select'] = metric_select
        
        # Column 2: Comparison Type (PopoverMultiSelect)
        comparison_frame = ttk.Frame(row_frame)
        comparison_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        comparison_select = PopoverMultiSelect(
            comparison_frame,
            header="Select Comparison",
            items=["greater than", "less than", "equal", "between"],
            width=20,
            height=4
        )
        comparison_select.pack(fill="x")
        row_widgets['comparison_select'] = comparison_select
        
        # Column 3: Filter Value (Entry)
        value_frame = ttk.Frame(row_frame)
        value_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        value_var = tk.StringVar()
        # Add validation callback to restrict to numerical values and convert commas to dots
        value_var.trace_add("write", lambda *args: self.validate_numerical_input(value_var, value_entry))
        value_entry = ttk.Entry(value_frame, textvariable=value_var)
        value_entry.pack(fill="x")
        row_widgets['value_var'] = value_var
        row_widgets['value_entry'] = value_entry
        
        # Bind events to ensure Entry remains responsive
        value_entry.bind("<Button-1>", self.on_entry_click)
        value_entry.bind("<FocusIn>", self.on_entry_focus)
        value_entry.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
        # Store the row frame and widgets
        row_widgets['frame'] = row_frame
        self.filter_rows.append(row_widgets)
        
        print(f"Added filter row #{len(self.filter_rows)}")
        
    def remove_last_filter_row(self):
        """Remove the last filter row (but keep at least one row)"""
        if len(self.filter_rows) <= 1:
            self.update_status("Cannot remove the last filter row")
            print("Cannot remove the last filter row - at least one row must remain")
            return
        
        # Get the last row
        last_row = self.filter_rows.pop()
        
        # Destroy the frame and all its widgets
        frame = last_row.get('frame')
        if frame:
            frame.destroy()
        
        print(f"Removed filter row. Remaining rows: {len(self.filter_rows)}")
        self.update_status(f"Filter row removed - {len(self.filter_rows)} row(s) remaining")
        
    def validate_numerical_input(self, string_var, entry_widget):
        """Validate and normalize numerical input: only allow numbers, dots, minus, semicolons, and convert commas to dots"""
        # Prevent recursive calls
        validation_attr = f'_validating_{id(string_var)}'
        if hasattr(self, validation_attr) and getattr(self, validation_attr):
            return
        
        setattr(self, validation_attr, True)
        try:
            current_text = string_var.get()
            cursor_pos = entry_widget.index(tk.INSERT)
            
            # Normalize: replace comma with dot
            normalized_text = current_text.replace(',', '.')
            
            # Validate: only allow digits, dots, minus sign, semicolon, and spaces
            valid_chars = set('0123456789.-; ')
            filtered_text = ''.join(c for c in normalized_text if c in valid_chars)
            
            # Split by semicolon to validate each part separately (for "between" case)
            parts = filtered_text.split(';')
            validated_parts = []
            
            for part in parts:
                part = part.strip()
                
                # Prevent multiple dots in each part
                if part.count('.') > 1:
                    dot_parts = part.split('.')
                    part = dot_parts[0] + '.' + ''.join(dot_parts[1:])
                
                # Prevent multiple minus signs and ensure minus is only at the beginning
                if part.count('-') > 1:
                    part = part.replace('-', '', part.count('-') - 1)
                if '-' in part and part.index('-') != 0:
                    part = '-' + part.replace('-', '')
                
                validated_parts.append(part)
            
            # Rejoin with semicolon (max 2 parts for "between")
            filtered_text = ';'.join(validated_parts[:2])
            
            # Update if changed
            if filtered_text != current_text:
                string_var.set(filtered_text)
                # Restore cursor position
                try:
                    entry_widget.icursor(min(cursor_pos, len(filtered_text)))
                except tk.TclError:
                    pass
        finally:
            setattr(self, validation_attr, False)
    
    def validate_plot_number_input(self):
        """Validate plot number input: only allow positive integers"""
        # Prevent recursive calls
        if hasattr(self, '_validating_plot_number') and self._validating_plot_number:
            return
        
        self._validating_plot_number = True
        try:
            current_text = self.plot_number_var.get()
            cursor_pos = self.plot_number_entry.index(tk.INSERT)
            
            # Validate: only allow digits (positive integers only)
            filtered_text = ''.join(c for c in current_text if c.isdigit())
            
            # Update if changed
            if filtered_text != current_text:
                self.plot_number_var.set(filtered_text)
                # Restore cursor position
                try:
                    self.plot_number_entry.icursor(min(cursor_pos, len(filtered_text)))
                except tk.TclError:
                    pass
        finally:
            self._validating_plot_number = False
        
        
        
    def build_results_info_section(self):
        """Build the results information section"""
        
        # Section description
        description_label = ttk.Label(
            self.results_frame, 
            text="Query results and statistics:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Open in fullscreen button - pack FIRST with side=bottom to reserve space
        self.fullscreen_button = ttk.Button(
            self.results_frame,
            text="⛶ Open in Fullscreen",
            command=self.open_results_fullscreen
        )
        self.fullscreen_button.pack(fill="x", side="bottom")
        
        # Container frame for results (will hold either treeview or plot)
        self.results_container = ttk.Frame(self.results_frame, style="Card.TFrame")
        self.results_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Initialize with empty message
        self.empty_results_label = ttk.Label(
            self.results_container,
            text="No results yet. Execute a query to see results here.",
            font=("Arial", 10, "italic"),
            foreground="#7f8c8d"
        )
        self.empty_results_label.pack(expand=True)
        
    def on_detail_input_change(self, *args):
        """Normalize and validate number input - replace commas with dots and allow only valid number characters"""
        # Prevent recursive calls
        if hasattr(self, '_updating_detail_1') and self._updating_detail_1:
            return
        
        self._updating_detail_1 = True
        try:
            current_text = self.eingabe_detail.get()
            cursor_pos = self.eingabe_detail_entry.index(tk.INSERT)
            
            # Normalize: replace comma with dot
            normalized_text = current_text.replace(',', '.')
            
            # Validate: only allow digits, dots, minus sign, and spaces
            valid_chars = set('0123456789.- ')
            filtered_text = ''.join(c for c in normalized_text if c in valid_chars)
            
            # Prevent multiple dots
            if filtered_text.count('.') > 1:
                # Keep only the first dot
                parts = filtered_text.split('.')
                filtered_text = parts[0] + '.' + ''.join(parts[1:])
            
            # Update if changed
            if filtered_text != current_text:
                self.eingabe_detail.set(filtered_text)
                # Restore cursor position
                try:
                    self.eingabe_detail_entry.icursor(cursor_pos)
                except tk.TclError:
                    pass
            
            print("Detail Input Changed:", filtered_text)
            self.update_status(f"Filter value updated: {filtered_text}")
        finally:
            self._updating_detail_1 = False

    def on_detail_input_change_2(self, *args):
        """Normalize and validate number input for second entry field"""
        # Prevent recursive calls
        if hasattr(self, '_updating_detail_2') and self._updating_detail_2:
            return
        
        self._updating_detail_2 = True
        try:
            current_text = self.eingabe_detail_2_var.get()
            cursor_pos = self.eingabe_detail_2.index(tk.INSERT)
            
            # Normalize: replace comma with dot
            normalized_text = current_text.replace(',', '.')
            
            # Validate: only allow digits, dots, minus sign, and spaces
            valid_chars = set('0123456789.- ')
            filtered_text = ''.join(c for c in normalized_text if c in valid_chars)
            
            # Prevent multiple dots
            if filtered_text.count('.') > 1:
                # Keep only the first dot
                parts = filtered_text.split('.')
                filtered_text = parts[0] + '.' + ''.join(parts[1:])
            
            # Update if changed
            if filtered_text != current_text:
                self.eingabe_detail_2_var.set(filtered_text)
                # Restore cursor position
                try:
                    self.eingabe_detail_2.icursor(cursor_pos)
                except tk.TclError:
                    pass
            
            print("Detail Input 2 Changed:", filtered_text)
            self.update_status(f"Filter value 2 updated: {filtered_text}")
        finally:
            self._updating_detail_2 = False
    
    def update_metric_fields(self):
        """Update available metrics in filter rows based on selected analysis type"""
        selected_analysis = self.ms_analysis_parameter.get_selected()
        
        if not selected_analysis:
            return
        
        analysis_type = selected_analysis[0] if selected_analysis else ""
        
        # Define metric mappings
        metrics_map = {
            "Loss Factor Analysis": ["avg_lf", "median_lf", "max_lf"],
            "Q-Error Analysis": ["avg_qerr", "median_qerr", "max_qerr"],
            "P-Error Analysis": ["avg_perr", "median_perr", "max_perr"]
        }
        
        metrics = metrics_map.get(analysis_type, [])
        
        # Update available metrics in all filter rows
        if hasattr(self, 'filter_rows') and metrics:
            for row in self.filter_rows:
                metric_select = row.get('metric_select')
                if metric_select:
                    # Update the available items in the metric selector
                    metric_select.set_items(metrics)

    def open_results_fullscreen(self):
        """Open current results in fullscreen window"""
        if hasattr(self, 'current_results_data') and self.current_results_data:
            result_type = self.current_results_data.get('type')
            
            if result_type == 'treeview':
                # Open treeview in fullscreen
                from plotting.treeview import plot_treeview
                plot_treeview(
                    self.current_results_data['columns'],
                    self.current_results_data['data'],
                    self.current_results_data['params_summary']
                )
            elif result_type == 'plot':
                # Open plot in fullscreen
                from plotting.plotting import create_plot_window
                create_plot_window(
                    self.current_results_data['columns'],
                    self.current_results_data['data'],
                    self.current_results_data['params_summary'],
                    self.current_results_data['plot_type'],
                    self.current_results_data.get('x_axis'),
                    self.current_results_data.get('y_axis'),
                    self.current_results_data.get('agg_metric'),
                    self.current_results_data.get('metric'),
                    self.current_results_data.get('plot_number', 5),
                    self.current_results_data.get('config_params')
                )
        else:
            self.update_status("No results available. Execute a query first.")

    def update_aggregation_items(self):
        """Update aggregation items based on selected analysis parameter"""
        selected_analysis = self.ms_analysis_parameter.get_selected()
        
        if not selected_analysis or len(selected_analysis) == 0:
            # No analysis parameter selected - clear aggregation items
            self.ms_agg_metric.set_items([])
        else:
            analysis_type = selected_analysis[0]
            
            # Map analysis type to metric suffix
            if analysis_type == "Loss Factor Analysis":
                metrics = ["avg_lf", "median_lf", "max_lf", "min_lf"]
            elif analysis_type == "Q-Error Analysis":
                metrics = ["avg_qerr", "median_qerr", "max_qerr", "min_qerr"]
            elif analysis_type == "P-Error Analysis":
                metrics = ["avg_perr", "median_perr", "max_perr", "min_perr"]
            else:
                metrics = []
            
            self.ms_agg_metric.set_items(metrics)
    
    def update_aggregation_availability(self):
        """Enable/disable aggregation popover based on query selection and update filter row metrics"""
        selected_queries = self.ms_query_selection.get_selected()
        
        if selected_queries and len(selected_queries) > 0:
            # Query mode - disable aggregation selection
            self.ms_agg_metric.button.config(state="disabled")
            self.ms_agg_metric.button.config(style="Disabled.TButton")
            # Reset to default header when disabled
            self.ms_agg_metric._var.set(self.ms_agg_metric._header)
            
            # Update filter row metrics to raw values (lf, qerr, perr) for single query mode
            self.update_filter_row_metrics_for_query_mode(query_mode=True)
        else:
            # Aggregated mode - enable aggregation selection
            self.ms_agg_metric.button.config(state="normal")
            self.ms_agg_metric.button.config(style="TButton")
            
            # Update filter row metrics to aggregated values (avg_lf, median_lf, etc.)
            self.update_filter_row_metrics_for_query_mode(query_mode=False)
        
        # Also update plot type dependent controls
        self.update_plot_type_dependent_controls()
    
    def update_plot_type_dependent_controls(self):
        """Enable/disable Metric popover and number entry based on plot type selection"""
        selected_plot_types = self.ms_plot_type.get_selected()
        
        # Check if aggregation is active (not disabled)
        agg_is_active = str(self.ms_agg_metric.button.cget('state')) == 'normal'
        
        # Update aggregation header based on plot type selection and active state
        if selected_plot_types and len(selected_plot_types) > 0 and agg_is_active:
            # Plot type selected AND aggregation is active - add asterisk
            self.ms_agg_metric._header = "* Select Aggregation"
        else:
            # No plot type or aggregation is disabled - no asterisk
            self.ms_agg_metric._header = "Select Aggregation"
        
        # Update button text if no selection
        if len(self.ms_agg_metric.get_selected()) == 0:
            self.ms_agg_metric._var.set(self.ms_agg_metric._header)
        
        if selected_plot_types and "Box Plot" in selected_plot_types:
            # Box Plot selected - disable Metric popover and number entry
            self.ms_metric.button.config(state="disabled")
            self.ms_metric.button.config(style="Disabled.TButton")
            # Reset to default header when disabled
            self.ms_metric._var.set(self.ms_metric._header)
            self.plot_number_entry.config(state="disabled")
        else:
            # Other plot types - enable Metric popover and number entry
            self.ms_metric.button.config(state="normal")
            self.ms_metric.button.config(style="TButton")
            self.plot_number_entry.config(state="normal")
    
    def update_filter_row_metrics_for_query_mode(self, query_mode=False):
        """Update available metrics in filter rows based on query selection mode"""
        if query_mode:
            # Query mode - use raw metrics (lf, qerr, perr)
            metrics = ["lf", "qerr", "perr"]
        else:
            # Aggregated mode - use aggregated metrics
            metrics = ["avg_lf", "median_lf", "max_lf", "min_lf", "avg_qerr", "median_qerr", "max_qerr", "min_qerr", "avg_perr", "median_perr", "max_perr", "min_perr"]
        
        # Update available metrics in all filter rows
        if hasattr(self, 'filter_rows'):
            for row in self.filter_rows:
                metric_select = row.get('metric_select')
                if metric_select:
                    # Update the available items in the metric selector
                    metric_select.set_items(metrics)

    def update_status(self, message):
        """Update the status message in the footer"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def restore_entry_focus(self):
        """Restore focus capabilities to Entry widgets after other operations"""
        try:
            # Ensure all filter row Entry widgets are properly enabled and can receive focus
            if hasattr(self, 'filter_rows'):
                for row in self.filter_rows:
                    value_entry = row.get('value_entry')
                    if value_entry and value_entry.winfo_exists():
                        value_entry.config(state='normal')
                        value_entry.update_idletasks()
            
        except tk.TclError:
            # Handle case where widgets have been destroyed
            pass
    
    def get_detail_filter_values(self):
        """
        Get all detail filter values from all filter rows.
        
        Returns:
            list: List of filter dictionaries, each containing:
                - 'metric': Selected metric (e.g., 'avg_lf')
                - 'comparison': Selected comparison type (e.g., 'greater than', 'between')
                - 'value': Numeric value from entry field (as float, tuple for 'between', or None)
        """
        filters = []
        
        # Iterate through all filter rows
        if hasattr(self, 'filter_rows'):
            for i, row in enumerate(self.filter_rows):
                filter_dict = {
                    'metric': None,
                    'comparison': None,
                    'value': None
                }
                
                # Get metric selection
                metric_select = row.get('metric_select')
                if metric_select:
                    selected_metrics = metric_select.get_selected()
                    if selected_metrics:
                        filter_dict['metric'] = selected_metrics[0]  # Take first selected metric
                
                # Get comparison selection
                comparison_select = row.get('comparison_select')
                if comparison_select:
                    selected_comparisons = comparison_select.get_selected()
                    if selected_comparisons:
                        filter_dict['comparison'] = selected_comparisons[0]
                
                # Get value
                value_var = row.get('value_var')
                if value_var:
                    value_str = value_var.get().strip()
                    if value_str:
                        # Check if this is a "between" value (contains semicolon)
                        if ';' in value_str and filter_dict['comparison'] == 'between':
                            try:
                                parts = value_str.split(';')
                                if len(parts) >= 2:
                                    val1 = float(parts[0].strip())
                                    val2 = float(parts[1].strip())
                                    # Ensure val1 <= val2 for BETWEEN syntax
                                    filter_dict['value'] = (min(val1, val2), max(val1, val2))
                            except ValueError:
                                filter_dict['value'] = None
                        else:
                            try:
                                filter_dict['value'] = float(value_str)
                            except ValueError:
                                filter_dict['value'] = None
                
                # Only add filter if it has at least a metric selected
                if filter_dict['metric']:
                    filters.append(filter_dict)
                    print(f"Filter row {i+1}: {filter_dict}")
        
        return filters


# =============================================================================
# RUN METHOD
# =============================================================================

    def run(self):
        """Start the main application loop."""
        self.mainloop()