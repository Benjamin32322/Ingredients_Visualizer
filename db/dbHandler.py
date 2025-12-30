# dbHandler.py
from config import DB_PATH, SQL_PATH_LOSS_FACTOR, SQL_PATH_Q_ERROR, SQL_PATH_P_ERROR, SQL_PATH_PLAENE, SQL_PATH_DETAIL_ANALYSIS, SQL_PATH_QUERY_ANALYSIS

import duckdb


def connect_to_db():
    
    conn = duckdb.connect(database=DB_PATH)

    return conn

def execute_query(file_nr,filters=None):
    
    if filters is None:
        filters = {}
    
    sql = ""

    match file_nr:
        case 1:
            try:
                sql = open(SQL_PATH_LOSS_FACTOR).read()
                sql = sql.replace("{PG_NAME_FILTER}",filters.get("PG_NAME_FILTER"))
                sql = sql.replace("{CP_NAME_FILTER}", filters.get("CP_NAME_FILTER"))
                sql = sql.replace("{CF_JOIN_BUNDLE_FILTER}", filters.get("BPI_CF_JOIN_BUNDLE_FILTER"))
                sql = sql.replace("{CF_MAT_FILTER}", filters.get("BPI_CF_MAT_FILTER"))
                sql = sql.replace("{CF_CONCAT_FILTER}", filters.get("BPI_CF_CONCAT_FILTER"))
                sql = sql.replace("{CF_HOST_ID_FILTER}", filters.get("WP_CF_HOST_ID_FILTER"))
                sql = sql.replace("{BPC_NAME_FILTER}", filters.get("BPC_NAME_FILTER"))
                sql = sql.replace("{QUERY_NAME_FILTER}", filters.get("QUERY_NAME_FILTER"))

                columns = [desc[0] for desc in connect_to_db().execute(sql).description]
                result = connect_to_db().execute(sql).fetchall()

                return columns, result
            except Exception as ex:
                raise ex
        case 2:
            try:
                sql = open(SQL_PATH_PLAENE).read()
                sql = sql.replace("{PG_NAME_FILTER}",filters.get("PG_NAME_FILTER"))
                sql = sql.replace("{CP_NAME_FILTER}", filters.get("CP_NAME_FILTER"))
                sql = sql.replace("{CF_JOIN_BUNDLE_FILTER}", filters.get("BPI_CF_JOIN_BUNDLE_FILTER"))
                sql = sql.replace("{CF_MAT_FILTER}", filters.get("BPI_CF_MAT_FILTER"))
                sql = sql.replace("{CF_CONCAT_FILTER}", filters.get("BPI_CF_CONCAT_FILTER"))
                sql = sql.replace("{CF_HOST_ID_FILTER}", filters.get("WP_CF_HOST_ID_FILTER"))
                sql = sql.replace("{BPC_NAME_FILTER}", filters.get("BPC_NAME_FILTER"))
                

                columns = [desc[0] for desc in connect_to_db().execute(sql).description]
                result = connect_to_db().execute(sql).fetchall()

                return columns, result
            except Exception as ex:
                raise ex
        case 3:
            try:
                sql = open(SQL_PATH_Q_ERROR).read()
                sql = sql.replace("{PG_NAME_FILTER}",filters.get("PG_NAME_FILTER"))
                sql = sql.replace("{CP_NAME_FILTER}", filters.get("CP_NAME_FILTER"))
                sql = sql.replace("{CF_JOIN_BUNDLE_FILTER}", filters.get("BPI_CF_JOIN_BUNDLE_FILTER"))
                sql = sql.replace("{CF_MAT_FILTER}", filters.get("BPI_CF_MAT_FILTER"))
                sql = sql.replace("{CF_CONCAT_FILTER}", filters.get("BPI_CF_CONCAT_FILTER"))
                sql = sql.replace("{CF_HOST_ID_FILTER}", filters.get("WP_CF_HOST_ID_FILTER"))
                sql = sql.replace("{BPC_NAME_FILTER}", filters.get("BPC_NAME_FILTER"))
                sql = sql.replace("{QUERY_NAME_FILTER}", filters.get("QUERY_NAME_FILTER"))


                columns = [desc[0] for desc in connect_to_db().execute(sql).description]
                result = connect_to_db().execute(sql).fetchall()

                return columns, result
            
            except Exception as ex:
                raise ex
        
        case 4:
            try: 
                sql = open(SQL_PATH_P_ERROR).read()
                sql = sql.replace("{PG_NAME_FILTER}",filters.get("PG_NAME_FILTER"))
                sql = sql.replace("{CP_NAME_FILTER}", filters.get("CP_NAME_FILTER"))
                sql = sql.replace("{CF_JOIN_BUNDLE_FILTER}", filters.get("BPI_CF_JOIN_BUNDLE_FILTER"))
                sql = sql.replace("{CF_MAT_FILTER}", filters.get("BPI_CF_MAT_FILTER"))
                sql = sql.replace("{CF_CONCAT_FILTER}", filters.get("BPI_CF_CONCAT_FILTER"))
                sql = sql.replace("{CF_HOST_ID_FILTER}", filters.get("WP_CF_HOST_ID_FILTER"))
                sql = sql.replace("{BPC_NAME_FILTER}", filters.get("BPC_NAME_FILTER"))
                sql = sql.replace("{QUERY_NAME_FILTER}", filters.get("QUERY_NAME_FILTER"))


                columns = [desc[0] for desc in connect_to_db().execute(sql).description]
                result = connect_to_db().execute(sql).fetchall()

                return columns, result
            except Exception as ex:
                raise ex
        
        case 5:
            try: 
                sql = open(SQL_PATH_DETAIL_ANALYSIS).read()
                sql = sql.replace("{PG_NAME_FILTER}",filters.get("PG_NAME_FILTER"))
                sql = sql.replace("{CP_NAME_FILTER}", filters.get("CP_NAME_FILTER"))
                sql = sql.replace("{CF_JOIN_BUNDLE_FILTER}", filters.get("BPI_CF_JOIN_BUNDLE_FILTER"))
                sql = sql.replace("{CF_MAT_FILTER}", filters.get("BPI_CF_MAT_FILTER"))
                sql = sql.replace("{CF_CONCAT_FILTER}", filters.get("BPI_CF_CONCAT_FILTER"))
                sql = sql.replace("{CF_HOST_ID_FILTER}", filters.get("WP_CF_HOST_ID_FILTER"))
                sql = sql.replace("{BPC_NAME_FILTER}", filters.get("BPC_NAME_FILTER"))
                sql = sql.replace("{DETAIL_METRIC_FILTER}", filters.get("DETAIL_METRIC_FILTER"))
                sql = sql.replace("{QUERY_NAME_FILTER}", filters.get("QUERY_NAME_FILTER"))

                
                print("\n" + "="*80)
                print("DEBUG: Final SQL Query (query_id=5):")
                print("="*80)
                print(sql)
                print("="*80 + "\n")
                
                columns = [desc[0] for desc in connect_to_db().execute(sql).description]
                result = connect_to_db().execute(sql).fetchall()

                return columns, result
            except Exception as ex:
                raise ex
        case 6:
            try:
                sql = open(SQL_PATH_QUERY_ANALYSIS).read()
                columns = [desc[0] for desc in connect_to_db().execute(sql).description]
                result = connect_to_db().execute(sql).fetchall()

                return columns, result
            except Exception as ex:
                raise ex

        case _:
            return None
    
    try:
        sql = sql.replace("{PG_NAME_FILTER}",filters.get("PG_NAME_FILTER"))
        sql = sql.replace("{CP_NAME_FILTER}", filters.get("CP_NAME_FILTER"))
        sql = sql.replace("{CF_JOIN_BUNDLE_FILTER}", filters.get("BPI_CF_JOIN_BUNDLE_FILTER"))
        sql = sql.replace("{CF_MAT_FILTER}", filters.get("BPI_CF_MAT_FILTER"))
        sql = sql.replace("{CF_CONCAT_FILTER}", filters.get("BPI_CF_CONCAT_FILTER"))
        sql = sql.replace("{CF_HOST_ID_FILTER}", filters.get("WP_CF_HOST_ID_FILTER"))
        sql = sql.replace("{BPC_NAME_FILTER}", filters.get("BPC_NAME_FILTER"))

        columns = [desc[0] for desc in connect_to_db().execute(sql).description]
        result = connect_to_db().execute(sql).fetchall()
        return columns, result
        
    except Exception as ex:
        raise ex


 

def get_values_for_dropdown(table_name, column_name):
    conn = connect_to_db()
    query = f"SELECT DISTINCT {column_name} FROM {table_name};"
    results = conn.execute(query).fetchall()
    conn.close()
    return [row[0] for row in results]

def build_filter(column_name, values):
    """
    Erzeugt SQL-Filter abhängig von Anzahl & Typ der Werte.

    Regeln:
    - [] oder None       -> AND 1=1
    - "None"/["None"]    -> AND column_name IS NULL
    - [x]                -> AND column_name = x
    - [x,y]              -> AND (column_name) IN (x,y)
    """

    # Kein Filter
    if values is None or values == []:
        return "AND 1=1"

    # NULL-Case
    if values == "None" or values == ["None"]:
        return f"AND {column_name} IS NULL"

    # Einzelwert (z.B. "BpTrad" oder 0) in Liste packen
    if not isinstance(values, (list, tuple, set)):
        values = [values]

    # Werte säubern + typisieren (direkt in der gleichen Variable)
    new_values = []
    for v in values:
        if v is None:
            continue

        s = str(v).strip()
        if s == "":
            continue

        # Integer?
        if s.lstrip("-").isdigit():
            new_values.append(s)          # numerisch ohne Quotes
        else:
            s = s.replace("'", "''")      # Quotes escapen
            new_values.append(f"'{s}'")   # String mit Quotes

    if not new_values:
        return "AND 1=1"

    # 1 Wert → =
    if len(new_values) == 1:
        return f"AND {column_name} = {new_values[0]}"

    # Mehrere Werte → IN (...)
    in_list = ",".join(new_values)
    return f"AND ({column_name}) IN ({in_list})"




def build_cost_filters(cost_function_dict):
    """
    Erzeugt ein Dictionary mit SQL-Filtern pro Cost-Funktion:
    {'CF_MAT_FILTER': 'AND cf_mat = 0', ...}
    """
    filters = {}

    for key, values in cost_function_dict.items():
        key_upper = key.upper()                       # z.B. cf_mat -> CF_MAT
        filter_key = f"{key_upper}_FILTER"            # -> CF_MAT_FILTER

        filters[filter_key] = build_filter(key, values)

    return filters
