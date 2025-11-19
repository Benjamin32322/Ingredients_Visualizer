import tkinter as tk
from tkinter import ttk


class PopoverMultiSelect(ttk.Frame):
    """
    Dropdown-ähnliches Multi-Select mit Popover+Listbox.

    Features:
    - Button "No selection" -> löscht Auswahl SOFORT (kein OK nötig), Header = Start-Header
    - Listbox zeigt nur die eigentlichen Items
    - get_selected() -> Liste gewählter Items (Strings).
    - set_selected(values | "No selection")
    """
    def __init__(self, master, items, header="Select…", all_label="All",
                 no_label="No selection", width=28, height=8, **kwargs):
        """
        all_label bleibt nur im Interface für Kompatibilität,
        wird aber nicht als eigenes Listbox-Item verwendet.
        """
        super().__init__(master, **kwargs)
        self._all_label = all_label         # wird NICHT mehr im UI genutzt
        self._no_label  = no_label
        self._items = [str(x) for x in items]
        self._selection = set()             # aktuelle Auswahl
        self._height = height
        self._header = header               # Start-Header merken

        # Button zeigt aktuellen Status (ähnlich Combobox)
        self._var = tk.StringVar(value=self._header)
        self.button = ttk.Button(self, textvariable=self._var,
                                 command=self.open_popover, width=width)
        self.button.pack(fill="x")

        self._update_button_text()

        # Popover-Objekte (lazy)
        self._top = None
        self._listbox = None

    # ----------------- Public API -----------------

    def get_selected(self):
        """Gibt die aktuelle Auswahl als sortierte Liste von Strings zurück."""
        return sorted(self._selection)

    def set_selected(self, values):
        """values: Iterable von Werten oder 'No selection'."""
        if values == self._no_label or values is None:
            self._selection.clear()
        else:
            try:
                iterable = values
                # strings, die in _items vorkommen
                self._selection = {str(v) for v in iterable if str(v) in self._items}
            except TypeError:
                # falls nur ein einzelner Wert übergeben wurde
                v = str(values)
                self._selection = {v} if v in self._items else set()
        self._update_button_text()

    def set_items(self, items):
        """Setzt Items neu und leert die Auswahl."""
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
        """Handler für den 'No selection'-Button."""
        self._selection.clear()
        self._update_button_text()
        self._close()

    def open_popover(self):
        if self._top and tk.Toplevel.winfo_exists(self._top):
            return  # schon offen

        # Popover erstellen
        self._top = tk.Toplevel(self)
        self._top.withdraw()
        self._top.overrideredirect(True)
        self._top.transient(self.winfo_toplevel())

        # Position neben dem Button
        bx = self.button.winfo_rootx()
        by = self.button.winfo_rooty() + self.button.winfo_height()
        self._top.geometry(f"+{bx}+{by}")

        # Container
        frame = ttk.Frame(self._top, padding=6, borderwidth=1, relief="solid")
        frame.grid(row=0, column=0, sticky="nsew")
        self._top.grid_columnconfigure(0, weight=1)
        self._top.grid_rowconfigure(0, weight=1)

        # Listbox + Scrollbar
        self._listbox = tk.Listbox(
            frame, selectmode="extended",
            height=self._height, exportselection=False
        )
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self._listbox.yview)
        self._listbox.config(yscrollcommand=scroll.set)

        self._listbox.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # Buttons (OK, Cancel, No selection)
        btns = ttk.Frame(frame)
        btns.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        ttk.Button(btns, text="OK", command=self._apply_and_close).pack(side="right")
        ttk.Button(btns, text="Cancel", command=self._close).pack(side="right", padx=(0, 6))
        ttk.Button(btns, text=self._no_label,
                   command=self._no_selection_and_close).pack(side="right", padx=(0, 6))

        # Inhalte einfüllen: nur Items
        for it in self._items:
            self._listbox.insert("end", it)

        # aktuelle Auswahl markieren
        if self._selection:
            for idx, it in enumerate(self._items, start=0):
                if it in self._selection:
                    self._listbox.selection_set(idx)

        # Event-Binds
        self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        self._top.bind("<Escape>", lambda e: self._close())
        self._top.bind("<FocusOut>", lambda e: self._apply_and_close())
        try:
            self._top.grab_set()
        except tk.TclError:
            pass

        self._top.deiconify()
        self._top.lift()
        self._top.update_idletasks()

    def _on_listbox_select(self, _evt=None):
        # Aktuell kein Spezialverhalten nötig,
        # aber Hook bleibt für spätere Logik
        return

    def _apply_and_close(self):
        if not (self._top and tk.Toplevel.winfo_exists(self._top)):
            return

        sel_idx = self._listbox.curselection()
        if not sel_idx:
            self._selection.clear()
        else:
            # Alle selektierten Items übernehmen
            self._selection = {
                self._listbox.get(i) for i in sel_idx
            }

        self._update_button_text()
        self._close()

    def _close(self):
        try:
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

    Accepted `items` formats:
    - existing PopoverMultiSelect instances
    - (label, iterable_of_values) tuples

    Public API:
    - get_selected() -> dict: {child_label: [selected_items,...], ...}
    - set_selected(values) -> accepts:
        * 'No selection' (löscht alles)
        * dict mapping child_label -> iterable_of_values
    """
    def __init__(self, master, items, header="Select…", all_label="All",
                 no_label="No selection", width=28, height=8, **kwargs):

        # interne Strukturen vor super()
        self._child_specs = []          # Liste von Dicts: {"label", "items", "selection"}
        self._child_widgets = None
        self._height = height
        self._all_label = all_label     # wird nur noch als Text-Konstante weitergereicht
        self._no_label = no_label

        # Basis-UI (Button etc.) mit leerer Itemliste bauen
        super().__init__(master, [], header=header, all_label=all_label,
                         no_label=no_label, width=width, height=height, **kwargs)

        # Eingaben normalisieren -> _child_specs füllen
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
        """Replace children and clear selections."""
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
        """Return dict {child_label: [selected_items,...]}"""
        return {
            spec["label"]: sorted(spec["selection"])
            for spec in self._child_specs
        }

    def set_selected(self, values):
        """
        values:
          - no_label: alles leeren
          - dict(label -> iterable_of_values): je Gruppe setzen
        """
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
        # alles andere wird ignoriert
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
        """Handler für 'No selection' im MultiSelectPlus-Popover."""
        # alle internen Selektionen löschen
        for spec in self._child_specs:
            spec["selection"].clear()

        # falls Kinder-Widgets existieren, diese ebenfalls leeren
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
                all_label=self._all_label,   # wird intern nicht als Item genutzt
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
        try:
            if self._top:
                self._top.grab_release()
        except Exception:
            pass
        if self._top and tk.Toplevel.winfo_exists(self._top):
            self._top.destroy()
        self._top = None
        self._child_widgets = None
