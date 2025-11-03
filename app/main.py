import streamlit as st
from pages.utils.db import init_db

st.set_page_config(
    page_title="Bienestar Diario - Cansadómetro & Motivómetro",
    layout="centered",
)

init_db()

st.title("🌞 Panel de Bienestar Diario")
st.markdown(
    "Registra tu nivel de **cansancio** y **motivación** para hacer un seguimiento de tu energía y bienestar."
)

st.sidebar.success("Selecciona una pestaña arriba para comenzar.")