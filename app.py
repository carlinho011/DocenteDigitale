import streamlit as st
import os
import re
import time
import pandas as pd
from fpdf import FPDF
try:
    import pypdf
except ImportError:
    pypdf = None

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect Professional", page_icon="📝", layout="wide")

# --- STATO SESSIONE ---
if "tema_scelto" not in st.session_state: st.session_state["tema_scelto"] = "Total Dark"
if "registro_voti" not in st.session_state: st.session_state["registro_voti"] = []
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# --- FUNZIONI DI SUPPORTO (CSS E UI) ---
def disabilita_cronologia():
    st.markdown("""
        <script>
            const inputs = parent.document.querySelectorAll('input');
            inputs.forEach(input => {
                input.setAttribute('autocomplete', 'off');
                input.setAttribute('autocorrect', 'off');
                input.setAttribute('autocapitalize', 'off');
                input.setAttribute('spellcheck', 'false');
            });
        </script>
    """, unsafe_allow_html=True)

def carica_css():
    st.markdown("""
    <style>
        .box-login { background: rgba(30, 41, 59, 0.7); padding: 25px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .foglio-word { background: white; color: #1e293b; padding: 40px; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); max-width: 800px; margin: 20px auto; font-family: 'Times New Roman', serif; }
        .tabella-intestazione { width: 100%; border-bottom: 2px solid #0f172a; margin-bottom: 20px; }
        .box-info { background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 12px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

carica_css()

# --- MOTORE PDF AVANZATO (FPDF2) ---
class PDF_Pro(FPDF):
    def safe(self, text): 
        return text.encode('latin-1', 'replace').decode('latin-1')
    
    def scrivi_formattato(self, testo, dimensione):
        for riga in testo.split('\n'):
            riga = riga.replace('**', '§')
            parti = riga.split('§')
            self.set_font("Times", "", dimensione)
            for i, parte in enumerate(parti):
                if i % 2 == 1: self.set_font("Times", "B", dimensione)
                self.write(6, self.safe(parte))
                self.set_font("Times", "", dimensione)
            self.ln(6)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, self.safe("EduCorrect AI - Verbale di Valutazione"), 0, 1, "C")
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

# --- LOGICA API ---
try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets.get("GEMINI_KEY"))
except Exception:
    client = None

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

# --- SIDEBAR E NAVIGAZIONE ---
st.sidebar.title(f"Prof. {st.session_state.get('nome_docente', '')}")
modalita = st.sidebar.radio("Funzioni", ["Genera Verifica", "Correggi Compito"])

# --- FUNZIONALITÀ ---
if modalita == "Genera Verifica":
    st.title("🚀 Generatore Verifiche")
    arg = st.text_input("Argomento:")
    if st.button("Genera"):
        st.session_state["testo_verifica"] = "Esempio di verifica generata..."
        st.success("Generazione completata!")

elif modalita == "Correggi Compito":
    st.title("🔍 Analisi Elaborati")
    file = st.file_uploader("Carica File", type=["pdf", "jpg", "png"])
    if file and st.button("🚀 Correggi ed Analizza"):
        with st.spinner("L'AI sta analizzando..."):
            # Simulazione logica di analisi
            st.session_state["registro_voti"].append({
                "Studente": "Alunno Test", 
                "Voto": 6, 
                "Data": time.strftime('%d/%m/%y')
            })
            st.success("Correzione salvata nel registro!")

# --- REGISTRO VOTI NELLA SIDEBAR ---
if st.session_state["registro_voti"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Registro Classe")
    df = pd.DataFrame(st.session_state["registro_voti"])
    st.sidebar.table(df)
    st.sidebar.download_button("📥 Scarica Registro CSV", df.to_csv(index=False), "registro.csv")

disabilita_cronologia()
