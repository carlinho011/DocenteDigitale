import streamlit as st
import os
import json
from fpdf import FPDF

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# STILE GRAFICO APPLICATO ALL'INTERA APPLICAZIONE (Anteprima a schermo stile foglio A4)
st.markdown("""
    <style>
    .foglio-word {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 50px 60px !important;
        margin: 20px auto !important;
        max-width: 800px !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.15) !important;
        border: 1px solid #d3d3d3 !important;
        font-family: 'Times New Roman', Times, serif !important;
        line-height: 1.6 !important;
        font-size: 16px !important;
    }
    .tabella-intestazione {
        width: 100% !important;
        border-collapse: collapse !important;
        border-bottom: 2px solid #000000 !important;
        margin-bottom: 25px !important;
        font-family: Arial, sans-serif !important;
        font-size: 14px !important;
        color: #000000 !important;
    }
    .tabella-intestazione td {
        border: none !important;
        padding: 6px 0 !important;
    }
    .salto-pagina {
        page-break-before: always !important;
        break-before: page !important;
        margin-top: 50px !important;
        border-top: 2px dashed #000000 !important;
        padding-top: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# CLASSE PER LA GENERAZIONE DEL FILE PDF COMPATIBILE
# ==========================================================
class PDFVerifica(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 9)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

def genera_file_pdf(argomento, difficolta, testo_compito, testo_soluzioni=None):
    pdf = PDFVerifica()
    pdf.add_page()
    
    # Intestazione formale scolastica nel PDF
    pdf.set_font("Arial", "B", 11)
    pdf.cell(110, 6, "Istituto d'Istruzione Superiore", 0, 0, "L")
    pdf.cell(80, 6, "Data: ____/____/________", 0, 1, "R")
    pdf.cell(110, 6, "Alunno/a: _____________________________________", 0, 0, "L")
    pdf.cell(80, 6, "Classe: ____________  Sez. ____", 0, 1, "R")
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(110, 6, f"Materia: Verifica scritta di approfondimento ({difficolta.capitalize()})", 0, 0, "L")
    pdf.cell(80, 6, f"Oggetto: {argomento.capitalize()}", 0, 1, "R")
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    # Corpo del compito
    pdf.set_font("Times", "", 11)
    testo_compito_codificato = testo_compito.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, testo_compito_codificato)
    
    # Sezione soluzioni
    if testo_soluzioni:
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "CHIAVE DI CORREZIONE (FOGLIO DOCENTE)", "B", 1, "L")
        pdf.ln(6)
        pdf.set_font("Times", "", 11)
        testo_soluzioni_codificato = testo_soluzioni.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, testo_soluzioni_codificato)
        
    return pdf.output()

# ==========================================================
# CONFIGURAZIONE CLIENT (Doppio supporto SDK Google)
# ==========================================================
if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Configurazione incompleta: Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
    usa_sdk_nuovo = True
except ImportError:
    import google.generativeai as dg_genai
    dg_genai.configure(api_key=st.secrets["GEMINI_KEY"])
    usa_sdk_nuovo = False

# ==========================================================
# GESTIONE ACCOUNT (LOGIN)
# ==========================================================
UTENTI_DEFAULT = {"admin@educorrect.it": "AdminPass2026", "prof.test@scuola.it": "TestScuola99"}
UTENTI_ATTIVI = UTENTI_DEFAULT
if "UTENTI_ABILITATI" in st.secrets:
    try:
        UTENTI_ATTIVI = json.loads(st.secrets["UTENTI_ABILITATI"])
    except Exception:
        UTENTI_ATTIVI = UTENTI_DEFAULT

if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state:
    st.session_state["utente_connesso"] = ""

if not st.session_state["autenticato"]:
    st.title("🔒 Area Riservata Docenti - EduCorrect")
    email_inserita = st.text_input("Inserisci la tua Email:")
    password_inserita = st.text_input("Inserisci la tua Password:", type="password")
    if st.button("Accedi al Sistema"):
        if email_inserita in UTENTI_ATTIVI and password_inserita == UTENTI_ATTIVI[email_inserita]:
            st.session_state["autenticato"] = True
            st.session_state["utente_connesso"] = email_inserita
            st.rerun()
        else:
            st.error("❌ Credenziali errate.")
    st.stop()

# ==========================================================
# INTERFACCIA PRINCIPALE
# ==========================================================
st.title("📝 EduCorrect: Crea e Correggi Verifiche con l'IA")
st.sidebar.write(f"👤 Connesso come: **{st.session_state['utente_connesso']}**")

if st.sidebar.button("Disconnetti / Esci"):
    st.session_state["autenticato"] = False
    st.session_state["utente_connesso"] = ""
    if "testo_verifica" in st.session_state:
        del st.session_state["testo_verifica"]
    if "analisi_correzione" in st.session_state:
        del st.session_state["analisi_correzione"]
    st.rerun()

tab1, tab2 = st.tabs(["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

# --- SCHEDA 1: GENERATORE DI VERIFICHE ---
with tab1:
    st.header("Generatore di Compiti in Classe (Livello Scuole Superiori)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        argomento = st.text_input("Inserisci l'argomento della verifica:", placeholder="Es. I vulcani...")
    with col2:
        stile_domande = st.selectbox("Tipo di domande:", ["Domande miste (Vero/Falso, Crocette, Aperte)", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3:
        difficolta = st.selectbox("Livello di difficoltà:", ["facile", "media", "difficile"])
    
    numero_domande = st.slider("Numero di domande totali:", min_value=1, max_value=20, value=5)
    
    if st.button("Genera Testo Verifica"):
        if not argomento:
            st.error("Scrivi un argomento prima di generare!")
        else:
            with st.spinner("L'intelligenza artificiale sta scrivendo il compito per le superiori..."):
                prompt_sistema = (
                    "Sei un assistente didattico esperto per i licei e gli istituti tecnici italiani (Scuola Superiore). "
                    "Genera la verifica e le relative risposte esclusivamente in lingua italiana. "
                    f"Il livello di complessità generale deve essere tassativamente calibrato come '{difficolta}' per gli standard delle scuole superiori. "
                    "Formatta l'intero output in testo chiaro (Markdown di base). "
                    "Inserisci obbligatoriamente il tag specifico [SOLUZIONI] subito prima di iniziare a scrivere le chiavi di correzione o le risposte corrette."
                )
                prompt_utente = f"Crea una verifica superiore di livello '{difficolta}' su '{argomento}'. Tipo domande: {stile_domande}. Numero quesiti: {numero_domande}. Includi le soluzioni in fondo precedute dal tag richiesto."
                
                try:
                    if usa_sdk_nuovo:
                        risposta = client.models.generate_content(
                            model='gemini-2.5-flash', contents=prompt_utente,
                            config={'system_instruction': prompt_sistema, 'temperature': 0.6}
                        )
                        testo_generato = risposta.text
                    else:
                        model = dg_genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=prompt_sistema)
                        risposta = model.generate_content(prompt_utente)
                        testo_generato = risposta.text
                    
                    st.session_state["testo_verifica"] = testo_generato
                    st.success(f"Verifica (Difficoltà: {difficolta.upper()}) generata con successo!")
                except Exception as e:
                    st.error(f"⚠️ Errore: {e}")

    if "testo_verifica" in st.session_state:
        testo_grezzo = st.session_state['testo_verifica']
        st.write("### 📄 Esporta e Visualizza")

        if "[SOLUZIONI]" in testo_grezzo:
            parti_testo = testo_grezzo.split("[SOLUZIONI]")
            compito_testo_puro = parti_testo[0].strip()
            soluzioni_testo_puro = parti_testo[1].strip()
        else:
            compito_testo_puro = testo_grezzo.strip()
            soluzioni_testo_puro = None

        try:
            pdf_raw = genera_file_pdf(argomento, difficolta, compito_testo_puro, soluzioni_testo_puro)
            pdf_bytes = bytes(pdf_raw)
            st.download_button(
                label="📥 Scarica Verifica in formato PDF (Pronta da stampare)",
                data=pdf_bytes, file_name=f"verifica_{difficolta}_{argomento.lower().replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as pdf_err:
            st.error(f"⚠️ Impossibile generare il PDF: {pdf_err}")

        testo_html = testo_grezzo.replace('\n', '<br>')
