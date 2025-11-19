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
        self.geometry("600x400")

        self.start_frame = ttk.Frame(self)
        self.planquality_frame = ttk.Frame(self)

        self.build_start_frame()
        self.start_frame.pack(fill="both", expand=True)

        self.build_planquality_widgets()  # nur Widgets erstellen, noch nicht packen

    # ----------------- Start-Screen -----------------
    def build_start_frame(self):
        label = ttk.Label(self.start_frame, text="Welcome to the Ingredients Visualizer!")
        label.pack(pady=30)

        btn_plan_quality = ttk.Button(
            self.start_frame,
            text="Plan Güte",
            command=self.show_planquality_frame
        )
        btn_plan_quality.pack(pady=10)

        btn_cost_function = ttk.Button(
            self.start_frame,
            text="Cost Function",
            command=lambda: messagebox.showinfo("Info", "Cost Function View kommt später 🙂")
        )
        btn_cost_function.pack(pady=10)

        btn_card_estimator = ttk.Button(
            self.start_frame,
            text="Cardinality Estimator",
            command=lambda: messagebox.showinfo("Info", "Cardinality Estimator View kommt später 🙂")
        )
        btn_card_estimator.pack(pady=10)
    def show_start_frame(self):
        """Zeigt wieder den Start-Screen an."""
        self.planquality_frame.pack_forget()
        self.start_frame.pack(fill="both", expand=True)
    
    def show_planquality_frame(self):
        # Start-Screen ausblenden
        self.start_frame.pack_forget()
        # Plan-Güte-Frame anzeigen
        self.layout_planquality_widgets()
        self.planquality_frame.pack(fill="both", expand=True)

    # Dummy-Funktion für Button
    def show_message(self):
        messagebox.showinfo("Information", "This is a sample GUI application.")

    # ----------------- Plan-Güte-Ansicht (dein bisheriges GUI) -----------------
    def build_planquality_widgets(self):
        # Alles wie vorher, aber mit parent = self.planquality_frame
        self.label = ttk.Label(self.planquality_frame, text="Plan Güte Ansicht")

        # 👉 Back-Button hier hinzufügen
        self.back_btn = ttk.Button(
            self.planquality_frame,
            text="← Back",
            command=self.show_start_frame
        )
        
        self.button = ttk.Button(self.planquality_frame, text="Execute", command=self.on_execute)

        self.ms_plan_generator = PopoverMultiSelect(
            self.planquality_frame,
            header="Plan Generator",
            items=get_values_for_dropdown("plan_generator", "pg_name")
        )
        self.ms_cardinality_provider = PopoverMultiSelect(
            self.planquality_frame,
            header="Cardinality Provider",
            items=get_values_for_dropdown("card_provider", "cp_name")
        )

        self.ms_cf_mat = PopoverMultiSelect(
            self.planquality_frame,
            header="bpi_cf_mat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_mat")
        )
        self.ms_cf_concat = PopoverMultiSelect(
            self.planquality_frame,
            header="bpi_cf_concat",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_concat")
        )
        self.ms_cf_join_bundle = PopoverMultiSelect(
            self.planquality_frame,
            header="bpi_cf_join_bundle",
            items=get_values_for_dropdown("build_plan_instance", "bpi_cf_join_bundle")
        )
        self.ms_cf_bpc = PopoverMultiSelect(
            self.planquality_frame,
            header="bpc_name",
            items=get_values_for_dropdown("build_plan_class", "bpc_name")
        )
        self.ms_cf_host_id = PopoverMultiSelect(
            self.planquality_frame,
            header="wp_cf_host_id",
            items=get_values_for_dropdown("work_package", "wp_cf_host_id")
        )

        self.msplus_cost_function = MultiSelectPlus(
            self.planquality_frame,
            header="Cost Function",
            items=[
                self.ms_cf_mat,
                self.ms_cf_concat,
                self.ms_cf_join_bundle,
                self.ms_cf_bpc,
                self.ms_cf_host_id
            ]
        )
    def layout_planquality_widgets(self):
        # Entspricht deinem bisherigen layout_widgets()
        self.back_btn.pack(anchor="w", padx=10, pady=10)
        self.label.pack(pady=20)
        self.ms_plan_generator.pack(pady=10)
        self.ms_cardinality_provider.pack(pady=10)
        self.msplus_cost_function.pack(pady=10)
        self.button.pack(pady=10)
    
    

# --------------------------------------------------------------------------------------------
    def build_widgets(self):
        self.label = ttk.Label(self, text="Welcome to the Ingredients Visualizer!")
        self.button = ttk.Button(self, text="Execute", command=self.on_execute)
        self.ms_plan_generator = PopoverMultiSelect(self, header="Plan Generator", items=get_values_for_dropdown("plan_generator", "pg_name"))
        self.ms_cardinality_provider = PopoverMultiSelect(self, header="Cardinality Provider", items=get_values_for_dropdown("card_provider", "cp_name"))

        self.ms_cf_mat = PopoverMultiSelect(self, header="bpi_cf_mat", items=get_values_for_dropdown("build_plan_instance", "bpi_cf_mat"))
        self.ms_cf_concat = PopoverMultiSelect(self, header="bpi_cf_concat", items=get_values_for_dropdown("build_plan_instance", "bpi_cf_concat"))
        self.ms_cf_join_bundle = PopoverMultiSelect(self, header="bpi_cf_join_bundle", items=get_values_for_dropdown("build_plan_instance", "bpi_cf_join_bundle"))
        self.ms_cf_bpc = PopoverMultiSelect(self, header="bpc_name", items=get_values_for_dropdown("build_plan_class", "bpc_name"))
        self.ms_cf_host_id = PopoverMultiSelect(self, header="wp_cf_host_id", items=get_values_for_dropdown("work_package", "wp_cf_host_id"))
        self.msplus_cost_function = MultiSelectPlus(self, header="Cost Function", items=[self.ms_cf_mat, self.ms_cf_concat, self.ms_cf_join_bundle, self.ms_cf_bpc, self.ms_cf_host_id])
        

    def layout_widgets(self):
        self.label.pack(pady=20)
        self.ms_plan_generator.pack(pady=10)
        self.ms_cardinality_provider.pack(pady=10)
        self.msplus_cost_function.pack(pady=10)
        self.button.pack(pady=10)

# --------------------------------------------------------------------------------------------
    def open_detail_view(self, row_values):
        """
        row_values ist ein Tupel/List mit allen Spaltenwerten der geklickten Zeile.
        Beispiel: (pg_name, cf, cp_name, avg_lf, median_lf, max_lf, cnt)
        """
        print("Detail-View für:", row_values)

        # Beispiel: wir nehmen pg_name und cp_name als Schlüssel für Detail-Query
        pg_name = row_values[0]
        cp_name = row_values[2]

        # Filter für Detail-SQL bauen (nur als Beispiel)
        pg_filter = build_filter("pg_name", [pg_name])
        cp_filter = build_filter("cp_name", [cp_name])
        join_filter = build_filter("bpi_cf_join_bundle",  )

        # z.B. eine zweite SQL-Abfrage (Query 2) mit zusätzlichen Details
        columns2, result2 = execute_query(
            2,
            filters={
                "PG_FILTER": pg_filter,
                "CP_FILTER": cp_filter,
                "BPI_CF_JOIN_BUNDLE_FILTER": join_filter,
            }
        )

        # Ergebnis wieder in einem neuen Treeview-Fenster anzeigen
        plot_treeview(columns2, result2)

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
    
    def run(self):
        self.mainloop()

