from sqlalchemy import create_engine
import pandas as pd
import datetime

DB_PATH = "data/cansadometro.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def init_db():
    with engine.begin() as conn:
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            score REAL
        )
        """)

def insert_score(metric_type: str, score: float):
    date = datetime.date.today().isoformat()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO metrics (date, type, score) VALUES (?, ?, ?)",
            (date, metric_type, score)
        )

def get_scores(metric_type: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT date, score FROM metrics WHERE type='{metric_type}' ORDER BY date", engine)