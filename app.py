import streamlit as st
import os
import json
from google import genai

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# Stili CSS per la stampa pulita (Nasconde la barra laterale e i pulsanti quando stampi)
st.markdown("""
    <style>
    @media print {
        header, [data-testid="stSidebar"], .stButton, [data-testid="stHeader"], button {
            display: none !important;
            visibility: hidden;
        }
        .main .block-container {
            padding-top: 0px;
            padding-bottom: 0px;
        }
        /* Classe per forzare l'interruzione di pagina nella stampa */
        .salto-pagina {
            page-break-before: always;
            break-before: page;
            margin-top: 50px;
            border-top: 2px dashed #333;
            padding-top: 20px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# CONFIGURAZIONE CLIENT (Ufficiale Google GenAI SDK)
# ==========================================================
if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Configurazione incompleta: Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

# Inizializzazione stabile con l'SDK nativo di Google
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

# ==========================================================
# GESTIONE ACCOUNT MULTIPLI TRAMITE SECRETS
# ==========================================================
UTENTI_DEFAULT = {
    "admin@educorrect.it": "AdminPass2026",
    "prof.test@scuola.it": "TestScuola99"
}

UTENTI_ATTIVI = UTENTI_DEFAULT
if "UTENTI_ABILITATI" in st.secrets:
    try:
        UTENTI_ATTIVI = json.loads(st.secrets["UTENTI_ABILITATI"])
    except Exception:
        UTENTI_ATTIVI = UTENTI_DEFAULT

# Controllo dello stato di autenticazione dell'utente
if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state:
    st.session_state["utente_connesso"] = ""

# SCHERMATA DI LOGIN
if not st.session_state["autenticato"]:
    st.title("🔒 Area Riservata Docenti - EduCorrect")
    st.write("Inserisci le tue credenziali personali per accedere al pannello software.")
    
    email_inserita = st.text_input("Inserisci la tua Email:", placeholder="nome.cognome@scuola.it")
    password_inserita = st.text_input("Inserisci la tua Password:", type="password")
    
    if st.button("Accedi al Sistema"):
        if email_inserita in UTENTI_ATTIVI and password_inserita == UTENTI_ATTIVI[email_inserita]:
            st.session_state["autenticato"] = True
            st.session_state["utente_connesso"] = email_inserita
            st.success("Accesso eseguito con successo!")
            st.rerun()
        else:
            st.error("❌ Credenziali errate. Riprova o contatta l'amministratore del sito.")
            
    st.stop()

# ==========================================================
# INTERFACCIA PRINCIPALE (UTENTE LOGGATO)
# ==========================================================
st.title("📝 EduCorrect: Crea e Correggi Verifiche con l'IA")
st.sidebar.write(f"👤 Connesso come: **{st.session_state['utente_connesso']}**")

if st.sidebar.button("Disconnetti / Esci"):
    st.session_state["autenticato"] = False
    st.session_state["utente_connesso"] = ""
    if "testo_verifica" in st.session_state:
        del st.session_state["testo_verifica"]
    if "testo_correzione" in st.session_state:
        del st.session_state["testo_correzione"]
    st.rerun()

tab1, tab2 = st.tabs(["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

# --- SCHEDA 1: GENERATORE DI VERIFICHE ---
with tab1:
    st.header("Generatore di Compiti in Classe")
    col1, col2 = st.columns(2)
    with col1:
        argomento = st.text_input("Inserisci l'argomento della verifica:", placeholder="Es. I vulcani, La prima guerra mondiale...")
    with col2:
        stile_domande = st.selectbox("Tipo di domande:", ["Domande miste (Vero/Falso, Crocette, Aperte)", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    
    numero_domande = st.slider("Numero di domande totali:", min_value=1, max_value=20, value=5)
    
    if st.button("Genera Testo Verifica"):
        if not argomento:
            st.error("Scrivi un argomento prima di generare!")
        else:
            with st.spinner("L'intelligenza artificiale sta scrivendo il compito in italiano..."):
                prompt_sistema = "Sei un assistente didattico per professori italiani. Genera la verifica e le risposte SOLO IN ITALIANO. Inserisci OBBLIGATORIAMNETE il tag [SOLUZIONI] subito prima di scrivere le risposte corrette o i criteri di valutazione."
                
                if stile_domande == "Domande miste (Vero/Falso, Crocette, Aperte)":
                    dettaglio_stile = "strutturata con un mix bilanciato di domande a scelta multipla, quesiti Vero o Falso e domande a risposta aperta."
                else:
                    dettaglio_stile = f"composta esclusivamente da domande di tipo: {stile_domande}."

                prompt_utente = f"Crea una verifica superiore su: {argomento}. Struttura: {dettaglio_stile}. Numero quesiti: {numero_domande}. Includi soluzioni in fondo anticipate dal tag richiesto."
                
                try:
                    # Chiamata nativa SDK Google senza rischi di 404
                    risposta = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_utente,
                        config={
                            'system_instruction': prompt_sistema,
                            'temperature': 0.7
                        }
                    )
                    
                    st.session_state["testo_verifica"] = risposta.text
                    st.success("Operazione completata con Gemini!")
                
                except Exception as e:
                    st.error(f"⚠️ Errore durante la generazione con Gemini: {e}")

    if "testo_verifica" in st.session_state:
        st.subheader("Anteprima della Verifica")
        testo_html = st.session_state['testo_verifica'].replace('\n', '<br>')
        blocco_salto_pagina = "<div class='salto-pagina'><h3>🔑 Soluzioni e Criteri di Valutazione (Foglio Docente)</h3></div>"
        testo_elaborato = testo_html.replace("[SOLUZIONI]", blocco_salto_pagina).replace("### Soluzioni", "").replace("## Soluzioni", "")
        
        intestazione_studente = """
        <div style='border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 20px; font-family: sans-serif; color: #111111;'>
            <table style='width: 100%; border: none;'>
                <tr>
                    <td style='width: 50%; font-weight: bold;'>Istituto Scolastico: ____________________</td>
                    <td style='width: 50%; font-weight: bold; text-align: right;'>Data: ____/____/________</td>
                </tr>
                <tr>
                    <td style='padding-top: 10px;'>Alunno/a: ______________________________</td>
                    <td style='padding-top: 10px; text-align: right;'>Classe: ________________</td>
                </tr>
            </table>
        </div>
        """
        
        st.markdown(intestazione_studente + testo_elaborato, unsafe_allow_html=True)

# --- SCHEDA 2: SCANSIONA E CORREGGI ---
with tab2:
    st.header("Correttore di Compiti")
    st.write("Qui puoi implementare la logica per correggere i testi dei tuoi studenti.")
