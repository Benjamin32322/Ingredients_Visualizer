# Unified Query Architecture - Simplified Implementation

## Overview

The query system has been **drastically simplified** to use only 2 SQL files that handle all scenarios:

### 🔹 **`all_aggregated.sql`** (query_id=7)
- Used when **NO specific queries** are selected
- Returns **aggregated metrics** (AVG, MEDIAN, MAX, MIN)
- Groups by configuration parameters

### 🔹 **`all_single_query.sql`** (query_id=8)
- Used when **specific queries ARE selected** in "Query Selection"
- Returns **individual row results** (no aggregation)
- Includes `ps_qg` (query graph) column

---

## How It Works

### 1. **Query Routing Logic** (Simplified!)

```python
def choose_correct_query(self):
    # Get selected analysis type (LF, Q-Error, or P-Error)
    analysis_type = determine_analysis_type()
    
    # Route based on Query Selection
    if user_selected_specific_queries:
        use query_id=8  # all_single_query.sql
    else:
        use query_id=7  # all_aggregated.sql
```

**That's it!** No more complex routing logic with 6 different query files.

---

## 2. **Both SQL Files Share the Same Structure**

### Common Features:
✅ Compute **ALL metrics** (Loss Factor, Q-Error, P-Error) in a CTE  
✅ Filter on **ANY metric** regardless of selected analysis type  
✅ Display only **relevant columns** based on `ANALYSIS_TYPE` parameter  

### Key Difference:
- **all_aggregated.sql**: Uses `AVG()`, `MEDIAN()`, `MAX()`, `MIN()` + `GROUP BY`
- **all_single_query.sql**: No aggregation, returns individual rows with `ps_qg`

---

## 3. **Parameter System**

Both queries use the same filters:

| Filter | Purpose |
|--------|---------|
| `{ANALYSIS_TYPE}` | Controls which columns to display (LF/QERR/PERR) |
| `{METRIC_COLUMNS}` | Replaced with appropriate column list |
| `{DETAIL_METRIC_FILTER}` | WHERE/HAVING conditions for filtering |
| `{PG_NAME_FILTER}`, `{CP_NAME_FILTER}`, etc. | Standard configuration filters |

---

## 4. **Column Selection Examples**

### If user selects "Loss Factor Analysis":
```sql
-- METRIC_COLUMNS is replaced with:
avg_lf,
median_lf,
max_lf,
min_lf,
cnt  -- (only in aggregated)
```

### If user selects "P-Error Analysis":
```sql
-- METRIC_COLUMNS is replaced with:
avg_perr,
median_perr,
max_perr,
min_perr,
cnt  -- (only in aggregated)
```

---

## 5. **Filter Configuration Works Across All Metrics**

**Example Scenario:**
- User selects: **"P-Error Analysis"**
- User adds filter: `avg_lf > 2.0 AND median_qerr < 15`

**What happens:**
1. CTE computes **all metrics** (lf, qerr, perr)
2. Filters applied: `avg_lf > 2.0 AND median_qerr < 15`
3. Only **P-Error columns** displayed in results

This allows **cross-metric filtering**! 🎯

---

## Benefits of Simplified Architecture

### ✅ **Reduced Complexity**
- From **6 query files** → **2 query files**
- From **complex routing logic** → **1 simple if/else**

### ✅ **Unified Behavior**
- All analysis types work the same way
- Consistent filtering across all metrics
- Same parameter system for both queries

### ✅ **Easier Maintenance**
- Changes only need to be made in 2 files
- Clear separation: aggregated vs single results

### ✅ **More Flexible**
- Filter on any metric regardless of display
- Easy to add new analysis types
- Simple to understand and debug

---

## Old vs New Architecture

### **OLD** (6 files):
```
Loss-Factor_Analysis.sql   → Only LF metrics, aggregated
Q-Error_Analysis.sql       → Only QERR metrics, aggregated
P-Error_Analysis.sql       → Only PERR metrics, aggregated
Detail_Analysis.sql        → LF with filters
Query_Analysis.sql         → Single queries
+ complex routing logic
```

### **NEW** (2 files):
```
all_aggregated.sql   → ALL metrics, aggregated, show selected
all_single_query.sql → ALL metrics, single rows, show selected
+ simple if/else routing
```

---

## Implementation Files

### Modified Files:
1. **`sql/all_aggregated.sql`** - CTE-based aggregated query
2. **`sql/all_single_query.sql`** - CTE-based single query
3. **`config.py`** - Added SQL_PATH_ALL_SINGLE_QUERY
4. **`db/dbHandler.py`** - Added case 7 and case 8
5. **`gui/query_handlers.py`** - Simplified choose_correct_query() and on_execute()

---

## Usage in GUI

**For Aggregated Results:**
- Don't select anything in "Query Selection"
- Select analysis type (LF/Q-Error/P-Error)
- Optionally add filters
- ➡️ Uses `all_aggregated.sql`

**For Single Query Results:**
- Select specific queries in "Query Selection"
- Select analysis type
- Optionally add filters
- ➡️ Uses `all_single_query.sql`

---

## Summary

The new architecture is **dramatically simpler** while being **more powerful**:
- 2 SQL files instead of 6
- Simple routing logic
- Cross-metric filtering
- Unified parameter system
- Easier to maintain and extend
