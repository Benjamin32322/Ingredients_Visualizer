import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from db.dbHandler import get_values_for_dropdown, build_filter, build_cost_filters, execute_query
from gui.multiSelect import PopoverMultiSelect, MultiSelectPlus
from plotting.plotting import plot_treeview



class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ingredients Visualizer")
        # Make the window fullscreen
        self.attributes("-fullscreen", True)
        # Allow exiting fullscreen with Esc
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        # define the window size to use when not fullscreen and center it
        width, height = 1200, 700
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self._default_geometry = f"{width}x{height}+{x}+{y}"
        # ensure geometry is set (will take effect when exiting fullscreen)
        self.geometry(self._default_geometry)

        # bind Escape to exit fullscreen and restore the desired size
        def _exit_fullscreen(event=None):
            self.attributes("-fullscreen", False)
            self.geometry(self._default_geometry)

        self.bind("<Escape>", _exit_fullscreen)

       
        self.top_level_frame = ttk.Frame(self)
        self.top_level_frame.pack(fill="both", expand=True)

         # Erstellen der Frames
        self.first_frame = ttk.Frame(self.top_level_frame)
        self.second_frame = ttk.Frame(self.top_level_frame)
        self.third_frame = ttk.Frame(self.top_level_frame)


        # Alle Frames initialisieren
        # First-Frame
        self.build_first_frame()
        self.layout_first_frame()
        # Second-Frame
        self.build_second_frame()
        self.layout_second_frame()
        # Third-Frame
        self.build_third_frame()
        self.layout_third_frame()

        # Beim Start wird der erste Frame angezeigt
        self.show_all_frames()
        
        # Initialize proper focus management
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

    # -------------------------- TOP-LEVEL FRAME -------------------------------------------------------------

    def build_top_level_frame(self):
        pass # Implementation

    def layout_top_level_frame(self):
        pass  # Implementation
    
    
    # ----------------- First-Frame -----------------------------------------------------------------
    
    def build_first_frame(self):
        
        self.welcome_label = ttk.Label(self.first_frame, text="Welcome to the Ingredients Visualizer!")

        self.execute_button = ttk.Button(self.first_frame, text="Execute", command=self.on_execute)

        self.ms_plan_generator = PopoverMultiSelect(
            self.first_frame,
            header="Plan Generator",
            items=get_values_for_dropdown("plan_generator", "pg_name")
        )
        self.ms_cardinality_provider = PopoverMultiSelect(
            self.first_frame,
            header="Cardinality Provider",
            items=get_values_for_dropdown("card_provider", "cp_name")
        )

        self.ms_cf_mat = PopoverMultiSelect(
            self.first_frame,
            header="bpi_cf_mat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_mat")
        )
        self.ms_cf_concat = PopoverMultiSelect(
            self.first_frame,
            header="bpi_cf_concat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_concat")
        )
        self.ms_cf_join_bundle = PopoverMultiSelect(
            self.first_frame,
            header="bpi_cf_join_bundle",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_join_bundle")
        )
        self.ms_cf_bpc = PopoverMultiSelect(
            self.first_frame,
            header="bpc_name",
            items=get_values_for_dropdown("build_plan_class", "bpc_name")
        )
        self.ms_cf_host_id = PopoverMultiSelect(
            self.first_frame,
            header="wp_cf_host_id",
            items=get_values_for_dropdown("work_package", "wp_cf_host_id")
        )

        self.msplus_cost_function = MultiSelectPlus(
            self.first_frame,
            header="Cost Function",
            items=[
                self.ms_cf_mat,
                self.ms_cf_concat,
                self.ms_cf_join_bundle,
                self.ms_cf_bpc,
                self.ms_cf_host_id
            ]
        )
    
    def layout_first_frame(self):

        self.welcome_label.pack(pady=30)
        self.ms_plan_generator.pack(pady=10)
        self.ms_cardinality_provider.pack(pady=10)
        self.msplus_cost_function.pack(pady=10)
        self.execute_button.pack(pady=10)
    
    # Dummy-Funktion für Noch nicht implementierte Buttons & Frames
    def show_message(self):
        messagebox.showinfo("Information", "This is a sample GUI application.")

    # ----------------- Second-Frame -----------------------------------------------------------------------------
    
    def build_second_frame(self):
        self.loss_factor_button = ttk.Button(
            self.second_frame,
            text = "Loss Factor",
            command=self.on_execute
        )

        self.q_error_button = ttk.Button(
            self.second_frame,
            text= "q-Error",
            command=self.execute_q_error
        )

        self.p_error_button = ttk.Button(
            self.second_frame,
            text= "p-Error",
            command=self.execute_p_error
        )
        
    def layout_second_frame(self):
        self.loss_factor_button.pack(pady=10)
        self.q_error_button.pack(pady=10)
        self.p_error_button.pack(pady=10)


    
    # ------------------------------ THIRD FRAME --------------------------------------------------------

    def on_detail_input_change(self, *args):
        current_text = self.eingabe_detail.get()
        print("Detail Input Changed:", current_text)
    
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
        
        self.ms_detail_view = PopoverMultiSelect(
            self.third_frame,
            header="Detail View Filter",
            items=["avg_lf", "median_lf", "max_lf", "avg_qerr", "median_qerr", "max_qerr"] 
        )

        self.ms_filter_detail = PopoverMultiSelect(
            self.third_frame,
            header="Detail View Größe",
            items=["größer als", "kleiner als", "gleich", "zwischen"]
        )
        
        # Bind to selection changes to show/hide second entry
        self.ms_filter_detail.button.configure(command=self.on_filter_detail_change)
        
        # Override the popover's close methods to restore Entry responsiveness
        self._setup_popover_callbacks()

        self.eingabe_detail = tk.StringVar()
        self.eingabe_detail.trace_add("write", self.on_detail_input_change)

        self.eingabe_detail_entry = ttk.Entry(self.third_frame, textvariable=self.eingabe_detail)
        
        # Bind events to ensure Entry remains responsive
        self.eingabe_detail_entry.bind("<Button-1>", self.on_entry_click)
        self.eingabe_detail_entry.bind("<FocusIn>", self.on_entry_focus)
        self.eingabe_detail_entry.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
        # Create second entry for "zwischen" option but don't pack it yet
        self.eingabe_detail_2 = ttk.Entry(self.third_frame)
        self.eingabe_detail_2.bind("<Button-1>", self.on_entry_click)
        self.eingabe_detail_2.bind("<FocusIn>", self.on_entry_focus)
        self.eingabe_detail_2.bind("<KeyPress>", lambda e: self.ensure_entry_focus(e))
        
        
    def layout_third_frame(self):
        self.ms_detail_view.pack(pady=10)
        self.ms_filter_detail.pack(pady=10)
        self.eingabe_detail_entry.pack(pady=10)

        
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
        
        # Restore focus to Entry widgets after execution
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
        
        # Restore focus to Entry widgets after execution
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
        
        # Restore focus to Entry widgets after execution
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
    
# --------------------------- WECHSEL ZWISCHEN DEN FRAMES ----------------------------------------------------------
    
    def show_all_frames(self):
        self.first_frame.pack(fill="x", padx=5, pady=5)
        self.second_frame.pack(fill="x", padx=5, pady=5)
        self.third_frame.pack(fill="x", padx=5, pady=5)

# ------------------------ RUN-METHODE --------------------------------------------------------------
    def run(self):
        self.mainloop()