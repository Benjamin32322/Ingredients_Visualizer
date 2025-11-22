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

        # Erstellen der Frames
        self.first_frame = ttk.Frame(self)
        self.second_frame = ttk.Frame(self)
        self.third_frame = ttk.Frame(self)

        # Header Frame für alle Frames
        self.header_frame = ttk.Frame(self.second_frame)
        self.header_frame.pack(side="top", fill="x")

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
        self.show_first_frame()


    # ----------------- First-Frame -----------------------------------------------------------------
    
    def build_first_frame(self):
        
        self.welcome_label = ttk.Label(self.first_frame, text="Welcome to the Ingredients Visualizer!")

        self.forward_button = ttk.Button(
            self.first_frame,
            text="→ Forward",
            command=self.show_second_frame
        )
        
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
        self.forward_button.pack(anchor="e", padx=10, pady=10)
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
        
        # Forward Button
        self.forward_button = ttk.Button(
            self.header_frame,
            text="→ Forward",
            command=self.show_third_frame
        )
        # Back Button
        self.back_button = ttk.Button(
            self.header_frame,
            text="← Back",
            command=self.show_first_frame
        )
        
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
        self.back_button.pack(side="left", padx=10, pady=10)
        self.forward_button.pack(side="right", padx=10, pady=10)
        self.loss_factor_button.pack(pady=10)
        self.q_error_button.pack(pady=10)
        self.p_error_button.pack(pady=10)


    
    # ------------------------------ THIRD FRAME --------------------------------------------------------
    
    def build_third_frame(self):
        # Back Button
        self.back_button = ttk.Button(
            self.third_frame,
            text="← Back",
            command=self.show_second_frame
        )

        self.forward_button = ttk.Button(
            self.third_frame,
            text="→ Forward",
            command=self.show_first_frame
        )

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

        self.eingabe_detail = ttk.Entry(self.third_frame)
        # Funktioniert noch nicht
        
        if self.ms_filter_detail.get_selected() == "zwischen":
            self.eingabe_detail_2 = ttk.Entry(self.third_frame)
            self.eingabe_detail_2.pack(pady=10)

    def layout_third_frame(self):
        self.back_button.pack(side="left", padx=10, pady=10)
        self.forward_button.pack(side="right", padx=10, pady=10)
        self.ms_detail_view.pack(pady=10)
        self.ms_filter_detail.pack(pady=10)
        self.eingabe_detail.pack(pady=10)
      
    

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
    
# --------------------------- WECHSEL ZWISCHEN DEN FRAMES ----------------------------------------------------------
    
    def show_first_frame(self):
        """Zeigt wieder den Start-Screen an."""
        self.second_frame.pack_forget()
        self.third_frame.pack_forget()  
        self.first_frame.pack(fill="both", expand=True)
    
    
    def show_second_frame(self):
        self.first_frame.pack_forget()
        self.third_frame.pack_forget()
        self.second_frame.pack(fill="both", expand=True)
    
    def show_third_frame(self):
        self.first_frame.pack_forget()
        self.second_frame.pack_forget()
        self.third_frame.pack(fill="both", expand=True)


# ------------------------ RUN-METHODE --------------------------------------------------------------
    def run(self):
        self.mainloop()