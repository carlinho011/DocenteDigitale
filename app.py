import streamlit as st
import os
import re
import time
import pandas as pd
from fpdf import FPDF

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect Pro", page_icon="📝", layout="wide")

# Inizializzazione Stato
if "tema_scelto" not in st.session_state: st.session_state["tema_scelto"] = "Total Dark"
if "registro_voti" not in st.session_state: st.session_state["registro_voti"] = []
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# --- CSS E STILE ---
def carica_stile():
    st.markdown("""
    <style>
        .box-login { background: rgba(30, 41, 59, 0.7); padding: 25px; border-radius: 12px; border: 1px solid #334155; }
        .foglio-word { background: white; color: #1e293b; padding: 40px; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); max-width: 800px; margin: 20px auto; font-family: 'Times New Roman', serif; }
        .tabella-intestazione { width: 100%; border-bottom: 2px solid #0f172a; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

carica_stile()

# --- MOTORE PDF AVANZATO (FPDF2) ---
class PDF_Pro(FPDF):
    def safe(self, text): 
        return text.encode('latin-1', 'replace').decode('latin-1')
    
    def scrivi_formattato(self, testo, dimensione):
        for riga in testo.split('\n'):
            riga = riga.replace('**', '§') # Parser grassetto
            parti = riga.split('§')
            self.set_font("Times", "", dimensione)
            for i, parte in enumerate(parti):
                if i % 2 == 1: self.set_font("Times", "B", dimensione)
                self.write(6, self.safe(parte))
                self.set_font("Times", "", dimensione)
            self.ln(6)

# --- LOGICA API GEMINI ---
from google import genai
from google.genai import types
client = genai.Client(api_key=st.secrets.get("GEMINI_KEY"))

# --- ACCESSO ---
if not st.session_state["autenticato"]:
    st.markdown("<div class='box-login'><h2>🔒 Accesso EduCorrect</h2></div>", unsafe_allow_html=True)
    nome = st.text_input("Nome Docente")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == st.secrets.get("PASSWORD_DOCENTI", "Mattei"):
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
    st.stop()

# --- INTERFACCIA E FUNZIONI ---
st.sidebar.title(f"Prof. {st.session_state.get('nome_docente', '')}")
modalita = st.sidebar.radio("Funzioni", ["Genera Verifica", "Correggi Compito"])

if modalita == "Correggi Compito":
    file = st.file_uploader("Carica File", type=["pdf", "jpg", "png"])
    if file and st.button("🚀 Correggi ed Analizza"):
        with st.spinner("Analisi in corso..."):
            # Prompt evoluto con Piano di Recupero
            sys_p = "Sei un professore severo ma giusto. Analizza il compito. Formato: STUDENTE: [Nome], TRACCIA RILEVATA: [Traccia], VOTO FINALE: [Voto], PIANO DI RECUPERO: [3 argomenti da ripassare]."
            
            # Qui inseriresti la chiamata client.models.generate_content...
            
            # Salvataggio nel registro (esempio)
            st.session_state["registro_voti"].append({
                "Studente": "Alunno Test", 
                "Voto": 6, 
                "Data": time.strftime('%d/%m/%y')
            })
            st.success("Correzione salvata nel registro!")

# --- REGISTRO VOTI (SIDEBAR) ---
if st.session_state["registro_voti"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Registro Classe")
    df = pd.DataFrame(st.session_state["registro_voti"])
    st.sidebar.table(df)
    st.sidebar.download_button("📥 Scarica Registro CSV", df.to_csv(index=False), "registro.csv")
