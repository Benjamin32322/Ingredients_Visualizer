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
SQL_PATH_DETAILED_QUERY = SQL_DIR / "Detailed_Query_Configuration.sql"
SQL_PATH_QUERY_ANALYSIS = SQL_DIR / "Query_Analysis.sql"