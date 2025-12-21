# Example: How to use get_detail_filter_values() method
# This file demonstrates how to retrieve and use the detail filter values

"""
The get_detail_filter_values() method returns a dictionary with the following structure:

{
    'metrics': ['avg_lf', 'median_qerr'],  # List of selected metrics
    'comparison': 'größer als',             # Comparison type
    'value1': 10.0,                         # First numeric value
    'value2': None                          # Second value (only for 'zwischen')
}

Usage Examples:
"""

def example_usage_in_execute_method(self):
    """Example of how to use this in an execute method"""
    
    # Get all detail filter values
    filter_values = self.get_detail_filter_values()
    
    # Extract individual components
    selected_metrics = filter_values['metrics']      # e.g., ['avg_lf']
    comparison_type = filter_values['comparison']    # e.g., 'größer als'
    value1 = filter_values['value1']                 # e.g., 10.0
    value2 = filter_values['value2']                 # e.g., None or 20.0
    
    # Example 1: Check if user selected any metrics
    if not selected_metrics:
        print("No metrics selected!")
        return
    
    # Example 2: Build SQL condition based on comparison type
    if comparison_type == "größer als":
        sql_operator = ">"
        sql_condition = f"{selected_metrics[0]} {sql_operator} {value1}"
        # Result: "avg_lf > 10.0"
    
    elif comparison_type == "kleiner als":
        sql_operator = "<"
        sql_condition = f"{selected_metrics[0]} {sql_operator} {value1}"
        # Result: "avg_lf < 10.0"
    
    elif comparison_type == "gleich":
        sql_operator = "="
        sql_condition = f"{selected_metrics[0]} {sql_operator} {value1}"
        # Result: "avg_lf = 10.0"
    
    elif comparison_type == "zwischen":
        if value1 is not None and value2 is not None:
            sql_condition = f"{selected_metrics[0]} BETWEEN {value1} AND {value2}"
            # Result: "avg_lf BETWEEN 5.0 AND 15.0"
        else:
            print("Two values required for 'zwischen' comparison!")
            return
    
    # Example 3: Handle multiple metrics (if your UI allows)
    if len(selected_metrics) > 1:
        conditions = []
        for metric in selected_metrics:
            if comparison_type == "zwischen" and value1 and value2:
                conditions.append(f"{metric} BETWEEN {value1} AND {value2}")
            elif value1 is not None:
                operator_map = {
                    "größer als": ">",
                    "kleiner als": "<",
                    "gleich": "="
                }
                operator = operator_map.get(comparison_type, ">")
                conditions.append(f"{metric} {operator} {value1}")
        
        # Combine with AND
        sql_condition = " AND ".join(conditions)
        # Result: "avg_lf > 10.0 AND median_qerr > 10.0"
    
    print(f"Generated SQL condition: {sql_condition}")
    return sql_condition


def build_detail_filter_for_query(filter_values):
    """
    Convert filter values to SQL HAVING clause
    
    Args:
        filter_values (dict): Dictionary from get_detail_filter_values()
    
    Returns:
        str: SQL HAVING clause condition
    """
    metrics = filter_values['metrics']
    comparison = filter_values['comparison']
    value1 = filter_values['value1']
    value2 = filter_values['value2']
    
    # Validate inputs
    if not metrics or not comparison or value1 is None:
        return "1=1"  # No filtering
    
    # Map German comparison types to SQL operators
    comparison_map = {
        "größer als": ">",
        "kleiner als": "<",
        "gleich": "="
    }
    
    conditions = []
    
    for metric in metrics:
        if comparison == "zwischen":
            if value2 is not None:
                conditions.append(f"{metric} BETWEEN {value1} AND {value2}")
        else:
            operator = comparison_map.get(comparison, ">")
            conditions.append(f"{metric} {operator} {value1}")
    
    # Combine multiple conditions with AND
    return " AND ".join(conditions) if conditions else "1=1"


# Example outputs:
"""
Input:
    metrics=['avg_lf'], comparison='größer als', value1=10.0, value2=None
Output:
    "avg_lf > 10.0"

Input:
    metrics=['median_lf'], comparison='zwischen', value1=5.0, value2=15.0
Output:
    "median_lf BETWEEN 5.0 AND 15.0"

Input:
    metrics=['avg_lf', 'median_qerr'], comparison='kleiner als', value1=20.0, value2=None
Output:
    "avg_lf < 20.0 AND median_qerr < 20.0"
"""
