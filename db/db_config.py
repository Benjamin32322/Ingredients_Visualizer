# db_config.py
# Centralized database configuration file
# All database column names, table names, SQL placeholders, and mappings are defined here.
# If column/parameter names in the database change, update them ONLY in this file.


# WICHTIG: FÜR NEUE DATENBANK-VERSIONEN ANPASSEN!

# =============================================================================
# TABLE NAMES
# =============================================================================
TABLES = {
    "plan_generator": "plan_generator",
    "cardinality_provider": "card_provider",
    "build_plan_class": "build_plan_class",
    "build_plan_instance": "build_plan_instance",
    "work_package": "work_package",
    "query_graph": "query_graph",
    "ps_base": "v_ps_base",  # View name
}

# =============================================================================
# COLUMN NAMES - Used in SQL queries and filters
# =============================================================================
COLUMNS = {
    # Plan Generator
    "pg_name": "pg_name",
    
    # Cardinality Provider
    "cp_name": "cp_name",
    
    # Build Plan Class
    "bpc_name": "bpc_name",
    
    # Cost Functions (Build Plan Instance)
    "cf_join_bundle": "bpi_cf_join_bundle",
    "cf_mat": "bpi_cf_mat",
    "cf_concat": "bpi_cf_concat",
    
    # Cost Functions (Work Package)
    "cf_host_id": "wp_cf_host_id",
    
    # Query Graph
    "query_name": "ps_qg",
    "qg_name": "qg_name",
    
    # Metrics - Raw values in database
    "loss_factor": "ps_loss_factor",
    "q_error": "ps_qerr_cost_pg",
    "p_error": "ps_p_error",
}

# =============================================================================
# SQL FILTER PLACEHOLDERS - Used in .sql files
# =============================================================================
SQL_PLACEHOLDERS = {
    "PG_NAME_FILTER": "{PG_NAME_FILTER}",
    "CP_NAME_FILTER": "{CP_NAME_FILTER}",
    "BPC_NAME_FILTER": "{BPC_NAME_FILTER}",
    "QUERY_NAME_FILTER": "{QUERY_NAME_FILTER}",
    "CF_JOIN_BUNDLE_FILTER": "{CF_JOIN_BUNDLE_FILTER}",
    "CF_MAT_FILTER": "{CF_MAT_FILTER}",
    "CF_CONCAT_FILTER": "{CF_CONCAT_FILTER}",
    "CF_HOST_ID_FILTER": "{CF_HOST_ID_FILTER}",
    "DETAIL_METRIC_FILTER": "{DETAIL_METRIC_FILTER}",
    "METRIC_COLUMNS": "{METRIC_COLUMNS}",
    "ANALYSIS_TYPE": "{ANALYSIS_TYPE}",
}

# =============================================================================
# FILTER KEY MAPPINGS - Maps internal keys to SQL placeholder keys
# =============================================================================
FILTER_KEY_MAP = {
    "PG_NAME_FILTER": "PG_NAME_FILTER",
    "CP_NAME_FILTER": "CP_NAME_FILTER",
    "BPC_NAME_FILTER": "BPC_NAME_FILTER",
    "QUERY_NAME_FILTER": "QUERY_NAME_FILTER",
    "BPI_CF_JOIN_BUNDLE_FILTER": "CF_JOIN_BUNDLE_FILTER",
    "BPI_CF_MAT_FILTER": "CF_MAT_FILTER",
    "BPI_CF_CONCAT_FILTER": "CF_CONCAT_FILTER",
    "WP_CF_HOST_ID_FILTER": "CF_HOST_ID_FILTER",
    "DETAIL_METRIC_FILTER": "DETAIL_METRIC_FILTER",
    "ANALYSIS_TYPE": "ANALYSIS_TYPE",
}
# =============================================================================
# FETCHING THE VALUES FOR THE DROPDOWNS IN THE UI
# =============================================================================
DROPDOWN_CONFIGS = {
    "plan_generator": {"table": "plan_generator", "column": "pg_name"},
    "cardinality_provider": {"table": "card_provider", "column": "cp_name"},
    "build_plan_class": {"table": "build_plan_class", "column": "bpc_name"},
    "query_selection": {"table": "query_graph", "column": "qg_name"},
    "cf_mat": {"table": "build_plan_instance", "column": "bpi_cf_mat"},
    "cf_concat": {"table": "build_plan_instance", "column": "bpi_cf_concat"},
    "cf_join_bundle": {"table": "build_plan_instance", "column": "bpi_cf_join_bundle"},
    "cf_host_id": {"table": "work_package", "column": "wp_cf_host_id"},
}

# ENDE - AB HIER MUSS (WAHRSCHEINLICH) NICHTS MEHR ANGEPASST WERDEN





# =============================================================================
# METRIC LABELS - Display names for metrics in UI and plots
# =============================================================================
METRIC_LABELS = {
    # Aggregated metrics
    "avg_lf": "Average Loss Factor",
    "median_lf": "Median Loss Factor",
    "max_lf": "Maximum Loss Factor",
    "min_lf": "Minimum Loss Factor",
    "avg_qerr": "Average Q-Error",
    "median_qerr": "Median Q-Error",
    "max_qerr": "Maximum Q-Error",
    "min_qerr": "Minimum Q-Error",
    "avg_perr": "Average P-Error",
    "median_perr": "Median P-Error",
    "max_perr": "Maximum P-Error",
    "min_perr": "Minimum P-Error",
    
    # Raw metrics (single query mode)
    "lf": "Loss Factor",
    "qerr": "Q-Error",
    "perr": "P-Error",
}

# =============================================================================
# METRIC TO SQL MAPPING - Maps metric aliases to SQL expressions
# =============================================================================
METRIC_TO_SQL = {
    # Aggregated mode metrics (used with all_aggregated.sql)
    "avg_lf": f"AVG({COLUMNS['loss_factor']})",
    "median_lf": f"MEDIAN({COLUMNS['loss_factor']})",
    "max_lf": f"MAX({COLUMNS['loss_factor']})",
    "avg_qerr": f"AVG({COLUMNS['q_error']})",
    "median_qerr": f"MEDIAN({COLUMNS['q_error']})",
    "max_qerr": f"MAX({COLUMNS['q_error']})",
    "avg_perr": f"AVG({COLUMNS['p_error']})",
    "median_perr": f"MEDIAN({COLUMNS['p_error']})",
    "max_perr": f"MAX({COLUMNS['p_error']})",
    
    # Raw metrics for single query mode (direct column aliases)
    "lf": "lf",
    "qerr": "qerr",
    "perr": "perr",
}

# =============================================================================
# COMPARISON OPERATORS - Maps UI comparison labels to SQL operators
# =============================================================================
COMPARISON_OPERATORS = {
    "greater than": ">",
    "less than": "<",
    "equal": "=",
    "between": "BETWEEN",  # Special handling required
}

# =============================================================================
# ANALYSIS TYPE MAPPING - Maps analysis types to column configurations
# =============================================================================
ANALYSIS_TYPES = {
    "LF": {
        "aggregated_columns": "avg_lf,\n  median_lf,\n  max_lf,\n  min_lf,\n  ",
        "single_column": "lf\n",
        "display_name": "Loss Factor",
    },
    "QERR": {
        "aggregated_columns": "avg_qerr,\n  median_qerr,\n  max_qerr,\n  min_qerr,\n  ",
        "single_column": "qerr\n",
        "display_name": "Q-Error",
    },
    "PERR": {
        "aggregated_columns": "avg_perr,\n  median_perr,\n  max_perr,\n  min_perr,\n  ",
        "single_column": "perr\n",
        "display_name": "P-Error",
    },
}

# =============================================================================
# UI ANALYSIS PARAMETER MAPPING - Maps UI labels to internal analysis types
# =============================================================================
UI_ANALYSIS_MAP = {
    "Loss Factor Analysis": "Loss Factor",
    "Q-Error Analysis": "Q-Error",
    "P-Error Analysis": "P-Error",
}

# Analysis type to filter key mapping
ANALYSIS_TO_FILTER_KEY = {
    "Loss Factor": "LF",
    "Q-Error": "QERR",
    "P-Error": "PERR",
}

# =============================================================================
# AGGREGATION METRICS BY ANALYSIS TYPE - For populating UI dropdowns
# =============================================================================
AGGREGATION_METRICS = {
    "Loss Factor Analysis": ["avg_lf", "median_lf", "max_lf", "min_lf"],
    "Q-Error Analysis": ["avg_qerr", "median_qerr", "max_qerr", "min_qerr"],
    "P-Error Analysis": ["avg_perr", "median_perr", "max_perr", "min_perr"],
}

# Filter metrics by mode
FILTER_METRICS_AGGREGATED = [
    "avg_lf", "median_lf", "max_lf",
    "avg_qerr", "median_qerr", "max_qerr",
    "avg_perr", "median_perr", "max_perr"
]

FILTER_METRICS_SINGLE_QUERY = ["lf", "qerr", "perr"]

# =============================================================================
# CONFIGURATION PARAMETER DISPLAY NAMES - For plots and labels
# =============================================================================
CONFIG_PARAM_DISPLAY = {
    "pg_name": "PG",
    "cp_name": "CP",
    "bpc_name": "BPC",
    "bpi_cf_join_bundle": "Join Bundle",
    "bpi_cf_mat": "Mat",
    "bpi_cf_concat": "Concat",
    "wp_cf_host_id": "Host ID",
    "ps_qg": "Query",
}

