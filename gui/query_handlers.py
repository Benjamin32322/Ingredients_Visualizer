"""
GUI Query Handlers Module
Handles database query execution and result processing
"""

from db.dbHandler import build_filter, build_cost_filters, execute_query
from plotting.plotting import plot_treeview


class QueryHandlersMixin:
    """Mixin class providing database query execution methods"""
    
    def choose_correct_query(self):
        """
        Determine the correct query based on GUI inputs.
        If all detail filter fields have values, use query_id=5 (DetailQuery).
        Otherwise, route to the selected analysis method.
        """
        # Check if all detail filter fields have values
        detail_filters = self.get_detail_filter_values()
        print("=" * 60)
        print("DEBUG: choose_correct_query - detail_filters:")
        print(f"  Number of filter rows: {len(detail_filters)}")
        
        # Check if at least one complete filter exists
        has_complete_filter = False
        for i, filter_row in enumerate(detail_filters):
            print(f"  Filter {i+1}:")
            print(f"    metric: {filter_row.get('metric')}")
            print(f"    comparison: {filter_row.get('comparison')}")
            print(f"    value: {filter_row.get('value')}")
            
            # A filter is complete if it has metric, comparison, and value
            if (filter_row.get('metric') and 
                filter_row.get('comparison') and 
                filter_row.get('value') is not None):
                has_complete_filter = True
        
        print(f"  has_complete_filter: {has_complete_filter}")
        
        # If at least one complete filter exists, use DetailQuery (query_id=5)
        if has_complete_filter:
            print("  -> Using DetailQuery (query_id=5)")
            self.on_execute(query_id=5, analysis_type="Detail Query")
        else:
            # Otherwise, execute based on selected analysis method
            selected_methods = self.ms_analysis_parameter.get_selected()
            print(f"  -> Using selected analysis: {selected_methods}")
            
            if "Loss Factor Analysis" in selected_methods:
                self.on_execute(query_id=1, analysis_type="Loss Factor")
            elif "Q-Error Analysis" in selected_methods:
                self.on_execute(query_id=3, analysis_type="Q-Error")
            elif "P-Error Analysis" in selected_methods:
                self.on_execute(query_id=4, analysis_type="P-Error")
            elif "Query Analysis" in selected_methods:
                self.on_execute(query_id=6, analysis_type="Detail Query")
            else:
                self.update_status("Please select an analysis method")
        print("=" * 60)
    
    def on_execute(self, query_id=1, analysis_type="Loss Factor"):
        """
        Execute analysis query
        
        Args:
            query_id (int): Query identifier (1 for Loss Factor, 3 for Q-Error, 4 for P-Error, 5 for Detail Query)
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
                "PG_NAME_FILTER": pg_filter,
                "CP_NAME_FILTER": cp_filter
            }
        elif query_id == 5:
            # Detail Query requires DETAIL_METRIC_FILTER
            filters = {
                "PG_NAME_FILTER": pg_filter,
                "CP_NAME_FILTER": cp_filter,
                "BPC_NAME_FILTER": ""  # No BPC filter for DetailQuery
            }
            # Build detail metric filter
            detail_filter_values = self.get_detail_filter_values()
            detail_metric_filter = self.build_detail_metric_filter(detail_filter_values)
            print("\nDEBUG: on_execute (query_id=5)")
            print(f"  detail_filter_values: {detail_filter_values}")
            print(f"  Generated DETAIL_METRIC_FILTER: {detail_metric_filter}")
            filters["DETAIL_METRIC_FILTER"] = detail_metric_filter
        else:
            filters = {
                "PG_NAME_FILTER": pg_filter,
                "CP_NAME_FILTER": cp_filter
            }
        
        filters.update(cf_filter)
        columns, result = execute_query(query_id, filters=filters)

        # Build parameter summary for display and export
        params_summary = self.build_params_summary(
            query_id=query_id,
            analysis_type=analysis_type,
            selected_pg=selected_pg,
            selected_cp=selected_cp,
            selected_cf=selected_cf,
            detail_filter_values=detail_filter_values if query_id == 5 else None
        )
        
        plot_treeview(columns, result, params_summary)
        
        # Update status and restore focus
        self.update_status(f"{analysis_type} query executed - {len(result)} results found")
        self.after(100, self.restore_entry_focus)
    
    def build_params_summary(self, query_id, analysis_type, selected_pg, selected_cp, selected_cf, detail_filter_values=None):
        """
        Build a summary string of all query parameters for display and export
        
        Returns:
            str: Formatted parameter summary
        """
        parts = []
        parts.append(f"Analysis Type: {analysis_type}")
        parts.append(f"Plan Generators: {', '.join(selected_pg) if selected_pg else 'All'}")
        parts.append(f"Cardinality Providers: {', '.join(selected_cp) if selected_cp else 'All'}")
        
        # Cost functions
        cf_parts = []
        for key, values in selected_cf.items():
            if values:
                cf_name = key.replace('_', ' ').title()
                cf_parts.append(f"{cf_name}: {', '.join(values)}")
        if cf_parts:
            parts.append(f"Cost Functions: {' | '.join(cf_parts)}")
        else:
            parts.append("Cost Functions: All")
        
        # Detail filters (only for query_id=5)
        if detail_filter_values and query_id == 5 and isinstance(detail_filter_values, list):
            filter_parts = []
            for filter_dict in detail_filter_values:
                metric = filter_dict.get('metric')
                comparison = filter_dict.get('comparison')
                value = filter_dict.get('value')
                
                if metric and comparison and value is not None:
                    filter_parts.append(f"{metric} {comparison} {value}")
            
            if filter_parts:
                parts.append(f"Detail Filters: {', '.join(filter_parts)}")
        
        return " | ".join(parts)
    
    def build_detail_metric_filter(self, filter_values):
        """
        Convert filter values to SQL HAVING clause condition for DuckDB
        
        Args:
            filter_values (list): List of filter dictionaries from get_detail_filter_values()
                Each dict contains:
                - 'metric': Selected metric (e.g., 'avg_lf')
                - 'comparison': Comparison type
                - 'value': Numeric value
        
        Returns:
            str: SQL HAVING clause condition with multiple filters combined with AND
                 (e.g., "AVG(ps_loss_factor) > 10.0 AND MEDIAN(ps_loss_factor) < 50.0")
        """
        print(f"\nDEBUG: build_detail_metric_filter")
        print(f"  Input - filter_values: {filter_values}")
        
        # Validate inputs
        if not filter_values:
            print(f"  -> No filters provided, returning '1=1'")
            return "1=1"  # No filtering
        
        # Map metric aliases to actual SQL aggregate functions
        # Note: Only Loss Factor metrics are available in v_ps_base view
        metric_to_sql = {
            "avg_lf": "AVG(ps_loss_factor)",
            "median_lf": "MEDIAN(ps_loss_factor)",
            "max_lf": "MAX(ps_loss_factor)",
            "avg_qerr": "AVG(ps_qerr)",
            "median_qerr": "MEDIAN(ps_qerr)",
            "max_qerr": "MAX(ps_qerr)",
            "avg_perr": "AVG(ps_perr)",
            "median_perr": "MEDIAN(ps_perr)",
            "max_perr": "MAX(ps_perr)"
        }
        
        # Map German comparison types to SQL operators
        comparison_map = {
            "größer als": ">",
            "kleiner als": "<",
            "gleich": "="
        }
        
        # Build SQL conditions for each filter
        conditions = []
        for i, filter_dict in enumerate(filter_values):
            metric = filter_dict.get('metric')
            comparison = filter_dict.get('comparison')
            value = filter_dict.get('value')
            
            # Skip incomplete filters
            if not metric or not comparison or value is None:
                print(f"  Filter {i+1}: Incomplete, skipping")
                continue
            
            sql_metric = metric_to_sql.get(metric, metric)
            operator = comparison_map.get(comparison, ">")
            condition = f"{sql_metric} {operator} {value}"
            conditions.append(condition)
            print(f"  Filter {i+1}: {metric} {comparison} {value} -> {condition}")
        
        # Combine all conditions with AND
        if conditions:
            result = " AND ".join(conditions)
            print(f"  -> Final SQL: {result}")
            return result
        else:
            print(f"  -> No valid conditions, returning '1=1'")
            return "1=1"
