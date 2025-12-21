import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from db.dbHandler import get_values_for_dropdown, build_filter, build_cost_filters, execute_query
from gui.multiSelect import PopoverMultiSelect, MultiSelectPlus
from gui.style import setup_application_styles
from gui.responsiveness import ResponsivenessMixin
from gui.query_handlers import QueryHandlersMixin
from plotting.plotting import plot_treeview



class GUI(ResponsivenessMixin, QueryHandlersMixin, tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ingredients Visualizer - Advanced Database Query Interface")
        
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
            current_state = self.state()
            if hasattr(self, '_last_state'):
                # If we're coming back from minimized state and not in fullscreen
                if (self._last_state == "iconic" and 
                    current_state == "normal" and 
                    not self.attributes("-fullscreen")):
                    self.geometry(self._default_geometry)
            self._last_state = current_state
            # Schedule next check
            self.after(100, _handle_window_state_change)
        
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
        
        # Start monitoring window state
        self.after(100, _handle_window_state_change)

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
        """Create the analysis tools section (top-right)"""
        self.second_frame = ttk.LabelFrame(
            self.content_frame,
            text="🔍 Analysis Parameter",
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
            padding=20
        )
        self.execute_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=(10, 0))
        
        # Create the execute button with larger size
        self.execute_button = ttk.Button(
            self.execute_frame,
            text="🚀 Execute Query",
            command=self.execute_selected_analysis,
            style="Action.TButton"
        )
        self.execute_button.pack(expand=True, ipadx=50, ipady=15)

    def build_footer(self):
        """Build the application footer"""
        # Status information
        self.status_label = ttk.Label(
            self.footer_frame,
            text="Ready - Select your query parameters and analysis tools",
            style="Footer.TLabel"
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        # Version and credits
        self.credits_label = ttk.Label(
            self.footer_frame,
            text="© 2025 Ingredients Visualizer v1.0 | Advanced Query Interface",
            style="Footer.TLabel"
        )
        self.credits_label.pack(side="right", padx=20, pady=10)
    
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
        
        self.ms_cf_bpc = PopoverMultiSelect(
            self.first_frame,
            header="bpc_name",
            items=get_values_for_dropdown("build_plan_class", "bpc_name"),
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
                self.ms_cf_bpc,
                self.ms_cf_host_id
            ],
            width=35
        )
        self.msplus_cost_function.pack(fill="x", pady=(0, 15))

    # ----------------- Analysis Parameter Section -----------------------------------------------------------------------------
    
    def build_second_frame(self):
        """Build the analysis tools section with enhanced layout"""
        
        # Section description
        description_label = ttk.Label(
            self.second_frame, 
            text="Choose your analysis method:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Analysis tools with descriptions
        tools_frame = ttk.Frame(self.second_frame)
        tools_frame.pack(fill="x")
        
        self.ms_analysis_parameter = PopoverMultiSelect(
            self.second_frame,
            header="Select Analysis Parameter",
            items=["Loss Factor Analysis", "Q-Error Analysis", "P-Error Analysis"],
            width=35
        )

        self.ms_analysis_parameter.pack(fill="x", pady=(0, 10))
    # ------------------------------ Detail Filters Section --------------------------------------------------------

    def build_third_frame(self):
        """Build the detail filters section with enhanced layout"""
        
        # Section description
        description_label = ttk.Label(
            self.third_frame, 
            text="Configure detailed result filters:",
            style="Title.TLabel"
        )
        description_label.pack(anchor="w", pady=(0, 15))

        # Filter type selection
        filter_label = ttk.Label(self.third_frame, text="📊 Filter Metric:", font=("Arial", 10, "bold"))
        filter_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_detail_view = PopoverMultiSelect(
            self.third_frame,
            header="Select Detail View Filter",
            items=["avg_lf", "median_lf", "max_lf", "avg_qerr", "median_qerr", "max_qerr"],
            width=35
        )
        self.ms_detail_view.pack(fill="x", pady=(0, 10))

        # Comparison type
        comparison_label = ttk.Label(self.third_frame, text="🔍 Comparison Type:", font=("Arial", 10, "bold"))
        comparison_label.pack(anchor="w", pady=(5, 2))
        
        self.ms_filter_detail = PopoverMultiSelect(
            self.third_frame,
            header="Select Comparison Type",
            items=["größer als", "kleiner als", "gleich", "zwischen"],
            width=35
        )
        self.ms_filter_detail.pack(fill="x", pady=(0, 10))
        
        # Bind to selection changes to show/hide second entry
        self.ms_filter_detail.button.configure(command=self.on_filter_detail_change)
        
        # Override the popover's close methods to restore Entry responsiveness
        self._setup_popover_callbacks()

        # Input values
        input_label = ttk.Label(self.third_frame, text="🔢 Filter Value(s):", font=("Arial", 10, "bold"))
        input_label.pack(anchor="w", pady=(5, 2))
        
        self.eingabe_detail = tk.StringVar()
        self.eingabe_detail.trace_add("write", self.on_detail_input_change)

        input_frame = ttk.Frame(self.third_frame)
        input_frame.pack(fill="x", pady=(0, 10))
        
        self.eingabe_detail_entry = ttk.Entry(input_frame, textvariable=self.eingabe_detail)
        self.eingabe_detail_entry.pack(fill="x")
        
        # Bind events to ensure Entry remains responsive
        self.eingabe_detail_entry.bind("<Button-1>", self.on_entry_click)
        self.eingabe_detail_entry.bind("<FocusIn>", self.on_entry_focus)
        self.eingabe_detail_entry.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
        # Create second entry for "zwischen" option but don't pack it yet
        self.eingabe_detail_2_var = tk.StringVar()
        self.eingabe_detail_2_var.trace_add("write", self.on_detail_input_change_2)
        
        self.eingabe_detail_2 = ttk.Entry(input_frame, textvariable=self.eingabe_detail_2_var)
        self.eingabe_detail_2.bind("<Button-1>", self.on_entry_click)
        self.eingabe_detail_2.bind("<FocusIn>", self.on_entry_focus)
        self.eingabe_detail_2.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
        
        
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
            # Ensure Entry widgets are properly enabled and can receive focus
            if hasattr(self, 'eingabe_detail_entry') and self.eingabe_detail_entry.winfo_exists():
                self.eingabe_detail_entry.config(state='normal')
                # Force focus update
                self.eingabe_detail_entry.update_idletasks()
                
            if hasattr(self, 'eingabe_detail_2') and self.eingabe_detail_2.winfo_exists():
                self.eingabe_detail_2.config(state='normal')
                self.eingabe_detail_2.update_idletasks()
                
            # Update entries visibility based on current selection
            self.update_detail_entries_visibility()
            
        except tk.TclError:
            # Handle case where widgets have been destroyed
            pass
    
    def get_detail_filter_values(self):
        """
        Get all detail filter values from the GUI.
        
        Returns:
            dict: Dictionary containing:
                - 'metrics': List of selected metric(s) (e.g., ['avg_lf', 'median_qerr'])
                - 'comparison': Selected comparison type (e.g., 'größer als', 'zwischen')
                - 'value1': First numeric value from entry field (as float or None)
                - 'value2': Second numeric value from entry field (as float or None, only for 'zwischen')
        """
        result = {
            'metrics': [],
            'comparison': None,
            'value1': None,
            'value2': None
        }
        
        # Get selected metrics
        if hasattr(self, 'ms_detail_view'):
            result['metrics'] = self.ms_detail_view.get_selected()
        
        # Get comparison type
        if hasattr(self, 'ms_filter_detail'):
            comparison_list = self.ms_filter_detail.get_selected()
            result['comparison'] = comparison_list[0] if comparison_list else None
        
        # Get first value
        if hasattr(self, 'eingabe_detail'):
            value_str = self.eingabe_detail.get().strip()
            if value_str:
                try:
                    result['value1'] = float(value_str)
                except ValueError:
                    result['value1'] = None
        
        # Get second value (only relevant for 'zwischen')
        if hasattr(self, 'eingabe_detail_2_var'):
            value_str = self.eingabe_detail_2_var.get().strip()
            if value_str:
                try:
                    result['value2'] = float(value_str)
                except ValueError:
                    result['value2'] = None
        
        return result
    
# ------------------------ RUN-METHODE --------------------------------------------------------------
    def run(self):
        self.mainloop()