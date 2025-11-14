# plotting.py
import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkinter import filedialog, messagebox

def plot_treeview(columns, data):
    plot_window = tk.Toplevel()
    plot_window.title("Plot Window")
    plot_window.geometry("800x600")

    toolbar = ttk.Frame(plot_window)
    toolbar.pack(side="top", fill="x")

    def export_to_excel():
        try:
            df = pd.DataFrame(data, columns=columns)

            # Dialog für Speicherort
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel-Datei", "*.xlsx"), ("Alle Dateien", "*.*")]
            )
            if not filepath:
                return  # Abbrechen

            df.to_excel(filepath, index=False)
            messagebox.showinfo("Export erfolgreich", f"Datei gespeichert:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Fehler beim Export", str(e))

    btn_export = ttk.Button(toolbar, text="Als Excel exportieren", command=export_to_excel)
    btn_export.pack(pady=8)


    table_frame = ttk.Frame(plot_window)
    table_frame.pack(side="top", fill="both", expand=True)

    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    for row in data:
        tree.insert("", "end", values=row)

    scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")


    plot_window.mainloop()