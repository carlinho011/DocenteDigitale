import streamlit as st
import os, time, pandas as pd, re
from fpdf import FPDF
try: import pypdf
except ImportError: pypdf = None

# --- CONFIG E CSS ---
st.set_page_config(page_title="EduCorrect Pro", layout="wide")
st.markdown("<style>.box-login {background: rgba(30, 41, 59, 0.7); padding: 25px; border-radius: 12px;}</style>", unsafe_allow_html=True)

# --- MOTORE PDF ---
class PDF(FPDF):
    def safe(self, t): return t.encode('latin-1', 'replace').decode('latin-1')
    def scrivi(self, testo, dim=11):
        for riga in testo.split('\n'):
            parti = riga.replace('**', '§').split('§')
            self.set_font("Times", "", dim)
            for i, p in enumerate(parti):
                if i % 2: self.set_font("Times", "B", dim)
                self.write(6, self.safe(p))
                self.set_font("Times", "", dim)
            self.ln(6)

# --- LOGICA APP ---
if "registro" not in st.session_state: st.session_state.registro = []

st.sidebar.title("EduCorrect AI")
modalita = st.sidebar.radio("Funzioni", ["Genera Verifica", "Correggi Compito"])

if modalita == "Correggi Compito":
    file = st.file_uploader("Carica File", type=["pdf", "jpg", "png"])
    if file and st.button("Analizza"):
        # Qui andrebbe la chiamata all'API Gemini
        st.session_state.registro.append({"Studente": "Alunno", "Voto": 6, "Data": time.strftime('%d/%m/%y')})
        st.success("Correzione salvata!")

if st.session_state.registro:
    st.sidebar.table(pd.DataFrame(st.session_state.registro))
