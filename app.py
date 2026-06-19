import streamlit as st
import os
import json

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# STILE GRAFICO: Crea un vero foglio A4 bianco con ombreggiatura e gestisce la stampa pulita
st.markdown("""
    <style>
    /* Stile Simulazione Foglio Word A4 su Schermo */
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
    
    /* Intestazione del Compito tipo Scuola Superiore */
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
    
    /* Interruzione di pagina pulita per la stampa */
    .salto-pagina {
        page-break-before: always !important;
        break-before: page !important;
        margin-top: 50px !important;
        border-top: 2px dashed #000000 !important;
        padding-top: 20px !important;
    }

    /* REGOLAZIONE PER LA STAMPA REALE: Nasconde tutto tranne il foglio */
    @media print {
        header, [data-testid="stSidebar"], .stButton, [data-testid="stHeader"], button, [data-testid="stTabs"] nav, .no-print {
            display: none !important;
            visibility: hidden !important;
        }
        .main .block-container {
            padding: 0px !important;
            margin: 0px !important;
        }
        .foglio-word {
            box-shadow: none !important;
            border: none !important;
            padding: 0px !important;
            margin: 0px !important;
            max-width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# CONFIGURAZIONE CLIENT (Doppio supporto SDK Google)
# ==========================================================
if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Configurazione incompleta: Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

try:
    from google import genai
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
    usa_sdk_nuovo = True
except ImportError:
    import google.generativeai as dg_genai
    dg_genai.configure(api_key=st.secrets["GEMINI_KEY"])
    usa_sdk_nuovo = False

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
    st.rerun()

tab1, tab2 = st.tabs(["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

# --- SCHEDA 1: GENERATORE DI VERIFICHE ---
with tab1:
    st.header("Generatore di Compiti in Classe (Livello Scuole Superiori)")
    
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
            with st.spinner("L'intelligenza artificiale sta scrivendo il compito per le superiori..."):
                prompt_sistema = (
                    "Sei un assistente didattico esperto per i licei e gli istituti tecnici italiani (Scuola Superiore). "
                    "Genera la verifica e le relative risposte esclusivamente in lingua italiana. "
                    "Il livello di complessità, il lessico e i criteri di valutazione devono essere calibrati per studenti delle scuole superiori. "
                    "Formatta l'intero output in testo chiaro (Markdown di base). "
                    "Inserisci obbligatoriamente il tag specifico [SOLUZIONI] subito prima di iniziare a scrivere le chiavi di correzione o le risposte corrette."
                )
                
                if stile_domande == "Domande miste (Vero/Falso, Crocette, Aperte)":
                    dettaglio_stile = "strutturata con un mix avanzato di quesiti a scelta multipla (con 4 opzioni), quesiti Vero o Falso giustificati e domande a risposta aperta che richiedono capacità di sintesi ed elaborazione."
                else:
                    dettaglio_stile = f"composta rigorosamente da quesiti di tipo: {stile_domande} adatti a studenti di scuola superiore."

                prompt_utente = (
                    f"Crea una verifica scolastica completa sull'argomento: '{argomento}'. "
                    f"La struttura deve essere: {dettaglio_stile}. "
                    f"Il numero totale di quesiti richiesto è: {numero_domande}. "
                    f"Ricorda di inserire in fondo le risposte esatte o una griglia di valutazione strutturata per il docente, anticipata dal tag richiesto."
                )
                
                try:
                    if usa_sdk_nuovo:
                        risposta = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_utente,
                            config={'system_instruction': prompt_sistema, 'temperature': 0.6}
                        )
                        testo_generato = risposta.text
                    else:
                        model = dg_genai.GenerativeModel(
                            model_name='gemini-2.5-flash',
                            system_instruction=prompt_sistema
                        )
                        risposta = model.generate_content(prompt_utente)
                        testo_generato = risposta.text
                    
                    st.session_state["testo_verifica"] = testo_generato
                    st.success("Verifica per le superiori generata con successo!")
                
                except Exception as e:
                    st.error(f"⚠️ Errore durante la generazione con Gemini: {e}")

    # RENDERING DEL FOGLIO REALE PRONTO DA STAMPARE
    if "testo_verifica" in st.session_state:
        testo_grezzo = st.session_state['testo_verifica']
        
        st.write("### 🖨️ Stampa la Verifica Pronta")
        
        # Pulsante JavaScript nativo per avviare la stampa del browser
        st.markdown("""
            <button onclick="window.print()" style="
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 20px;
            " class="no-print">
                🖨️ Clicca qui per Stampare o Salvare in PDF
            </button>
        """, unsafe_allow_html=True)

        # Elaborazione stringhe pulita senza bug di concatenazione o split errati
        if "[SOLUZIONI]" in testo_grezzo:
            parti_testo = testo_grezzo.split("[SOLUZIONI]")
            compito_pulito = parti_testo[0].strip().replace('\n', '<br>')
            soluzioni_pulite = parti_testo[1].strip().replace('\n', '<br>')
            
            corpo_documento_html = (
                compito_pulito +
