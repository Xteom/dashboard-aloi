# app/pages/utils/plotting.py
import pandas as pd

def tidy_series(rows, cols, index=0, value=1):
    """Convierte filas [(date, score, ...)] a DataFrame time-series."""
    df = pd.DataFrame(rows, columns=cols)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df
