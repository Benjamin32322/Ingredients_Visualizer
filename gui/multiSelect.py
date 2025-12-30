import tkinter as tk
from tkinter import ttk


class PopoverMultiSelect(ttk.Frame):
    """
    Dropdown-ähnliches Multi-Select mit Popover+Listbox.

    Fixes in this version:
    - Robust "click outside" handling (works even with overrideredirect + grab_set)
    - Safe unbinding of the global click handler (unbind by funcid)
    - FocusOut is kept as an extra fallback, but no longer the only close mechanism
    """
    def __init__(self, master, items, header="Select…", all_label="All",
                 no_label="No selection", width=28, height=8, **kwargs):
        super().__init__(master, **kwargs)
        self._all_label = all_label
        self._no_label  = no_label
        self._items = [str(x) for x in items]
        self._selection = set()
        self._height = height
        self._header = header

        self._var = tk.StringVar(value=self._header)
        self.button = ttk.Button(self, textvariable=self._var,
                                 command=self.open_popover, width=width)
        self.button.pack(fill="x")

        self._update_button_text()

        # Popover objects (lazy)
        self._top = None
        self._listbox = None

        # For click-outside binding
        self._root_click_bind_id = None

    # ----------------- Public API -----------------

    def get_selected(self):
        return sorted(self._selection)

    def set_selected(self, values):
        if values == self._no_label or values is None:
            self._selection.clear()
        else:
            try:
                iterable = values
                self._selection = {str(v) for v in iterable if str(v) in self._items}
            except TypeError:
                v = str(values)
                self._selection = {v} if v in self._items else set()
        self._update_button_text()

    def set_items(self, items):
        self._items = [str(x) for x in items]
        self._selection.clear()
        self._update_button_text()

    # ----------------- Intern -----------------

    def _update_button_text(self):
        n = len(self._selection)
        if n == 0:
            self._var.set(self._header)
        elif n <= 2:
            self._var.set(", ".join(sorted(self._selection)))
        else:
            self._var.set(f"{n} selected")

    def _no_selection_and_close(self):
        self._selection.clear()
        self._update_button_text()
        self._close()

    def _bind_click_outside(self):
        """Bind a click handler on the root to detect clicks outside the popover."""
        root = self.winfo_toplevel()
        if self._root_click_bind_id is None:
            # Bind on root (not bind_all) and store funcid so we can unbind just ours.
            self._root_click_bind_id = root.bind("<Button-1>", self._on_root_click, add="+")

    def _unbind_click_outside(self):
        root = self.winfo_toplevel()
        if self._root_click_bind_id is not None:
            try:
                root.unbind("<Button-1>", self._root_click_bind_id)
            except Exception:
                pass
            self._root_click_bind_id = None

    def _on_root_click(self, event):
        """If click is outside the popover window, apply + close."""
        if not (self._top and tk.Toplevel.winfo_exists(self._top)):
            return

        # Coordinates of click
        x, y = event.x_root, event.y_root

        # Popover bounds
        x0 = self._top.winfo_rootx()
        y0 = self._top.winfo_rooty()
        x1 = x0 + self._top.winfo_width()
        y1 = y0 + self._top.winfo_height()

        if not (x0 <= x <= x1 and y0 <= y <= y1):
            self._apply_and_close()

    def open_popover(self):
        if self._top and tk.Toplevel.winfo_exists(self._top):
            return  # already open

        self._top = tk.Toplevel(self)
        self._top.withdraw()
        self._top.overrideredirect(True)
        self._top.transient(self.winfo_toplevel())

        # Position
        bx = self.button.winfo_rootx()
        by = self.button.winfo_rooty() + self.button.winfo_height()
        self._top.geometry(f"+{bx}+{by}")

        frame = ttk.Frame(self._top, padding=6, borderwidth=1, relief="solid")
        frame.grid(row=0, column=0, sticky="nsew")
        self._top.grid_columnconfigure(0, weight=1)
        self._top.grid_rowconfigure(0, weight=1)

        # Search field
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        
        search_label = ttk.Label(search_frame, text="🔍 Search:")
        search_label.pack(side="left", padx=(0, 5))
        
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_changed)
        self._search_entry = ttk.Entry(search_frame, textvariable=self._search_var)
        self._search_entry.pack(side="left", fill="x", expand=True)
        
        # Bind events to ensure Entry remains responsive (similar to detail filter entries)
        self._search_entry.bind("<Button-1>", self._on_search_entry_click)
        self._search_entry.bind("<FocusIn>", self._on_search_entry_focus)
        self._search_entry.bind("<KeyPress>", self._ensure_search_focus)
        
        # Store filtered items list
        self._filtered_items = self._items.copy()

        self._listbox = tk.Listbox(
            frame, selectmode="extended",
            height=self._height, exportselection=False
        )
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self._listbox.yview)
        self._listbox.config(yscrollcommand=scroll.set)

        self._listbox.grid(row=1, column=0, sticky="nsew")
        scroll.grid(row=1, column=1, sticky="ns")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        btns = ttk.Frame(frame)
        btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        ttk.Button(btns, text="OK", command=self._apply_and_close).pack(side="right")
        ttk.Button(btns, text="Cancel", command=self._close).pack(side="right", padx=(0, 6))
        ttk.Button(btns, text=self._no_label,
                   command=self._no_selection_and_close).pack(side="right", padx=(0, 6))

        # Populate listbox with all items initially
        for it in self._filtered_items:
            self._listbox.insert("end", it)

        # mark current selection
        if self._selection:
            for idx, it in enumerate(self._filtered_items):
                if it in self._selection:
                    self._listbox.selection_set(idx)

        self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        self._top.bind("<Escape>", lambda e: self._close())

        # Modified FocusOut handler - don't close if focus is on search entry or listbox
        self._top.bind("<FocusOut>", self._on_focus_out)

        # Grab + click-outside
        try:
            self._top.grab_set()
        except tk.TclError:
            pass

        self._bind_click_outside()

        self._top.deiconify()
        self._top.lift()
        self._top.update_idletasks()
        
        # Set focus to search entry for immediate typing
        self._search_entry.focus_set()

    def _on_focus_out(self, event):
        """Handle FocusOut event - only close if focus truly left the popover window"""
        if not (self._top and tk.Toplevel.winfo_exists(self._top)):
            return
        
        # Get the widget that now has focus
        try:
            focus_widget = self._top.focus_get()
            # Don't close if focus is on search entry, listbox, or any widget within the popover
            if focus_widget in [self._search_entry, self._listbox]:
                return
            # Also check if focus is on any child widget of the popover
            if focus_widget and str(focus_widget).startswith(str(self._top)):
                return
        except Exception:
            pass
        
        # If focus truly left the popover, apply and close
        self._apply_and_close()

    def _on_listbox_select(self, _evt=None):
        return

    def _on_search_entry_click(self, event):
        """Handle click events for search Entry to ensure it remains responsive"""
        try:
            # Force grab release from the toplevel to allow Entry to get focus
            try:
                if self._top:
                    self._top.grab_release()
            except tk.TclError:
                pass
            
            # Set focus and cursor
            event.widget.focus_force()
            event.widget.icursor(tk.INSERT)
            
            # Ensure the widget is in normal state
            event.widget.config(state='normal')
            
            # Reapply grab after a short delay to maintain modal behavior
            if self._top:
                self._top.after(10, lambda: self._reapply_grab())
            
        except (tk.TclError, AttributeError):
            pass
        return "break"
    
    def _on_search_entry_focus(self, event):
        """Handle FocusIn events for search Entry"""
        try:
            # Release grab temporarily
            if self._top:
                try:
                    self._top.grab_release()
                except tk.TclError:
                    pass
            
            # Set focus
            event.widget.focus_force()
            
            # Reapply grab after focus is set
            if self._top:
                self._top.after(10, lambda: self._reapply_grab())
                
        except (tk.TclError, AttributeError):
            pass
    
    def _ensure_search_focus(self, event):
        """Ensure search Entry maintains focus during key events"""
        if event.widget and hasattr(event.widget, 'focus_set'):
            event.widget.focus_set()
        return None  # Allow normal key processing to continue
    
    def _reapply_grab(self):
        """Reapply grab_set to maintain modal behavior"""
        try:
            if self._top and tk.Toplevel.winfo_exists(self._top):
                self._top.grab_set()
        except tk.TclError:
            pass

    def _on_search_changed(self, *args):
        """Filter listbox items based on search input (case-insensitive and space-insensitive)"""
        if not (self._listbox and tk.Listbox.winfo_exists(self._listbox)):
            return
        
        search_text = self._search_var.get()
        
        # Normalize search text: remove spaces and convert to lowercase
        normalized_search = search_text.replace(" ", "").lower()
        
        # Get currently selected items from the listbox before clearing
        current_selection = set()
        sel_idx = self._listbox.curselection()
        if sel_idx:
            current_selection = {self._listbox.get(i) for i in sel_idx}
        
        # Clear listbox
        self._listbox.delete(0, "end")
        
        # Filter items: normalize each item and check if search text is contained
        self._filtered_items = []
        for item in self._items:
            normalized_item = item.replace(" ", "").lower()
            if normalized_search in normalized_item:
                self._filtered_items.append(item)
        
        # Repopulate listbox with filtered items
        for item in self._filtered_items:
            self._listbox.insert("end", item)
        
        # Restore selection for items that are still visible
        for idx, item in enumerate(self._filtered_items):
            if item in current_selection:
                self._listbox.selection_set(idx)

    def _apply_and_close(self):
        if not (self._top and tk.Toplevel.winfo_exists(self._top)):
            return

        sel_idx = self._listbox.curselection()
        if not sel_idx:
            self._selection.clear()
        else:
            self._selection = {self._listbox.get(i) for i in sel_idx}

        self._update_button_text()
        self._close()

    def _close(self):
        # unbind click-outside handler first
        self._unbind_click_outside()

        # release grab
        try:
            if self._top:
                self._top.grab_release()
        except Exception:
            pass

        if self._top and tk.Toplevel.winfo_exists(self._top):
            self._top.destroy()

        self._top = None
        self._listbox = None


class MultiSelectPlus(PopoverMultiSelect):
    """
    Composite MultiSelect where each "item" is itself a logical group.

    Fixes in this version:
    - Same click-outside robustness as PopoverMultiSelect
    """
    def __init__(self, master, items, header="Select…", all_label="All",
                 no_label="No selection", width=28, height=8, **kwargs):

        self._child_specs = []
        self._child_widgets = None
        self._height = height
        self._all_label = all_label
        self._no_label = no_label

        super().__init__(master, [], header=header, all_label=all_label,
                         no_label=no_label, width=width, height=height, **kwargs)

        for it in items:
            if isinstance(it, PopoverMultiSelect):
                label = getattr(it, "_header", "Group")
                elems = [str(x) for x in getattr(it, "_items", [])]
                selection = set(map(str, it.get_selected()))
            else:
                label, elems = it
                elems = [str(x) for x in elems]
                selection = set()
            self._child_specs.append({
                "label": str(label),
                "items": elems,
                "selection": selection
            })

        self._update_button_text()

    # --------------- Public API ----------------

    def set_items(self, items):
        self._child_specs = []
        for it in items:
            if isinstance(it, PopoverMultiSelect):
                label = getattr(it, "_header", "Group")
                elems = [str(x) for x in getattr(it, "_items", [])]
            else:
                label, elems = it
                elems = [str(x) for x in elems]
            self._child_specs.append({
                "label": str(label),
                "items": elems,
                "selection": set()
            })
        self._update_button_text()

    def get_selected(self):
        return {
            spec["label"]: sorted(spec["selection"])
            for spec in self._child_specs
        }

    def set_selected(self, values):
        if values == self._no_label:
            for spec in self._child_specs:
                spec["selection"].clear()
        elif isinstance(values, dict):
            for spec in self._child_specs:
                v = values.get(spec["label"])
                if v is None:
                    continue
                vset = {str(x) for x in v}
                spec["selection"] = {x for x in vset if x in spec["items"]}
        self._update_button_text()

    # --------------- Intern ----------------

    def _update_button_text(self):
        total_selected = sum(len(spec["selection"]) for spec in self._child_specs)
        if total_selected == 0:
            self._var.set(self._header)
        elif total_selected <= 2:
            flat = []
            for spec in self._child_specs:
                for it in sorted(spec["selection"]):
                    flat.append(f"{spec['label']}: {it}")
                    if len(flat) >= 2:
                        break
                if len(flat) >= 2:
                    break
            self._var.set(", ".join(flat) if flat else self._header)
        else:
            self._var.set(f"{total_selected} selected")

    def _clear_all_and_close(self):
        for spec in self._child_specs:
            spec["selection"].clear()

        if self._child_widgets:
            for child in self._child_widgets:
                child.set_selected([])

        self._update_button_text()
        self._close()

    def open_popover(self):
        if self._top and tk.Toplevel.winfo_exists(self._top):
            return

        self._top = tk.Toplevel(self)
        self._top.withdraw()
        self._top.overrideredirect(True)
        self._top.transient(self.winfo_toplevel())

        bx = self.button.winfo_rootx()
        by = self.button.winfo_rooty() + self.button.winfo_height()
        self._top.geometry(f"+{bx}+{by}")

        frame = ttk.Frame(self._top, padding=6, borderwidth=1, relief="solid")
        frame.grid(row=0, column=0, sticky="nsew")
        self._top.grid_columnconfigure(0, weight=1)
        self._top.grid_rowconfigure(0, weight=1)

        inner = ttk.Frame(frame)
        inner.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self._child_widgets = []
        for spec in self._child_specs:
            child = PopoverMultiSelect(
                inner,
                spec["items"],
                header=spec["label"],
                all_label=self._all_label,
                no_label=self._no_label,
                width=self.button.cget("width"),
                height=self._height
            )
            child.pack(fill="x", pady=2)
            child.set_selected(sorted(spec["selection"]))
            self._child_widgets.append(child)

        btns = ttk.Frame(frame)
        btns.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        ttk.Button(btns, text="OK", command=self._apply_and_close).pack(side="right")
        ttk.Button(btns, text="Cancel", command=self._close).pack(side="right", padx=(0, 6))
        ttk.Button(btns, text=self._no_label,
                   command=self._clear_all_and_close).pack(side="right", padx=(0, 6))

        self._top.bind("<Escape>", lambda e: self._close())
        self._top.bind("<FocusOut>", lambda e: self._apply_and_close())

        try:
            self._top.grab_set()
        except tk.TclError:
            pass

        # Use same click-outside binding from base class
        self._bind_click_outside()

        self._top.deiconify()
        self._top.lift()
        self._top.update_idletasks()

    def _apply_and_close(self):
        if not (self._top and tk.Toplevel.winfo_exists(self._top)):
            return
        for spec, child in zip(self._child_specs, self._child_widgets or []):
            spec["selection"] = set(child.get_selected())
        self._update_button_text()
        self._close()

    def _close(self):
        # unbind click-outside handler
        self._unbind_click_outside()

        try:
            if self._top:
                self._top.grab_release()
        except Exception:
            pass

        if self._top and tk.Toplevel.winfo_exists(self._top):
            self._top.destroy()

        self._top = None
        self._child_widgets = None
