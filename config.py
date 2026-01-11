# config.py
from pathlib import Path

# Project Root 
BASE_DIR = Path(__file__).resolve().parent

# DB
DB_PATH = BASE_DIR / "pgb_job_0.db"

# SQL-Files
SQL_DIR = BASE_DIR / "sql"

# Paths für SQL-Files
SQL_PATH_PLAENE = SQL_DIR / "Pläne_treeview.sql"  
SQL_PATH_ALL_AGGREGATED = SQL_DIR / "all_aggregated.sql"
SQL_PATH_ALL_SINGLE_QUERY = SQL_DIR / "all_single_query.sql"