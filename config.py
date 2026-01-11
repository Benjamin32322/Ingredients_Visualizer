from pathlib import Path

# Project Root 
BASE_DIR = Path(__file__).resolve().parent

# DB
DB_PATH = BASE_DIR / "pgb_job_0.db"

# SQL-Files
SQL_DIR = BASE_DIR / "sql"

# Paths für SQL-Files
SQL_PATH_LOSS_FACTOR = SQL_DIR / "Loss-Factor_Analysis.sql"
SQL_PATH_PLAENE = SQL_DIR / "Pläne_treeview.sql"  
SQL_PATH_Q_ERROR = SQL_DIR / "Q-Error_Analysis.sql"
SQL_PATH_P_ERROR = SQL_DIR / "P-Error_Analysis.sql"
SQL_PATH_DETAIL_ANALYSIS = SQL_DIR / "Detail_Analysis.sql"
SQL_PATH_QUERY_ANALYSIS = SQL_DIR / "Query_Analysis.sql"
SQL_PATH_P_ERROR_CALCULATION = SQL_DIR / "P-Error_Calculation.sql"
SQL_PATH_ALL_AGGREGATED = SQL_DIR / "all_aggregated.sql"
SQL_PATH_ALL_SINGLE_QUERY = SQL_DIR / "all_single_query.sql"