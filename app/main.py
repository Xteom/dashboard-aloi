# app/main.py
import streamlit as st
from pages.utils.db import init_db

st.set_page_config(page_title="Wellness Dashboard", page_icon="💤", layout="wide")
init_db()

st.title("Wellness Dashboard")
st.markdown(
    "Usa la barra lateral izquierda para ir a **Bienestar**. "
    "Esta app guarda datos localmente en `app/data/cansadometro.db`."
)
