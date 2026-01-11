# treeview.py
import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkinter import filedialog, messagebox
from db.dbHandler import build_filter, execute_query

# ----------------------------- PLOTTING TREEVIEW & DETAIL-TREEVIEW -------------------------------------

def plot_treeview(columns, data, params_summary=""):
    plot_window = tk.Toplevel()
    plot_window.title("Plot Window")
    plot_window.geometry("800x600")

    toolbar = ttk.Frame(plot_window)
    toolbar.pack(side="top", fill="x")

    def export_to_csv():
        try:
            df = pd.DataFrame(data, columns=columns)

            # Dialog für Speicherort
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV-Datei", "*.csv"), ("Alle Dateien", "*.*")]
            )
            if not filepath:
                return  # Abbrechen

            # Export to CSV
            if params_summary:
                # Add parameter info as comment lines at the top
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Query Parameters: {params_summary}\n")
                    f.write("#\n")
                    # Write the DataFrame
                    df.to_csv(f, index=False)
            else:
                # No parameters, just write data
                df.to_csv(filepath, index=False, encoding='utf-8')
            
            messagebox.showinfo("Export erfolgreich", f"Datei gespeichert:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Fehler beim Export", str(e))

    btn_export = ttk.Button(toolbar, text="Export as CSV", command=export_to_csv)
    btn_export.pack(pady=8)

    # Display parameter summary if provided
    if params_summary:
        params_frame = ttk.Frame(plot_window, relief="solid", borderwidth=1)
        params_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        params_label = ttk.Label(
            params_frame, 
            text=params_summary,
            wraplength=780,
            justify="left",
            padding=10,
            font=("Arial", 9)
        )
        params_label.pack(fill="x")

    table_frame = ttk.Frame(plot_window)
    table_frame.pack(side="top", fill="both", expand=True)
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

   
    def handle_row_double_click():
        item_id = tree.focus()
        if not item_id:
            return

         # Werte der Zeile
        values = tree.item(item_id, "values")

        # Spaltennamen
        columns = tree["columns"]

        row_dict = dict(zip(columns, values))

    
        return row_dict
    
    def open_detail_view(event):
        
        dict_row = handle_row_double_click()

        filters = {}

        for key, value in dict_row.items():
            filter_key = key.upper() + "_FILTER"
            filter_value = build_filter(key, value)
            filters.update({filter_key: filter_value})
            print(f"{filter_key}: {filter_value}")
        
        
        columns2, result2 = execute_query(1, filters=filters)
        
        # Pass the same params_summary to the detail view
        plot_treeview(columns2, result2, params_summary)


    tree.bind("<Double-1>", open_detail_view)
