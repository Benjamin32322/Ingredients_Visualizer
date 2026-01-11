# dbHandler.py
"""
Database Handler Module
Handles database connections, SQL query execution, and filter building.
All database column names and SQL placeholders are imported from db_config.py
"""
from config import (
    DB_PATH, SQL_PATH_PLAENE, SQL_PATH_ALL_AGGREGATED, SQL_PATH_ALL_SINGLE_QUERY
)
from db.db_config import FILTER_KEY_MAP, ANALYSIS_TYPES

import duckdb


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def connect_to_db():
    """Create and return a connection to the DuckDB database."""
    return duckdb.connect(database=DB_PATH)


# =============================================================================
# SQL FILTER REPLACEMENT HELPERS
# =============================================================================

def _apply_standard_filters(sql, filters):
    """
    Apply standard filter replacements to SQL string.
    This eliminates code duplication across all query cases.
    
    Args:
        sql (str): SQL string with placeholders
        filters (dict): Dictionary of filter values
    
    Returns:
        str: SQL string with placeholders replaced
    """
    # Standard filter mappings: SQL placeholder -> filter dict key
    standard_replacements = {
        "{PG_NAME_FILTER}": "PG_NAME_FILTER",
        "{CP_NAME_FILTER}": "CP_NAME_FILTER",
        "{BPC_NAME_FILTER}": "BPC_NAME_FILTER",
        "{QUERY_NAME_FILTER}": "QUERY_NAME_FILTER",
        "{CF_JOIN_BUNDLE_FILTER}": "BPI_CF_JOIN_BUNDLE_FILTER",
        "{CF_MAT_FILTER}": "BPI_CF_MAT_FILTER",
        "{CF_CONCAT_FILTER}": "BPI_CF_CONCAT_FILTER",
        "{CF_HOST_ID_FILTER}": "WP_CF_HOST_ID_FILTER",
        "{DETAIL_METRIC_FILTER}": "DETAIL_METRIC_FILTER",
    }
    
    for placeholder, filter_key in standard_replacements.items():
        value = filters.get(filter_key)
        if value is not None:
            sql = sql.replace(placeholder, value)
    
    return sql


def _apply_metric_columns(sql, analysis_type, is_aggregated=True):
    """
    Replace {METRIC_COLUMNS} placeholder based on analysis type.
    Uses centralized ANALYSIS_TYPES configuration.
    
    Args:
        sql (str): SQL string with {METRIC_COLUMNS} placeholder
        analysis_type (str): Analysis type key ("LF", "QERR", "PERR")
        is_aggregated (bool): True for aggregated queries, False for single queries
    
    Returns:
        str: SQL string with metric columns replaced
    """
    analysis_config = ANALYSIS_TYPES.get(analysis_type, ANALYSIS_TYPES["LF"])
    
    if is_aggregated:
        metric_cols = analysis_config["aggregated_columns"]
    else:
        metric_cols = analysis_config["single_column"]
    
    return sql.replace("{METRIC_COLUMNS}", metric_cols)


def _execute_sql(sql, debug_label=None):
    """
    Execute SQL and return columns and results.
    Optionally print debug information.
    
    Args:
        sql (str): SQL query to execute
        debug_label (str): If provided, print debug info with this label
    
    Returns:
        tuple: (columns, results)
    """
    if debug_label:
        print("\n" + "=" * 80)
        print(f"DEBUG: {debug_label}:")
        print("=" * 80)
        print(sql)
        print("=" * 80 + "\n")
    
    conn = connect_to_db()
    columns = [desc[0] for desc in conn.execute(sql).description]
    result = conn.execute(sql).fetchall()
    
    return columns, result


# =============================================================================
# QUERY FILE MAPPING
# =============================================================================

# Maps query IDs to their SQL file paths
# 1: Pläne treeview (detail view)
# 2: All Aggregated (grouped metrics)
# 3: All Single Query (individual query results)
QUERY_FILE_MAP = {
    1: SQL_PATH_PLAENE,
    2: SQL_PATH_ALL_AGGREGATED,
    3: SQL_PATH_ALL_SINGLE_QUERY,
}


# =============================================================================
# MAIN QUERY EXECUTION
# =============================================================================

def execute_query(file_nr, filters=None):
    """
    Execute a SQL query based on the query ID.
    
    Args:
        file_nr (int): Query identifier (1-8)
        filters (dict): Filter values for SQL placeholders
    
    Returns:
        tuple: (columns, results) or None if invalid query ID
    """
    if filters is None:
        filters = {}
    
    # Get SQL file path
    sql_path = QUERY_FILE_MAP.get(file_nr)
    if sql_path is None:
        return None
    
    try:
        # Read SQL template
        sql = open(sql_path).read()
        
        # Apply standard filters
        sql = _apply_standard_filters(sql, filters)
        
        # Handle special cases for metric columns (query 2 and 3)
        if file_nr in (2, 3):
            analysis_type = filters.get("ANALYSIS_TYPE", "LF")
            is_aggregated = (file_nr == 2)
            sql = _apply_metric_columns(sql, analysis_type, is_aggregated)
            
            # Set default for DETAIL_METRIC_FILTER if not present
            if "{DETAIL_METRIC_FILTER}" in sql:
                sql = sql.replace("{DETAIL_METRIC_FILTER}", filters.get("DETAIL_METRIC_FILTER", "1=1"))
            
            debug_label = f"{'All Aggregated' if is_aggregated else 'All Single'} Query (query_id={file_nr}, analysis_type={analysis_type})"
            return _execute_sql(sql, debug_label)
        
        # Standard queries (query 1: Pläne treeview)
        return _execute_sql(sql)
        
    except Exception as ex:
        raise ex


# =============================================================================
# DROPDOWN DATA RETRIEVAL
# =============================================================================

def get_values_for_dropdown(table_name, column_name):
    """
    Get distinct values from a table column for populating dropdowns.
    
    Args:
        table_name (str): Name of the database table
        column_name (str): Name of the column to get values from
    
    Returns:
        list: Distinct values from the column
    """
    conn = connect_to_db()
    query = f"SELECT DISTINCT {column_name} FROM {table_name};"
    results = conn.execute(query).fetchall()
    conn.close()
    return [row[0] for row in results]


# =============================================================================
# FILTER BUILDING
# =============================================================================

def build_filter(column_name, values):
    """
    Build SQL filter clause based on value count and type.
    
    Rules:
    - [] or None         -> AND 1=1 (no filter)
    - "None"/["None"]    -> AND column_name IS NULL
    - [x]                -> AND column_name = x
    - [x, y, ...]        -> AND (column_name) IN (x, y, ...)
    
    Args:
        column_name (str): Database column name to filter on
        values: Single value or list of values to filter by
    
    Returns:
        str: SQL filter clause starting with "AND "
    """
    # No filter
    if values is None or values == []:
        return "AND 1=1"

    # NULL case
    if values == "None" or values == ["None"]:
        return f"AND {column_name} IS NULL"

    # Wrap single value in list
    if not isinstance(values, (list, tuple, set)):
        values = [values]

    # Clean and type values
    processed_values = []
    for v in values:
        if v is None:
            continue

        s = str(v).strip()
        if s == "":
            continue

        # Numeric values (integer check)
        if s.lstrip("-").isdigit():
            processed_values.append(s)  # Numeric without quotes
        else:
            s = s.replace("'", "''")    # Escape quotes
            processed_values.append(f"'{s}'")  # String with quotes

    if not processed_values:
        return "AND 1=1"

    # Single value -> equals
    if len(processed_values) == 1:
        return f"AND {column_name} = {processed_values[0]}"

    # Multiple values -> IN clause
    in_list = ",".join(processed_values)
    return f"AND ({column_name}) IN ({in_list})"


def build_cost_filters(cost_function_dict):
    """
    Build SQL filters for all cost functions.
    
    Args:
        cost_function_dict (dict): Dictionary mapping cost function names to values
            e.g., {'bpi_cf_mat': [0, 1], 'bpi_cf_concat': ['value1']}
    
    Returns:
        dict: Dictionary of filter keys to SQL filter clauses
            e.g., {'BPI_CF_MAT_FILTER': 'AND bpi_cf_mat IN (0,1)', ...}
    """
    filters = {}

    for key, values in cost_function_dict.items():
        key_upper = key.upper()
        filter_key = f"{key_upper}_FILTER"
        filters[filter_key] = build_filter(key, values)

    return filters
