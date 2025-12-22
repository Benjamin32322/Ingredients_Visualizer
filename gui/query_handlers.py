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
        print(f"  metrics: {detail_filters['metrics']}")
        print(f"  comparison: {detail_filters['comparison']}")
        print(f"  value1: {detail_filters['value1']}")
        print(f"  value2: {detail_filters['value2']}")
        
        # Check if all required fields are filled
        has_metrics = bool(detail_filters['metrics'])
        has_comparison = detail_filters['comparison'] is not None
        has_value1 = detail_filters['value1'] is not None
        
        print(f"  has_metrics: {has_metrics}")
        print(f"  has_comparison: {has_comparison}")
        print(f"  has_value1: {has_value1}")
        
        # For "zwischen", also check if value2 is filled
        if detail_filters['comparison'] == "zwischen":
            has_value2 = detail_filters['value2'] is not None
            all_fields_filled = has_metrics and has_comparison and has_value1 and has_value2
            print(f"  has_value2: {has_value2}")
        else:
            all_fields_filled = has_metrics and has_comparison and has_value1
        
        print(f"  all_fields_filled: {all_fields_filled}")
        
        # If all detail fields are filled, use DetailQuery (query_id=5)
        if all_fields_filled:
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
                "PG_FILTER": pg_filter,
                "CP_FILTER": cp_filter
            }
        elif query_id == 5:
            # Detail Query requires DETAIL_METRIC_FILTER
            filters = {
                "PG_FILTER": pg_filter,
                "CP_FILTER": cp_filter,
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
        
        # Detail filter (only for query_id=5)
        if detail_filter_values and query_id == 5:
            metric = detail_filter_values.get('metrics', [None])[0]
            comparison = detail_filter_values.get('comparison')
            value1 = detail_filter_values.get('value1')
            value2 = detail_filter_values.get('value2')
            
            if metric and comparison and value1 is not None:
                if comparison == "zwischen" and value2 is not None:
                    parts.append(f"Detail Filter: {metric} {comparison} {value1} und {value2}")
                else:
                    parts.append(f"Detail Filter: {metric} {comparison} {value1}")
        
        return " | ".join(parts)
    
    def build_detail_metric_filter(self, filter_values):
        """
        Convert filter values to SQL HAVING clause condition for DuckDB
        
        Args:
            filter_values (dict): Dictionary from get_detail_filter_values()
                - 'metrics': List of selected metric(s)
                - 'comparison': Comparison type
                - 'value1': First numeric value
                - 'value2': Second numeric value (only for 'zwischen')
        
        Returns:
            str: SQL HAVING clause condition (e.g., "AVG(ps_loss_factor) > 10.0")
        """
        metrics = filter_values['metrics']
        comparison = filter_values['comparison']
        value1 = filter_values['value1']
        value2 = filter_values['value2']
        
        print(f"\nDEBUG: build_detail_metric_filter")
        print(f"  Input - metrics: {metrics}")
        print(f"  Input - comparison: {comparison}")
        print(f"  Input - value1: {value1}")
        print(f"  Input - value2: {value2}")
        
        # Validate inputs
        if not metrics or not comparison or value1 is None:
            print(f"  -> Validation failed, returning '1=1'")
            return "1=1"  # No filtering
        
        # Map metric aliases to actual SQL aggregate functions
        # Note: Only Loss Factor metrics are available in v_ps_base view
        metric_to_sql = {
            "avg_lf": "AVG(ps_loss_factor)",
            "median_lf": "MEDIAN(ps_loss_factor)",
            "max_lf": "MAX(ps_loss_factor)"
        }
        
        # Map German comparison types to SQL operators
        comparison_map = {
            "größer als": ">",
            "kleiner als": "<",
            "gleich": "="
        }
        
        # Use only the first metric for the filter
        metric = metrics[0]
        sql_metric = metric_to_sql.get(metric, metric)
        print(f"  Using metric: {metric} -> SQL: {sql_metric}")
        
        if comparison == "zwischen":
            if value2 is not None:
                result = f"{sql_metric} BETWEEN {value1} AND {value2}"
                print(f"  -> Generated (zwischen): {result}")
                return result
            else:
                print(f"  -> 'zwischen' selected but value2 is None, returning '1=1'")
                return "1=1"  # Invalid 'zwischen' without value2
        else:
            operator = comparison_map.get(comparison, ">")
            result = f"{sql_metric} {operator} {value1}"
            print(f"  -> Generated ({comparison} -> {operator}): {result}")
            return result
