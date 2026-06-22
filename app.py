import streamlit as st
import os
from google import genai

# Setup
st.set_page_config(page_title="EduCorrect", page_icon="📝")

# Caricamento CSS robusto
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sessione
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# Login
if not st.session_state["autenticato"]:
    st.title("Area Riservata 💜")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
    st.stop()

# App
st.sidebar.title(f"Benvenuto Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Funzioni", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    with st.form("form_viola"):
        materia = st.text_input("Materia")
        argomento = st.text_input("Argomento")
        num = st.slider("Numero domande", 1, 10, 5)
        if st.form_submit_button("Genera"):
            client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
            res = client.models.generate_content(model="gemini-2.0-flash", contents=f"Crea {num} domande su {materia}: {argomento}")
            st.markdown(res.text)
