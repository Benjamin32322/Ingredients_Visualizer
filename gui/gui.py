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
        
        # Main content area with grid layout
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Configure grid weights for responsive layout
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=0)  # Execute button row - no expansion
        
        # Footer section
        self.footer_frame = ttk.Frame(self.main_container, style="Footer.TFrame")
        self.footer_frame.pack(fill="x")

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
            self.content_frame,
            text="📊 Query Configuration",
            style="Card.TFrame",
            padding=20
        )
        self.first_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))
        
        self.build_first_frame()

    def create_analysis_tools_section(self):
        """Create the plotting section (top-right)"""
        self.second_frame = ttk.LabelFrame(
            self.content_frame,
            text="� Plotting",
            style="Card.TFrame",
            padding=20
        )
        self.second_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        self.build_second_frame()

    def create_detail_filters_section(self):
        """Create the detail filters section (bottom-left)"""
        self.third_frame = ttk.LabelFrame(
            self.content_frame,
            text="🔧 Detailed Query Configuration",
            style="Card.TFrame",
            padding=20
        )
        self.third_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(5, 0))
        
        self.build_third_frame()

    def create_results_section(self):
        """Create the results information section (bottom-right)"""
        self.results_frame = ttk.LabelFrame(
            self.content_frame,
            text="📈 Results & Information",
            style="Card.TFrame",
            padding=20
        )
        self.results_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
        
        self.build_results_info_section()

    def create_execute_button_section(self):
        """Create the execute button section (centered, bottom)"""
        self.execute_frame = ttk.LabelFrame(
            self.content_frame,
            text="⚡ Execute",
            style="Card.TFrame",
            padding=15
        )
        self.execute_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=(10, 0))
        
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
        
        # Section description
        description_label = ttk.Label(
            self.first_frame, 
            text="Configure your database query parameters:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))

        # Plan Generator section
        pg_label = ttk.Label(self.first_frame, text="🎯 Plan Generator:", font=("Arial", 10, "bold"))
        pg_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_plan_generator = PopoverMultiSelect(
            self.first_frame,
            header="Select Plan Generator",
            items=get_values_for_dropdown("plan_generator", "pg_name"),
            width=35
        )
        self.ms_plan_generator.pack(fill="x", pady=(0, 10))

        # Cardinality Provider section
        cp_label = ttk.Label(self.first_frame, text="📊 Cardinality Provider:", font=("Arial", 10, "bold"))
        cp_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_cardinality_provider = PopoverMultiSelect(
            self.first_frame,
            header="Select Cardinality Provider",
            items=get_values_for_dropdown("card_provider", "cp_name"),
            width=35
        )
        self.ms_cardinality_provider.pack(fill="x", pady=(0, 10))

        # Build Plan Class section
        bpc_label = ttk.Label(self.first_frame, text="🏗️ Build Plan Class:", font=("Arial", 10, "bold"))
        bpc_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_build_plan_class = PopoverMultiSelect(
            self.first_frame,
            header="Select Build Plan Class",
            items=get_values_for_dropdown("build_plan_class", "bpc_name"),
            width=35
        )
        self.ms_build_plan_class.pack(fill="x", pady=(0, 10))

        # Cost Function section
        cf_label = ttk.Label(self.first_frame, text="💰 Cost Function Parameters:", font=("Arial", 10, "bold"))
        cf_label.pack(anchor="w", pady=(5, 2))

        self.ms_cf_mat = PopoverMultiSelect(
            self.first_frame,
            header="bpi_cf_mat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_mat"),
            width=35
        )
        
        self.ms_cf_concat = PopoverMultiSelect(
            self.first_frame,
            header="bpi_cf_concat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_concat"),
            width=35
        )
        
        self.ms_cf_join_bundle = PopoverMultiSelect(
            self.first_frame,
            header="bpi_cf_join_bundle",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_join_bundle"),
            width=35
        )
        
        self.ms_cf_host_id = PopoverMultiSelect(
            self.first_frame,
            header="wp_cf_host_id",
            items=get_values_for_dropdown("work_package", "wp_cf_host_id"),
            width=35
        )

        self.msplus_cost_function = MultiSelectPlus(
            self.first_frame,
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
        
        # Section description
        description_label = ttk.Label(
            self.second_frame, 
            text="Configure your plot visualization:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Plot Type section
        plot_type_label = ttk.Label(self.second_frame, text="📊 Plot Type:", font=("Arial", 10, "bold"))
        plot_type_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_plot_type = PopoverMultiSelect(
            self.second_frame,
            header="Select Plot Type",
            items=["Bar Chart", "Box Plot", "Graph", "Scatter Plot"],
            width=35
        )
        self.ms_plot_type.pack(fill="x", pady=(0, 10))
        
        # X-Axis section
        x_axis_label = ttk.Label(self.second_frame, text="📐 X-Axis:", font=("Arial", 10, "bold"))
        x_axis_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_x_axis = PopoverMultiSelect(
            self.second_frame,
            header="Select X-Axis",
            items=["Configuration Parameters"],
            width=35
        )
        self.ms_x_axis.pack(fill="x", pady=(0, 10))
        
        # Y-Axis section
        y_axis_label = ttk.Label(self.second_frame, text="📏 Y-Axis:", font=("Arial", 10, "bold"))
        y_axis_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_y_axis = PopoverMultiSelect(
            self.second_frame,
            header="Select Y-Axis",
            items=["Loss Factor", "Q-Error", "P-Error"],
            width=35
        )
        self.ms_y_axis.pack(fill="x", pady=(0, 10))
        
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
        
        self.third_canvas.create_window((0, 0), window=self.third_scrollable_frame, anchor="nw")
        self.third_canvas.configure(yscrollcommand=self.third_scrollbar.set)
        
        # Pack the scrollbar and canvas
        self.third_scrollbar.pack(side="right", fill="y")
        self.third_canvas.pack(side="left", fill="both", expand=True)
        
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
            header="Select Analysis Parameter",
            items=["Loss Factor Analysis", "Q-Error Analysis", "P-Error Analysis", "Query Analysis", "Detail Query Analysis"],
            width=35
        )
        self.ms_analysis_parameter.pack(fill="x", pady=(0, 10))
        
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
        
        # Separator for visual distinction
        separator = ttk.Separator(self.third_scrollable_frame, orient="horizontal")
        separator.pack(fill="x", pady=(10, 15))
        
        # Filter configuration label
        filter_label = ttk.Label(
            self.third_scrollable_frame, 
            text="Filter Configuration:",
            font=("Arial", 10, "bold")
        )
        filter_label.pack(anchor="w", pady=(0, 10))

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
            text="− Remove Last",
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
        
        metric_label = ttk.Label(metric_frame, text="Filter Metric:", font=("Arial", 9))
        metric_label.pack(anchor="w")
        
        # All available metrics (not filtered by analysis type)
        all_metrics = ["avg_lf", "median_lf", "max_lf", "avg_qerr", "median_qerr", "max_qerr", "avg_perr", "median_perr", "max_perr"]
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
        
        comparison_label = ttk.Label(comparison_frame, text="Comparison:", font=("Arial", 9))
        comparison_label.pack(anchor="w")
        
        comparison_select = PopoverMultiSelect(
            comparison_frame,
            header="Select Comparison",
            items=["größer als", "kleiner als", "gleich", "zwischen"],
            width=20,
            height=4
        )
        comparison_select.pack(fill="x")
        row_widgets['comparison_select'] = comparison_select
        
        # Column 3: Filter Value (Entry)
        value_frame = ttk.Frame(row_frame)
        value_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        value_label = ttk.Label(value_frame, text="Value:", font=("Arial", 9))
        value_label.pack(anchor="w")
        
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
        """Validate and normalize numerical input: only allow numbers, dots, minus, and convert commas to dots"""
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
            
            # Validate: only allow digits, dots, minus sign, and spaces
            valid_chars = set('0123456789.- ')
            filtered_text = ''.join(c for c in normalized_text if c in valid_chars)
            
            # Prevent multiple dots
            if filtered_text.count('.') > 1:
                # Keep only the first dot
                parts = filtered_text.split('.')
                filtered_text = parts[0] + '.' + ''.join(parts[1:])
            
            # Prevent multiple minus signs and ensure minus is only at the beginning
            if filtered_text.count('-') > 1:
                # Keep only the first minus
                filtered_text = filtered_text.replace('-', '', filtered_text.count('-') - 1)
            if '-' in filtered_text and filtered_text.index('-') != 0:
                # Move minus to the beginning
                filtered_text = '-' + filtered_text.replace('-', '')
            
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
        
        
        
    def build_results_info_section(self):
        """Build the results information section"""
        # Section description
        description_label = ttk.Label(
            self.results_frame, 
            text="Query results and statistics:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Results summary
        self.results_text = tk.Text(
            self.results_frame, 
            height=10, 
            wrap="word",
            font=("Courier", 10),
            state="disabled"
        )
        self.results_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Clear results button
        self.clear_results_button = ttk.Button(
            self.results_frame,
            text="🗑️ Clear Results",
            command=self.clear_results
        )
        self.clear_results_button.pack(fill="x")

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

    def clear_results(self):
        """Clear the results display"""
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")
        self.update_status("Results cleared")

    def update_status(self, message):
        """Update the status message in the footer"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)

# ------------------------ RUN-METHODE --------------------------------------------------------------
    def run(self):
        self.mainloop()

        
        selected_pg = self.ms_plan_generator.get_selected()
        selected_cp = self.ms_cardinality_provider.get_selected()
        selected_cf = self.msplus_cost_function.get_selected()

        pg_filter = build_filter("pg_name", selected_pg)
        cp_filter = build_filter("cp_name", selected_cp)
        cf_filter = build_cost_filters(selected_cf)
        
        filters = {
            "PG_FILTER": pg_filter,
            "CP_FILTER": cp_filter
        }
        filters.update(cf_filter)
        columns, result = execute_query(1, filters=filters)

        plot_treeview(columns, result)
        
        # Update status and restore focus
        self.update_status(f"Loss Factor query executed - {len(result)} results found")
        self.after(100, self.restore_entry_focus)
    
    def execute_q_error(self):
        selected_pg = self.ms_plan_generator.get_selected()
        selected_cp = self.ms_cardinality_provider.get_selected()
        selected_cf = self.msplus_cost_function.get_selected()

        pg_filter = build_filter("pg_name", selected_pg)
        cp_filter = build_filter("cp_name", selected_cp)
        cf_filter = build_cost_filters(selected_cf)
        
        filters = {
            "PG_NAME_FILTER": pg_filter,
            "CP_NAME_FILTER": cp_filter
        }
        filters.update(cf_filter)
        columns, result = execute_query(3, filters=filters)

        plot_treeview(columns, result)
        
        # Update status and restore focus
        self.update_status(f"Q-Error analysis executed - {len(result)} results found")
        self.after(100, self.restore_entry_focus)

    def execute_p_error(self):
        selected_pg = self.ms_plan_generator.get_selected()
        selected_cp = self.ms_cardinality_provider.get_selected()
        selected_cf = self.msplus_cost_function.get_selected()

        pg_filter = build_filter("pg_name", selected_pg)
        cp_filter = build_filter("cp_name", selected_cp)
        cf_filter = build_cost_filters(selected_cf)
        
        filters = {
            "PG_NAME_FILTER": pg_filter,
            "CP_NAME_FILTER": cp_filter
        }
        filters.update(cf_filter)
        columns, result = execute_query(4, filters=filters)

        plot_treeview(columns, result)
        
        # Update status and restore focus
        self.update_status(f"P-Error analysis executed - {len(result)} results found")
        self.after(100, self.restore_entry_focus)
    
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
                - 'comparison': Selected comparison type (e.g., 'größer als', 'zwischen')
                - 'value': Numeric value from entry field (as float or None)
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
                        try:
                            filter_dict['value'] = float(value_str)
                        except ValueError:
                            filter_dict['value'] = None
                
                # Only add filter if it has at least a metric selected
                if filter_dict['metric']:
                    filters.append(filter_dict)
                    print(f"Filter row {i+1}: {filter_dict}")
        
        return filters
    
# ------------------------ RUN-METHODE --------------------------------------------------------------
    def run(self):
        self.mainloop()