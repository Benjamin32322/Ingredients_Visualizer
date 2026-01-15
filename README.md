# Ingredients Visualizer

A desktop application for analyzing and visualizing query plan metrics from a DuckDB database. Developed as part of a Bachelor Thesis in Business Informatics.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Overview](#project-overview)
3. [Configuration for New Database Versions](#configuration-for-new-database-versions)
4. [SQL Architecture](#sql-architecture)
5. [Project Structure](#project-structure)
6. [Technical Details](#technical-details)

---

## Quick Start

1. **Place the database file** (`pgb_job_0.db`) in the project root directory
2. **Install dependencies**:
   ```bash
   pip install duckdb pandas matplotlib
   ```
3. **Run the application**:
   ```bash
   python app.py
   ```

---

## Project Overview

The Ingredients Visualizer enables analysis of query plan metrics through:

- **Loss Factor Analysis** - Measures plan quality
- **Q-Error Analysis** - Cardinality estimation errors
- **P-Error Analysis** - Cost estimation errors

### Features

- Interactive filtering by configuration parameters (Plan Generator, Cardinality Provider, etc.)
- Multiple visualization types: Bar Charts, Box Plots, Scatter Plots, Line Graphs
- Aggregated mode (metrics across all queries) and Single Query mode
- Logarithmic scaling for Q-Error and P-Error (handles extreme values like 1e+38)
- Export functionality for plots and data

---

## Configuration for New Database Versions

### ⚠️ IMPORTANT: When using a new database version, only TWO files need to be modified:

### 1. Database File Path (`config.py`)

Update the database filename if it changes:

```python
# config.py
DB_PATH = BASE_DIR / "pgb_job_0.db"  # ← Change filename here
```

### 2. Database Schema Configuration (`db/db_config.py`)

**This is the central configuration file.** All database column names and table names are defined here. If column names change in a new database version, update them **ONLY** in this file.

#### Section: TABLE NAMES
```python
TABLES = {
    "plan_generator": "plan_generator",      # ← Table name in DB
    "cardinality_provider": "card_provider", # ← Table name in DB
    "build_plan_class": "build_plan_class",
    "build_plan_instance": "build_plan_instance",
    "work_package": "work_package",
    "query_graph": "query_graph",
    "ps_base": "v_ps_base",                  # ← Main view name
}
```

#### Section: COLUMN NAMES
```python
COLUMNS = {
    # Plan Generator
    "pg_name": "pg_name",           # ← Column name in DB
    
    # Cardinality Provider
    "cp_name": "cp_name",           # ← Column name in DB
    
    # Build Plan Class
    "bpc_name": "bpc_name",         # ← Column name in DB
    
    # Cost Functions (Build Plan Instance)
    "cf_join_bundle": "bpi_cf_join_bundle",  # ← Column name in DB
    "cf_mat": "bpi_cf_mat",
    "cf_concat": "bpi_cf_concat",
    
    # Cost Functions (Work Package)
    "cf_host_id": "wp_cf_host_id",  # ← Column name in DB
    
    # Query Graph
    "query_name": "ps_qg",          # ← Column name in DB
    "qg_name": "qg_name",
    
    # Metrics - Raw values in database
    "loss_factor": "ps_loss_factor",      # ← Metric column in DB
    "q_error": "ps_qerr_cost_pg",         # ← Metric column in DB
    "p_error": "ps_p_error",              # ← Metric column in DB
}
```

#### Section: DROPDOWN CONFIGURATIONS
Defines which table and column to query for each UI dropdown:

```python
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
```

---

## SQL Architecture

### SQL Files Location: `sql/`

| File | Purpose |
|------|---------|
| `all_aggregated.sql` | Computes aggregated metrics (AVG, MEDIAN, MAX, MIN) across all queries |
| `all_single_query.sql` | Returns individual query results (no aggregation) |
| `Pläne_treeview.sql` | Displays all plan configurations in the TreeView |

### How SQL Queries Work

The SQL files use **placeholder syntax** that gets replaced at runtime:

```sql
WHERE 1=1
    {BPC_NAME_FILTER}      -- Replaced with: AND bpc_name IN ('value1', 'value2')
    {PG_NAME_FILTER}       -- Replaced with: AND pg_name IN ('value1')
    {DETAIL_METRIC_FILTER} -- Replaced with: avg_lf > 1.5
```

### Placeholder Reference

| Placeholder | Purpose | Example Replacement |
|-------------|---------|---------------------|
| `{PG_NAME_FILTER}` | Plan Generator filter | `AND pg_name IN ('DPccp')` |
| `{CP_NAME_FILTER}` | Cardinality Provider filter | `AND cp_name IN ('trueCE')` |
| `{BPC_NAME_FILTER}` | Build Plan Class filter | `AND bpc_name IN ('full')` |
| `{QUERY_NAME_FILTER}` | Query selection filter | `AND ps_qg IN ('1a', '2a')` |
| `{CF_JOIN_BUNDLE_FILTER}` | Cost function filter | `AND bpi_cf_join_bundle IN ('Cout')` |
| `{CF_MAT_FILTER}` | Materialization cost filter | `AND bpi_cf_mat IN ('Cout')` |
| `{CF_CONCAT_FILTER}` | Concatenation cost filter | `AND bpi_cf_concat IN ('Cout')` |
| `{CF_HOST_ID_FILTER}` | Host ID filter | `AND wp_cf_host_id IN (0)` |
| `{DETAIL_METRIC_FILTER}` | Metric filter condition | `avg_lf > 1.5 AND max_lf < 10` |
| `{METRIC_COLUMNS}` | Dynamic column selection | `avg_lf, median_lf, max_lf, min_lf,` |

### Filter Building Logic (`db/dbHandler.py`)

The `_apply_standard_filters()` function handles placeholder replacement:

```python
def _apply_standard_filters(sql, filters):
    standard_replacements = {
        "{PG_NAME_FILTER}": "PG_NAME_FILTER",
        "{CP_NAME_FILTER}": "CP_NAME_FILTER",
        "{BPC_NAME_FILTER}": "BPC_NAME_FILTER",
        # ... etc
    }
    for placeholder, filter_key in standard_replacements.items():
        value = filters.get(filter_key)
        if value is not None:
            sql = sql.replace(placeholder, value)
    return sql
```

### Analysis Type Column Selection

The `{METRIC_COLUMNS}` placeholder is replaced based on the selected analysis type:

| Analysis Type | Aggregated Columns | Single Query Column |
|---------------|-------------------|---------------------|
| LF (Loss Factor) | `avg_lf, median_lf, max_lf, min_lf` | `lf` |
| QERR (Q-Error) | `avg_qerr, median_qerr, max_qerr, min_qerr` | `qerr` |
| PERR (P-Error) | `avg_perr, median_perr, max_perr, min_perr` | `perr` |

---

## Project Structure

```
Ingredients_Visualizer/
│
├── app.py                    # Application entry point
├── config.py                 # Database path and SQL file paths
├── utils.py                  # Shared utility functions
├── pgb_job_0.db             # DuckDB database file (must be added)
│
├── db/
│   ├── db_config.py         # ⭐ CENTRAL CONFIG: All DB column/table names
│   └── dbHandler.py         # Database connection and query execution
│
├── gui/
│   ├── gui.py               # Main GUI class (Tkinter)
│   ├── query_handlers.py    # Query execution logic
│   ├── multiSelect.py       # Custom multi-select dropdown widget
│   ├── responsiveness.py    # Window resizing handlers
│   └── style.py             # GUI styling
│
├── plotting/
│   ├── plotting.py          # Chart creation (bar, box, scatter, line)
│   ├── style_plot.py        # Plot color palette and styling
│   └── treeview.py          # TreeView display component
│
└── sql/
    ├── all_aggregated.sql   # Aggregated metrics query
    ├── all_single_query.sql # Single query results
    └── Pläne_treeview.sql   # Plan overview query
```

---

## Technical Details

### Dependencies

- **Python 3.10+**
- **DuckDB** - Embedded analytical database
- **Pandas** - Data manipulation
- **Matplotlib** - Visualization
- **Tkinter** - GUI framework (included with Python)

### Query Flow

1. User selects filters in GUI
2. `query_handlers.py` builds filter dictionary
3. `dbHandler.py` loads SQL template and replaces placeholders
4. Query executes against DuckDB
5. Results displayed in TreeView or as plot

### Metric Scaling

- **Loss Factor**: Linear scale (values typically 1-10)
- **Q-Error / P-Error**: Logarithmic scale (values can reach 1e+38)

The plotting module automatically detects metric type and applies appropriate scaling.

---

## Adding New Metrics or Analysis Types

To add a new analysis type, update these sections in `db/db_config.py`:

1. **COLUMNS** - Add raw column name
2. **METRIC_LABELS** - Add display names
3. **METRIC_TO_SQL** - Add SQL expressions
4. **ANALYSIS_TYPES** - Define aggregated and single column sets
5. **AGGREGATION_METRICS** - Add to UI dropdown options

---

## Author

Benjamin Sander  
Bachelor Thesis - Business Informatics  
January 2026