# app/pages/utils/db.py
import os, sqlite3
from pathlib import Path
from typing import Iterable, Optional, Tuple

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "cansadometro.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_conn() as con:
        # Cansadometro (único por fecha)
        con.execute("""
        CREATE TABLE IF NOT EXISTS fatigue_entries (
            date TEXT PRIMARY KEY,
            D REAL, QS REAL, AM REAL, S REAL, AF REAL, A REAL,
            score REAL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)
        # Motivometro (único por fecha)
        con.execute("""
        CREATE TABLE IF NOT EXISTS motivation_entries (
            date TEXT PRIMARY KEY,
            EB REAL, AUT REAL, EMO REAL, CLA REAL, REL REAL,
            APO REAL, REC REAL, VAL REAL, PRO REAL,
            score REAL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)
        # Vista de export
        con.execute("""
        CREATE VIEW IF NOT EXISTS vw_export AS
        SELECT
          COALESCE(f.date, m.date) AS date,
          f.score AS fatigue_score, m.score AS motivation_score,
          f.D, f.QS, f.AM, f.S, f.AF, f.A,
          m.EB, m.AUT, m.EMO, m.CLA, m.REL, m.APO, m.REC, m.VAL, m.PRO
        FROM fatigue_entries f
        FULL OUTER JOIN motivation_entries m
          ON f.date = m.date;
        """)
        # Nota: SQLite no soporta FULL OUTER JOIN; creamos vista con UNION
        con.execute("DROP VIEW IF EXISTS vw_export;")
        con.execute("""
        CREATE VIEW vw_export AS
        SELECT f.date as date, f.score as fatigue_score, m.score as motivation_score,
               f.D, f.QS, f.AM, f.S, f.AF, f.A,
               m.EB, m.AUT, m.EMO, m.CLA, m.REL, m.APO, m.REC, m.VAL, m.PRO
        FROM fatigue_entries f
        LEFT JOIN motivation_entries m ON f.date=m.date
        UNION
        SELECT m.date as date, f.score as fatigue_score, m.score as motivation_score,
               f.D, f.QS, f.AM, f.S, f.AF, f.A,
               m.EB, m.AUT, m.EMO, m.CLA, m.REL, m.APO, m.REC, m.VAL, m.PRO
        FROM motivation_entries m
        LEFT JOIN fatigue_entries f ON f.date=m.date
        ;
        """)

def upsert_fatigue(date_iso: str, payload: dict):
    cols = ["date","D","QS","AM","S","AF","A","score"]
    vals = [date_iso] + [payload[k] for k in ["D","QS","AM","S","AF","A","score"]]
    with get_conn() as con:
        con.execute(f"""
            INSERT INTO fatigue_entries ({",".join(cols)})
            VALUES ({",".join(["?"]*len(cols))})
            ON CONFLICT(date) DO UPDATE SET
              D=excluded.D, QS=excluded.QS, AM=excluded.AM, S=excluded.S,
              AF=excluded.AF, A=excluded.A, score=excluded.score
        """, vals)

def upsert_motivation(date_iso: str, payload: dict):
    cols = ["date","EB","AUT","EMO","CLA","REL","APO","REC","VAL","PRO","score"]
    vals = [date_iso] + [payload[k] for k in ["EB","AUT","EMO","CLA","REL","APO","REC","VAL","PRO","score"]]
    with get_conn() as con:
        con.execute(f"""
            INSERT INTO motivation_entries ({",".join(cols)})
            VALUES ({",".join(["?"]*len(cols))})
            ON CONFLICT(date) DO UPDATE SET
              EB=excluded.EB, AUT=excluded.AUT, EMO=excluded.EMO, CLA=excluded.CLA,
              REL=excluded.REL, APO=excluded.APO, REC=excluded.REC, VAL=excluded.VAL,
              PRO=excluded.PRO, score=excluded.score
        """, vals)

def fetch_fatigue_history(limit: Optional[int]=90):
    q = "SELECT date, score, D, QS, AM, S, AF, A FROM fatigue_entries ORDER BY date"
    if limit: q += " LIMIT ?"
    with get_conn() as con:
        cur = con.execute(q, (limit,) if limit else ())
        return cur.fetchall()

def fetch_motivation_history(limit: Optional[int]=90):
    q = "SELECT date, score, EB, AUT, EMO, CLA, REL, APO, REC, VAL, PRO FROM motivation_entries ORDER BY date"
    if limit: q += " LIMIT ?"
    with get_conn() as con:
        cur = con.execute(q, (limit,) if limit else ())
        return cur.fetchall()

def fetch_latest_fatigue() -> Optional[dict]:
    """Returns the most recent fatigue entry as a dict, or None if no entries exist."""
    with get_conn() as con:
        cur = con.execute("""
            SELECT D, QS, AM, S, AF, A
            FROM fatigue_entries
            ORDER BY date DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            return {"D": row[0], "QS": row[1], "AM": row[2], "S": row[3], "AF": row[4], "A": row[5]}
        return None

def fetch_latest_motivation() -> Optional[dict]:
    """Returns the most recent motivation entry as a dict, or None if no entries exist."""
    with get_conn() as con:
        cur = con.execute("""
            SELECT EB, AUT, EMO, CLA, REL, APO, REC, VAL, PRO
            FROM motivation_entries
            ORDER BY date DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            return {
                "EB": row[0], "AUT": row[1], "EMO": row[2], "CLA": row[3],
                "REL": row[4], "APO": row[5], "REC": row[6], "VAL": row[7], "PRO": row[8]
            }
        return None

def fetch_export_df():
    import pandas as pd
    with get_conn() as con:
        return pd.read_sql_query("SELECT * FROM vw_export ORDER BY date;", con)
