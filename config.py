from pathlib import Path

# Project Root 
BASE_DIR = Path(__file__).resolve().parent

# DB
DB_PATH = BASE_DIR / "pgb_job_0.db"

# SQL-Files
SQL_DIR = BASE_DIR / "sql"

# Paths für SQL-Files
SQL_PATH_1 = SQL_DIR / "PlanQuality.sql"
SQL_PATH_2 = SQL_DIR / "Pläne_Plangüte.sql"  
SQL_PATH_3 = SQL_DIR / "CostFunction.sql"
SQL_PATH_4 = SQL_DIR / "CardinalityEstimator.sql"