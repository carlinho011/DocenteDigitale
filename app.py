import streamlit as st
import os
import io
import google.generativeai as genai
from reportlab.pdfgen import canvas

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# Configurazione API con la libreria classica
genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

def chiama_gemini(prompt, file_data=None, mime_type=None):
    if file_data and mime_type:
        # Caricamento file tramite il sistema File API classico
        file_io = io.BytesIO(file_data)
        # Nota: per file piccoli, passiamo il contenuto direttamente
        response = model.generate_content([prompt, {"mime_type": mime_type, "data": file_data}])
    else:
        response = model.generate_content(prompt)
    return response.text

# --- LOGIN E UI ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    st.title("Area Riservata Docente")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome:
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else: st.error("Password errata.")
    st.stop()

# --- INTERFACCIA ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    if st.button("Genera"):
        with st.spinner("Generazione..."):
            res = chiama_gemini(f"Crea una verifica di {materia} su {argomento}.")
            st.markdown(res)

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica File", type=["jpg", "png", "pdf"])
    if file and st.button("Analizza"):
        with st.spinner("Analisi..."):
            mime = "image/jpeg" if file.type != "application/pdf" else "application/pdf"
            res = chiama_gemini("Correggi questo compito.", file.getvalue(), mime)
            st.markdown(res)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
