import streamlit as st
import os
import re
import time
import io
# Assicurati di avere queste librerie installate: pip install streamlit reportlab pypdf google-genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="wide")

# --- AUTENTICAZIONE (Semplificata per brevità) ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    st.title("🔒 Accesso Docenti")
    nome = st.text_input("Nome e Cognome")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == st.secrets.get("PASSWORD_DOCENTI", "ScuolaDigitale2026!"):
            st.session_state["autenticato"] = True
            st.session_state["nome_docente"] = nome
            st.rerun()
        else:
            st.error("Credenziali non valide")
    st.stop()

# --- BARRA LATERALE (SOLO NAVIGAZIONE) ---
with st.sidebar:
    st.markdown("## 📝 EduCorrect AI")
    st.write(f"Docente: **{st.session_state.get('nome_docente', 'Prof')}**")
    st.markdown("---")
    menu = st.radio("SEZIONI OPERATIVE:", ["🚀 Generatore Verifiche", "🔍 Scanner Correzioni"])
    st.markdown("---")
    if st.button("🚪 Esci"):
        st.session_state.clear()
        st.rerun()

# --- LOGICA APPLICATIVA ---

if menu == "🚀 Generatore Verifiche":
    st.title("🚀 Generatore di Verifiche")
    st.markdown("### Configurazione Verifica")
    
    # Parametri nel corpo centrale
    col1, col2 = st.columns(2)
    with col1:
        argomento = st.text_input("Argomento Didattico:", placeholder="Es. Rivoluzione Francese")
        tipologia = st.selectbox("Tipologia Quesiti:", ["Risposte aperte", "Scelta multipla", "Vero/Falso"])
    with col2:
        difficolta = st.select_slider("Livello di Difficoltà:", ["Facile", "Media", "Difficile"])
        numero = st.slider("Numero di domande:", 1, 20, 5)
    
    if st.button("🪄 Genera Verifica", type="primary"):
        st.info(f"Elaborazione in corso: {argomento} ({tipologia})...")
        # Inserisci qui la logica di generazione con Gemini SDK

elif menu == "🔍 Scanner Correzioni":
    st.title("🔍 Assistente AI alla Correzione")
    
    # Metodo nel corpo centrale
    metodo = st.radio("Scegli la modalità di acquisizione:", ["📁 Carica File (PDF/Immagini)", "📸 Scatta con Fotocamera"], horizontal=True)
    
    if metodo == "📁 Carica File (PDF/Immagini)":
        file_input = st.file_uploader("Carica l'elaborato:", type=["pdf", "jpg", "png"])
    else:
        file_input = st.camera_input("Inquadra il compito:")
        
    if st.button("🚀 Avvia Correzione AI", type="primary"):
        if file_input:
            st.success("Analisi dell'elaborato in corso...")
            # Inserisci qui la logica di analisi con Gemini Vision/Text
        else:
            st.warning("Per favore, carica un documento o scatta una foto prima di procedere.")

# --- CSS GLOBALE (Da inserire nel file stile.css o tramite st.markdown) ---
st.markdown("""
    <style>
    /* Personalizzazione estetica */
    .stApp { background-color: #f8fafc; }
    div[data-testid="stSidebar"] { background-color: #0b132b; color: white; }
    </style>
""", unsafe_allow_html=True)
