import streamlit as st
import os
import re
import time
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Gestione librerie opzionali
try:
    import pypdf
except ImportError:
    pypdf = None

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="wide")

# Inizializzazione Session State
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "tema_scelto" not in st.session_state: st.session_state["tema_scelto"] = "Total Dark"

# --- AUTENTICAZIONE ---
if not st.session_state["autenticato"]:
    st.title("🔒 Accesso Docenti")
    nome = st.text_input("Nome Docente")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == st.secrets.get("PASSWORD_DOCENTI", "ScuolaDigitale2026!"):
            st.session_state["autenticato"] = True
            st.session_state["nome_docente"] = nome
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- IMPORTAZIONE SDK GEMINI (Dopo autenticazione) ---
from google import genai
from google.genai import types
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

# --- BARRA LATERALE (MENU) ---
st.sidebar.markdown(f"## 📝 EduCorrect AI")
st.sidebar.write(f"Docente: **{st.session_state.get('nome_docente', 'Prof')}**")

menu = st.sidebar.radio("NAVIGAZIONE", ["🚀 Generatore Verifiche", "🔍 Scanner Correzioni"])
st.sidebar.markdown("---")

# --- SEZIONE GENERATORE ---
if menu == "🚀 Generatore Verifiche":
    st.sidebar.subheader("⚙️ Impostazioni Generazione")
    arg = st.sidebar.text_input("Argomento")
    tipologia = st.sidebar.selectbox("Tipologia", ["Risposte aperte", "Scelta multipla"])
    diff = st.sidebar.select_slider("Difficoltà", ["Facile", "Media", "Difficile"])
    num = st.sidebar.slider("N. Domande", 1, 10, 5)
    
    st.title("🚀 Generatore Integrato di Verifiche")
    if st.button("Genera Verifica"):
        # Logica di chiamata a Gemini (omessa per brevità, usa il tuo codice precedente)
        st.write("Generazione in corso per:", arg)

# --- SEZIONE SCANNER ---
elif menu == "🔍 Scanner Correzioni":
    st.sidebar.subheader("⚙️ Metodo di Input")
    metodo = st.sidebar.radio("Sorgente:", ["📁 Carica File", "📸 Fotocamera"])
    
    st.title("🔍 Assistente AI alla Correzione")
    
    if metodo == "📁 Carica File":
        file = st.file_uploader("Carica PDF o Immagine", type=["pdf", "jpg", "png"])
    else:
        file = st.camera_input("Scatta foto")
        
    if st.button("Avvia Correzione"):
        if file:
            st.write("Analisi in corso...")
        else:
            st.warning("Carica prima un file!")

# --- FOOTER SIDEBAR ---
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Esci"):
    st.session_state.clear()
    st.rerun()
