import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from db.dbHandler import get_values_for_dropdown, build_filter, build_cost_filters, execute_query
from gui.multiSelect import PopoverMultiSelect, MultiSelectPlus
from plotting.plotting import plot_treeview



class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ingredients Visualizer - Advanced Database Query Interface")
        
        # Configure window
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        
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

    def setup_focus_management(self):
        """Set up focus management to prevent Entry widgets from becoming unresponsive"""
        # Bind a global handler to restore Entry focus when clicking on the main window
        self.bind_all("<Button-1>", self.on_global_click)
        
        # Schedule periodic focus restoration
        self.after(1000, self.periodic_focus_check)
    
    def on_global_click(self, event):
        """Handle global clicks to maintain Entry widget responsiveness"""
        # Don't interfere with normal widget operations
        return None
    
    def periodic_focus_check(self):
        """Periodically ensure Entry widgets remain responsive"""
        try:
            # Check if Entry widgets exist and are responsive
            if hasattr(self, 'eingabe_detail_entry') and self.eingabe_detail_entry.winfo_exists():
                # Ensure the Entry widget can still receive events
                self.eingabe_detail_entry.config(state='normal')
                
            if hasattr(self, 'eingabe_detail_2') and self.eingabe_detail_2.winfo_exists():
                self.eingabe_detail_2.config(state='normal')
                
        except tk.TclError:
            pass
        
        # Schedule the next check
        self.after(2000, self.periodic_focus_check)

    def setup_styles(self):
        """Configure modern styling for the application"""
        self.style = ttk.Style()
        
        # Configure modern frame styles with borders
        self.style.configure("Card.TFrame", 
                           relief="solid", 
                           borderwidth=1, 
                           background="#f8f9fa")
        
        self.style.configure("Header.TFrame", 
                           relief="solid", 
                           borderwidth=2, 
                           background="#2c3e50")
        
        self.style.configure("Footer.TFrame", 
                           relief="solid", 
                           borderwidth=1, 
                           background="#34495e")
        
        # Configure label styles
        self.style.configure("Header.TLabel", 
                           background="#2c3e50", 
                           foreground="white", 
                           font=("Arial", 16, "bold"))
        
        self.style.configure("Title.TLabel", 
                           font=("Arial", 12, "bold"), 
                           foreground="#2c3e50")
        
        self.style.configure("Footer.TLabel", 
                           background="#34495e", 
                           foreground="white", 
                           font=("Arial", 9))
        
        # Configure button styles
        self.style.configure("Action.TButton", 
                           font=("Arial", 10, "bold"))

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
        
        # Exit fullscreen button
        self.exit_fullscreen_btn = ttk.Button(
            self.header_frame,
            text="Exit Fullscreen (ESC)",
            command=lambda: self.attributes("-fullscreen", False)
        )
        self.exit_fullscreen_btn.pack(side="right", padx=20, pady=10)

    def build_main_content(self):
        """Build the main content area with three organized sections"""
        # Create the three main sections with cards
        self.create_query_configuration_section()
        self.create_analysis_tools_section()
        self.create_detail_filters_section()
        self.create_results_section()

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
            text="🔍 Analysis Tools",
            style="Card.TFrame",
            padding=20
        )
        self.second_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        self.build_second_frame()

    def create_detail_filters_section(self):
        """Create the detail filters section (bottom-left)"""
        self.third_frame = ttk.LabelFrame(
            self.content_frame,
            text="🔧 Detail Filters",
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

        # Execute button
        self.execute_button = ttk.Button(
            self.first_frame, 
            text="🚀 Execute Query", 
            command=self.on_execute,
            style="Action.TButton"
        )
        self.execute_button.pack(fill="x", pady=10)

    # ----------------- Analysis Tools Section -----------------------------------------------------------------------------
    
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
        
        # Loss Factor Analysis
        lf_frame = ttk.Frame(tools_frame)
        lf_frame.pack(fill="x", pady=5)
        
        self.loss_factor_button = ttk.Button(
            lf_frame,
            text="📉 Loss Factor Analysis",
            command=self.on_execute,
            style="Action.TButton"
        )
        self.loss_factor_button.pack(fill="x")
        
        lf_desc = ttk.Label(
            lf_frame,
            text="Analyze loss factors in query execution plans",
            font=("Arial", 9),
            foreground="gray"
        )
        lf_desc.pack(anchor="w", pady=(2, 0))

        # Q-Error Analysis
        qe_frame = ttk.Frame(tools_frame)
        qe_frame.pack(fill="x", pady=15)
        
        self.q_error_button = ttk.Button(
            qe_frame,
            text="📊 Q-Error Analysis",
            command=self.execute_q_error,
            style="Action.TButton"
        )
        self.q_error_button.pack(fill="x")
        
        qe_desc = ttk.Label(
            qe_frame,
            text="Examine cardinality estimation errors (Q-Error)",
            font=("Arial", 9),
            foreground="gray"
        )
        qe_desc.pack(anchor="w", pady=(2, 0))

        # P-Error Analysis
        pe_frame = ttk.Frame(tools_frame)
        pe_frame.pack(fill="x", pady=5)
        
        self.p_error_button = ttk.Button(
            pe_frame,
            text="📈 P-Error Analysis",
            command=self.execute_p_error,
            style="Action.TButton"
        )
        self.p_error_button.pack(fill="x")
        
        pe_desc = ttk.Label(
            pe_frame,
            text="Analyze prediction errors in cost estimation",
            font=("Arial", 9),
            foreground="gray"
        )
        pe_desc.pack(anchor="w", pady=(2, 0))

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
        self.eingabe_detail_2 = ttk.Entry(input_frame)
        self.eingabe_detail_2.bind("<Button-1>", self.on_entry_click)
        self.eingabe_detail_2.bind("<FocusIn>", self.on_entry_focus)
        self.eingabe_detail_2.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
        # Add a button to manually restore Entry responsiveness for testing
        self.restore_button = ttk.Button(
            self.third_frame,
            text="🔧 Fix Entry Responsiveness",
            command=self.force_entry_responsiveness
        )
        self.restore_button.pack(fill="x", pady=5)

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
        current_text = self.eingabe_detail.get()
        print("Detail Input Changed:", current_text)
        self.update_status(f"Filter value updated: {current_text}")

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
    
    def on_entry_focus(self, event):
        """Handle focus events for Entry widgets to ensure they remain responsive"""
        try:
            # Force grab release
            try:
                self.grab_release()
            except tk.TclError:
                pass
                
            event.widget.focus_force()
            event.widget.config(state='normal')
        except (tk.TclError, AttributeError):
            pass
        return "break"
    
    def on_entry_click(self, event):
        """Handle click events for Entry widgets to ensure they remain responsive"""
        try:
            # Force grab release first
            try:
                self.grab_release()
            except tk.TclError:
                pass
            
            # Set focus and cursor
            event.widget.focus_force()
            event.widget.icursor(tk.INSERT)
            
            # Ensure the widget is in normal state
            event.widget.config(state='normal')
            
        except (tk.TclError, AttributeError):
            pass
        return "break"
    
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
        self.eingabe_detail_2 = ttk.Entry(input_frame)
        self.eingabe_detail_2.bind("<Button-1>", self.on_entry_click)
        self.eingabe_detail_2.bind("<FocusIn>", self.on_entry_focus)
        self.eingabe_detail_2.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
        # Add a button to manually restore Entry responsiveness for testing
        self.restore_button = ttk.Button(
            self.third_frame,
            text="🔧 Fix Entry Responsiveness",
            command=self.force_entry_responsiveness
        )
        self.restore_button.pack(fill="x", pady=5)
        
        
    # Layout is now handled within build_third_frame method

        
    def ensure_entry_focus(self, event):
        """Ensure Entry widget maintains focus during key events"""
        if event.widget and hasattr(event.widget, 'focus_set'):
            event.widget.focus_set()
        return None  # Allow normal key processing to continue
        
    def update_detail_entries_visibility(self):
        """Update visibility of second entry based on filter selection"""
        selected_filter = self.ms_filter_detail.get_selected()
        if "zwischen" in selected_filter:
            if not self.eingabe_detail_2.winfo_ismapped():
                self.eingabe_detail_2.pack(pady=10)
        else:
            if self.eingabe_detail_2.winfo_ismapped():
                self.eingabe_detail_2.pack_forget()
                
    def on_filter_detail_change(self):
        """Handle changes in the filter detail selection"""
        # Store the original Entry focus state
        self.store_entry_state()
        
        # Release any existing grabs before opening popover
        try:
            self.grab_release()
        except tk.TclError:
            pass
            
        # First call the original open_popover method
        self.ms_filter_detail.open_popover()
        
        # Schedule multiple restoration attempts
        self.after(200, self.update_detail_entries_visibility)
        self.after(300, self.restore_entry_responsiveness)
        self.after(500, self.force_entry_responsiveness)  # Additional safety net
    
    def store_entry_state(self):
        """Store the current state of Entry widgets before popover operations"""
        try:
            self._entry_states = {}
            if hasattr(self, 'eingabe_detail_entry') and self.eingabe_detail_entry.winfo_exists():
                self._entry_states['entry1'] = {
                    'value': self.eingabe_detail.get(),
                    'cursor_pos': self.eingabe_detail_entry.index(tk.INSERT) if hasattr(self.eingabe_detail_entry, 'index') else 0
                }
            if hasattr(self, 'eingabe_detail_2') and self.eingabe_detail_2.winfo_exists():
                self._entry_states['entry2'] = {
                    'value': self.eingabe_detail_2.get(),
                    'cursor_pos': self.eingabe_detail_2.index(tk.INSERT) if hasattr(self.eingabe_detail_2, 'index') else 0
                }
        except (tk.TclError, AttributeError):
            self._entry_states = {}
    
    def restore_entry_responsiveness(self):
        """Restore Entry widget responsiveness after popover operations"""
        try:
            # Force release any remaining grabs
            try:
                self.grab_release()
            except tk.TclError:
                pass
                
            # Restore Entry widget states and bindings
            if hasattr(self, 'eingabe_detail_entry') and self.eingabe_detail_entry.winfo_exists():
                # Ensure the widget is properly configured
                self.eingabe_detail_entry.config(state='normal')
                
                # Rebind all necessary events
                self.eingabe_detail_entry.bind("<Button-1>", self.on_entry_click)
                self.eingabe_detail_entry.bind("<FocusIn>", self.on_entry_focus)
                self.eingabe_detail_entry.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
                
                # Restore cursor position if available
                if hasattr(self, '_entry_states') and 'entry1' in self._entry_states:
                    try:
                        self.eingabe_detail_entry.icursor(self._entry_states['entry1']['cursor_pos'])
                    except (tk.TclError, KeyError):
                        pass
                
                # Force widget update
                self.eingabe_detail_entry.update_idletasks()
                
            if hasattr(self, 'eingabe_detail_2') and self.eingabe_detail_2.winfo_exists():
                self.eingabe_detail_2.config(state='normal')
                
                # Rebind all necessary events
                self.eingabe_detail_2.bind("<Button-1>", self.on_entry_click)
                self.eingabe_detail_2.bind("<FocusIn>", self.on_entry_focus)
                self.eingabe_detail_2.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
                
                # Restore cursor position if available
                if hasattr(self, '_entry_states') and 'entry2' in self._entry_states:
                    try:
                        self.eingabe_detail_2.icursor(self._entry_states['entry2']['cursor_pos'])
                    except (tk.TclError, KeyError):
                        pass
                        
                self.eingabe_detail_2.update_idletasks()
            
            # Clear stored state
            if hasattr(self, '_entry_states'):
                delattr(self, '_entry_states')
                
        except (tk.TclError, AttributeError):
            pass
    
    def _setup_popover_callbacks(self):
        """Setup callbacks to restore Entry responsiveness when popover closes"""
        # Store original close methods
        original_close = self.ms_filter_detail._close
        original_apply_and_close = self.ms_filter_detail._apply_and_close
        
        def enhanced_close():
            original_close()
            # Schedule Entry restoration after popover closes
            self.after(50, self.restore_entry_responsiveness)
        
        def enhanced_apply_and_close():
            original_apply_and_close()
            # Schedule Entry restoration and visibility update
            self.after(50, self.restore_entry_responsiveness)
            self.after(100, self.update_detail_entries_visibility)
        
        # Replace the methods
        self.ms_filter_detail._close = enhanced_close
        self.ms_filter_detail._apply_and_close = enhanced_apply_and_close
    
    def force_entry_responsiveness(self):
        """Manually force Entry widgets to become responsive again"""
        try:
            # Release any grabs on the main window
            try:
                self.grab_release()
            except tk.TclError:
                pass
            
            # Check for any existing toplevels with grabs and release them
            for child in self.winfo_children():
                if isinstance(child, tk.Toplevel):
                    try:
                        child.grab_release()
                    except tk.TclError:
                        pass
            
            # Force Entry widgets to be responsive
            if hasattr(self, 'eingabe_detail_entry') and self.eingabe_detail_entry.winfo_exists():
                self.eingabe_detail_entry.config(state='normal')
                self.eingabe_detail_entry.focus_force()
                # Rebind events
                self.eingabe_detail_entry.bind("<Button-1>", self.on_entry_click)
                self.eingabe_detail_entry.bind("<FocusIn>", self.on_entry_focus)
                self.eingabe_detail_entry.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
                
            if hasattr(self, 'eingabe_detail_2') and self.eingabe_detail_2.winfo_exists():
                self.eingabe_detail_2.config(state='normal')
                # Rebind events
                self.eingabe_detail_2.bind("<Button-1>", self.on_entry_click)
                self.eingabe_detail_2.bind("<FocusIn>", self.on_entry_focus)
                self.eingabe_detail_2.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
            
            print("Entry responsiveness restored!")
            
        except Exception as e:
            print(f"Error restoring Entry responsiveness: {e}")

    # ------------------------------ EXECUTE -------------------------------------------------------------
    def get_filter():
        pass # Implementation

    def on_execute(self):
        
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
    
# ------------------------ RUN-METHODE --------------------------------------------------------------
    def run(self):
        self.mainloop()