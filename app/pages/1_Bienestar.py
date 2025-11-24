# app/pages/1_Bienestar.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta

from pages.utils.metrics import cansadometro_score, motivometro
from pages.utils.db import (
    init_db, upsert_fatigue, upsert_motivation,
    fetch_fatigue_history, fetch_motivation_history, fetch_export_df,
    fetch_latest_fatigue, fetch_latest_motivation
)
from pages.utils.plotting import tidy_series

st.set_page_config(page_title="Bienestar", page_icon="🧠", layout="wide")

HELP_FATIGUE = {
    "D":  "Deuda de sueño (de tu app). 0–3.5: súper bien; 6–10: cansado; >10: muy cansado. Sin tope superior.",
    "QS": "Calidad de sueño anoche (duración, eficiencia, regularidad, despertares). 0 = pésima, 10 = excelente.",
    "AM": "Agotamiento mental/estrés/carga cognitiva. 0 = colapsado, 10 = sin agotamiento.",
    "S":  "Salud general y síntomas. 0 = muy enfermo, 10 = sano.",
    "AF": "Agotamiento físico. 0 = extenuado/dolor fuerte, 10 = descanso total.",
    "A":  "Peso de acumulado: qué tanto sientes que la deuda te pega hoy. 0 = nada, 10 = muchísimo."
}

HELP_MOTIV = {
    "EB":  "Energía base. 0 = sin energía, 10 = lleno de energía.",
    "AUT": "Autonomía/control sobre la tarea. 0 = sin control, 10 = control total.",
    "EMO": "Emociones inspiradoras (ánimo, entusiasmo, curiosidad). 0 = nulas, 10 = muy altas.",
    "CLA": "Claridad de metas/pasos. 0 = confuso, 10 = cristalino.",
    "REL": "Relevancia personal/profesional de la tarea. 0 = irrelevante, 10 = muy relevante.",
    "APO": "Apoyo social/feedback disponible. 0 = sin apoyo, 10 = soporte fuerte y oportuno.",
    "REC": "Reconocimiento/recompensa esperada. 0 = nada, 10 = alta y cercana.",
    "VAL": "Alineación con valores personales. 0 = no alinea, 10 = totalmente alineada.",
    "PRO": "Conexión con propósito/misión personal. 0 = nada, 10 = totalmente conectada."
}


init_db()

st.title("Bienestar")
today = date.today()
yesterday = today - timedelta(days=1)

# ------------- Captura Cansadómetro -------------
st.subheader("Cansadómetro")
# Load last entered values
last_fatigue = fetch_latest_fatigue()
default_D = last_fatigue["D"] if last_fatigue else 10.0
default_QS = last_fatigue["QS"] if last_fatigue else 10.0
default_AM = last_fatigue["AM"] if last_fatigue else 10.0
default_S = last_fatigue["S"] if last_fatigue else 10.0
default_AF = last_fatigue["AF"] if last_fatigue else 10.0
default_A = last_fatigue["A"] if last_fatigue else 10.0

with st.form("cansado_form", clear_on_submit=False):
    c_date = st.date_input("Fecha", value=today, help="Puedes registrar días pasados.")
    col1, col2, col3 = st.columns(3)
    with col1:
        D  = st.number_input("Deuda de sueño (puede >10)", min_value=0.0, step=0.1, value=default_D,
                             help=HELP_FATIGUE["D"])
        QS = st.slider("Calidad de sueño (QS)", 0.0, 10.0, default_QS, 0.5,
                       help=HELP_FATIGUE["QS"])
    with col2:
        AM = st.slider("Agotamiento mental (AM)", 0.0, 10.0, default_AM, 0.5,
                       help=HELP_FATIGUE["AM"])
        S  = st.slider("Salud (S)", 0.0, 10.0, default_S, 0.5,
                       help=HELP_FATIGUE["S"])
    with col3:
        AF = st.slider("Agotamiento físico (AF)", 0.0, 10.0, default_AF, 0.5,
                       help=HELP_FATIGUE["AF"])
        A  = st.slider("Peso de acumulado (A)", 0.0, 10.0, default_A, 0.5,
                       help=HELP_FATIGUE["A"])

    submitted = st.form_submit_button("Guardar Cansadómetro")
    if submitted:
        res = cansadometro_score(D, QS, AM, S, AF, A)
        payload = {"D":D,"QS":QS,"AM":AM,"S":S,"AF":AF,"A":A,"score":res["score"]}
        upsert_fatigue(c_date.isoformat(), payload)
        st.success(f"Guardado. Score Cansadómetro: **{res['score']:.2f} / 10**")

# ------------- Captura Motivómetro -------------
st.subheader("Motivómetro")
# Load last entered values
last_motivation = fetch_latest_motivation()
default_EB = last_motivation["EB"] if last_motivation else 7.0
default_AUT = last_motivation["AUT"] if last_motivation else 8.0
default_EMO = last_motivation["EMO"] if last_motivation else 6.0
default_CLA = last_motivation["CLA"] if last_motivation else 8.0
default_REL = last_motivation["REL"] if last_motivation else 8.0
default_APO = last_motivation["APO"] if last_motivation else 7.0
default_REC = last_motivation["REC"] if last_motivation else 6.0
default_VAL = last_motivation["VAL"] if last_motivation else 9.0
default_PRO = last_motivation["PRO"] if last_motivation else 8.0

with st.form("motivo_form", clear_on_submit=False):
    m_date = st.date_input("Fecha", value=today, key="m_date")
    co1, co2, co3 = st.columns(3)
    with co1:
        EB  = st.slider("Energía base (EB)", 0.0, 10.0, default_EB, 0.5,
                        help=HELP_MOTIV["EB"])
        AUT = st.slider("Autonomía (AUT)", 0.0, 10.0, default_AUT, 0.5,
                        help=HELP_MOTIV["AUT"])
        EMO = st.slider("Emociones (+) (EMO)", 0.0, 10.0, default_EMO, 0.5,
                        help=HELP_MOTIV["EMO"])
    with co2:
        CLA = st.slider("Claridad (CLA)", 0.0, 10.0, default_CLA, 0.5,
                        help=HELP_MOTIV["CLA"])
        REL = st.slider("Relevancia (REL)", 0.0, 10.0, default_REL, 0.5,
                        help=HELP_MOTIV["REL"])
        APO = st.slider("Apoyo (APO)", 0.0, 10.0, default_APO, 0.5,
                        help=HELP_MOTIV["APO"])
    with co3:
        REC = st.slider("Reconocimiento (REC)", 0.0, 10.0, default_REC, 0.5,
                        help=HELP_MOTIV["REC"])
        VAL = st.slider("Valores (VAL)", 0.0, 10.0, default_VAL, 0.5,
                        help=HELP_MOTIV["VAL"])
        PRO = st.slider("Propósito (PRO)", 0.0, 10.0, default_PRO, 0.5,
                        help=HELP_MOTIV["PRO"])


    submit_m = st.form_submit_button("Guardar Motivómetro")
    if submit_m:
        score = motivometro(EB,AUT,EMO,CLA,REL,APO,REC,VAL,PRO)
        payload = {"EB":EB,"AUT":AUT,"EMO":EMO,"CLA":CLA,"REL":REL,"APO":APO,"REC":REC,"VAL":VAL,"PRO":PRO,"score":score}
        upsert_motivation(m_date.isoformat(), payload)
        st.success(f"Guardado. Score Motivación: **{score:.2f} / 10**")

st.divider()

# ------------- Resumen del día previo -------------
colA, colB = st.columns(2)
with colA:
    st.markdown(f"### Ayer ({yesterday.isoformat()}) — Cansadómetro")
    rows_f = fetch_fatigue_history(limit=None)
    df_f = tidy_series(
        rows_f,
        ["date","score","D","QS","AM","S","AF","A"]
    )
    if not df_f.empty and (df_f["date"] == pd.to_datetime(yesterday)).any():
        y_row = df_f[df_f["date"] == pd.to_datetime(yesterday)].iloc[-1]
        st.metric("Score", f"{y_row['score']:.2f}")
        st.caption(f"D={y_row['D']}, QS={y_row['QS']}, AM={y_row['AM']}, S={y_row['S']}, AF={y_row['AF']}, A={y_row['A']}")
    else:
        st.info("Sin registro de ayer.")

with colB:
    st.markdown(f"### Ayer ({yesterday.isoformat()}) — Motivómetro")
    rows_m = fetch_motivation_history(limit=None)
    df_m = tidy_series(
        rows_m,
        ["date","score","EB","AUT","EMO","CLA","REL","APO","REC","VAL","PRO"]
    )
    if not df_m.empty and (df_m["date"] == pd.to_datetime(yesterday)).any():
        y_row = df_m[df_m["date"] == pd.to_datetime(yesterday)].iloc[-1]
        st.metric("Score", f"{y_row['score']:.2f}")
        st.caption(
            f"EB={y_row['EB']}, AUT={y_row['AUT']}, EMO={y_row['EMO']}, "
            f"CLA={y_row['CLA']}, REL={y_row['REL']}, APO={y_row['APO']}, "
            f"REC={y_row['REC']}, VAL={y_row['VAL']}, PRO={y_row['PRO']}"
        )
    else:
        st.info("Sin registro de ayer.")

st.divider()

# ------------- Gráficas simples (últimos 60 días) -------------
left, right = st.columns(2)
with left:
    st.markdown("#### Histórico Cansadómetro (score)")
    if not df_f.empty:
        st.line_chart(df_f.set_index("date")[["score"]])
    else:
        st.info("Aún no hay datos de Cansadómetro.")

with right:
    st.markdown("#### Histórico Motivómetro (score)")
    if not df_m.empty:
        st.line_chart(df_m.set_index("date")[["score"]])
    else:
        st.info("Aún no hay datos de Motivómetro.")

# ------------- Export CSV -------------
st.subheader("Exportar datos")
exp_df = fetch_export_df()
csv = exp_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Descargar CSV histórico",
    data=csv,
    file_name="bienestar_historico.csv",
    mime="text/csv"
)
st.dataframe(exp_df, use_container_width=True)
