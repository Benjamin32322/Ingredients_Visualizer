"""
GUI Responsiveness Module
Handles Entry widget focus management and responsiveness issues
"""

import tkinter as tk


class ResponsivenessMixin:
    """Mixin class providing Entry widget responsiveness management"""
    
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
            # Widget might have been destroyed
            pass
        
        # Schedule next check
        self.after(1000, self.periodic_focus_check)
    
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
                self.eingabe_detail_2.pack(fill="x", pady=(5, 0))
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
