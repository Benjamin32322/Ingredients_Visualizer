"""
GUI Query Handlers Module
Handles database query execution and result processing
"""

from db.dbHandler import build_filter, build_cost_filters, execute_query
from plotting.plotting import plot_treeview


class QueryHandlersMixin:
    """Mixin class providing database query execution methods"""
    
    def execute_selected_analysis(self):
        """Execute the analysis based on selected method from MultiSelectPlus"""
        # Get the selected analysis methods
        selected_methods = self.msplus_analysis_methods.get_selected()
        
        # Check which analysis method is selected
        if "Loss Factor Analysis" in selected_methods:
            self.on_execute(query_id=1, analysis_type="Loss Factor")
        elif "Q-Error Analysis" in selected_methods:
            self.on_execute(query_id=3, analysis_type="Q-Error")
        elif "P-Error Analysis" in selected_methods:
            self.on_execute(query_id=4, analysis_type="P-Error")
        else:
            self.update_status("Please select an analysis method")
    
    def on_execute(self, query_id=1, analysis_type="Loss Factor"):
        """
        Execute analysis query
        
        Args:
            query_id (int): Query identifier (1 for Loss Factor, 3 for Q-Error, 4 for P-Error)
            analysis_type (str): Type of analysis for status message
        """
        selected_pg = self.ms_plan_generator.get_selected()
        selected_cp = self.ms_cardinality_provider.get_selected()
        selected_cf = self.msplus_cost_function.get_selected()

        pg_filter = build_filter("pg_name", selected_pg)
        cp_filter = build_filter("cp_name", selected_cp)
        cf_filter = build_cost_filters(selected_cf)
        
        # Use different filter names based on query type
        if query_id == 1:
            filters = {
                "PG_FILTER": pg_filter,
                "CP_FILTER": cp_filter
            }
        else:
            filters = {
                "PG_NAME_FILTER": pg_filter,
                "CP_NAME_FILTER": cp_filter
            }
        
        filters.update(cf_filter)
        columns, result = execute_query(query_id, filters=filters)

        plot_treeview(columns, result)
        
        # Update status and restore focus
        self.update_status(f"{analysis_type} query executed - {len(result)} results found")
        self.after(100, self.restore_entry_focus)
    
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
