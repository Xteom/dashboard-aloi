import streamlit as st
from pages.utils.metrics import score_fatigue, motivometro
from pages.utils.db import insert_score, get_scores
from pages.utils.plotting import plot_metric

st.title("🌙 Cansadómetro & 💡 Motivómetro")

st.header("🌙 Cansadómetro")

with st.form("cansado_form"):
    col1, col2 = st.columns(2)
    with col1:
        D = st.slider("Deuda de sueño (D)", 0.0, 15.0, 5.0)
        QS = st.slider("Calidad de sueño (QS)", 0.0, 10.0, 7.0)
        AM = st.slider("Carga mental (AM)", 0.0, 10.0, 6.0)
    with col2:
        S = st.slider("Estrés (S)", 0.0, 10.0, 7.0)
        AF = st.slider("Actividad física (AF)", 0.0, 10.0, 7.0)
        A = st.slider("Ánimo general (A)", 0.0, 10.0, 6.0)
    submitted_cansado = st.form_submit_button("Guardar Cansadómetro")

if submitted_cansado:
    score = score_fatigue(D, QS, AM, S, AF, A)
    st.success(f"Tu puntaje de cansancio es: **{score:.2f}/10**")
    insert_score("cansadometro", score)

data_cansado = get_scores("cansadometro")
plot_metric(data_cansado, "Cansadómetro")

# ----------------------------
st.header("💡 Motivómetro")

with st.form("motivometro_form"):
    col1, col2 = st.columns(2)
    with col1:
        EB = st.slider("Energía base", 0.0, 10.0, 7.0)
        AUT = st.slider("Autonomía", 0.0, 10.0, 7.0)
        EMO = st.slider("Emociones positivas", 0.0, 10.0, 7.0)
        CLA = st.slider("Claridad de metas", 0.0, 10.0, 7.0)
        REL = st.slider("Relevancia de la tarea", 0.0, 10.0, 7.0)
    with col2:
        APO = st.slider("Apoyo social", 0.0, 10.0, 7.0)
        REC = st.slider("Reconocimiento", 0.0, 10.0, 7.0)
        VAL = st.slider("Alineación con valores", 0.0, 10.0, 7.0)
        PRO = st.slider("Propósito", 0.0, 10.0, 7.0)
    submitted_motivo = st.form_submit_button("Guardar Motivómetro")

if submitted_motivo:
    score = motivometro(EB, AUT, EMO, CLA, REL, APO, REC, VAL, PRO)
    st.success(f"Tu motivación es: **{score:.2f}/10**")
    insert_score("motivometro", score)

data_motivo = get_scores("motivometro")
plot_metric(data_motivo, "Motivómetro")