# dbHandler.py

#TODO: Pfade anpassen
DB_PATH = "/Users/benjaminsander/Library/Mobile Documents/com~apple~CloudDocs/B.Sc. Wirtschaftsinformatik/semester_7/Bachelorarbeit/pgb_job_0.db"
SQL_PATH_1 = "/Users/benjaminsander/Library/Mobile Documents/com~apple~CloudDocs/B.Sc. Wirtschaftsinformatik/semester_7/Bachelorarbeit/Ingredients_Visualizer/sql/Plangüte_Exp.sql"

import duckdb


def connect_to_db():
    
    conn = duckdb.connect(database=DB_PATH)
    return conn

def execute_query(file_nr,filters=None):
    
    if filters is None:
        filters = {}

    match file_nr:
        case 1:
            try:
                sql = open(SQL_PATH_1).read()
                sql = sql.replace("{PG_FILTER}",filters.get("PG_FILTER"))
                sql = sql.replace("{CP_FILTER}", filters.get("CP_FILTER"))
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
        case _:
            return None

 

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
    - []  -> AND 1=1
    - [x] -> AND column_name = x   (x numerisch → ohne Quotes)
    - [x,y] -> AND column_name IN (x,y) (numerisch ohne Quotes)
    """

    # Kein Filter
    if not values:
        return "AND 1=1"

    # Werte bereinigen & typisieren
    cleaned = []
    for v in values:
        v = str(v).strip()
        if v == "":
            continue

        # Prüfen, ob Zahl → dann int konvertieren
        if v.isdigit():
            cleaned.append(int(v))     # numerisch
        else:
            cleaned.append(f"'{v}'")  # String mit Quotes

    if not cleaned:
        return "AND 1=1"  

    # 1 Wert = Gleichheitsvergleich
    if len(cleaned) == 1:
        return f"AND {column_name} = {cleaned[0]}"

    # Mehrere Werte = IN (...)
    in_list = ",".join(str(x) for x in cleaned)
    return f"AND {column_name} IN ({in_list})"


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
