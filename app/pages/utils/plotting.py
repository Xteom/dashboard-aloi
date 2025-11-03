import matplotlib.pyplot as plt
import streamlit as st

def plot_metric(df, metric_name):
    if df.empty:
        st.info("No hay datos aún para este indicador.")
        return
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["score"], marker="o")
    ax.set_title(f"Evolución de {metric_name}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Puntaje")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)