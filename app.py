import streamlit as st
import os
import json

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# Stili CSS per simulare un foglio Word A4 bianco con ombreggiatura e gestire la stampa
st.markdown("""
    <style>
    /* Stile Simulazione Foglio Word A4 */
    .foglio-word {
        background-color: #ffffff;
        color: #000000;
        padding: 40px 50px;
        margin: 20px auto;
        max-width: 850px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
        border: 1px solid #e0e0e0;
        font-family: 'Times New Roman', Times, serif, Arial;
        line-height: 1.6;
        font-size: 16px;
    }
    
    /* Intestazione del Compito */
    .tabella-intestazione {
        width: 100%;
        border-collapse: collapse;
        border-bottom: 2px solid #000000;
        margin-bottom: 25px;
        font-family: Arial, sans-serif;
        font-size: 14px;
    }
    .tabella-intestazione td {
        border: none;
        padding: 6px 0;
    }
    
    /* Classe per forzare l'interruzione di pagina nella stampa fisica o PDF */
    .salto-pagina {
        page-break-before: always;
        break-before: page;
        margin-top: 40px;
        border-top: 1px dashed #666666;
        padding-top: 20px;
    }

    /* Ottimizzazione per la stampa fisica reale (Nasconde l'interfaccia web) */
    @media print {
        header, [data-testid="stSidebar"], .stButton, [data-testid="stHeader"], button, [data-testid="stTabs"] nav {
            display: none !important;
            visibility: hidden;
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
                # Istruzioni mirate per le scuole superiori (secondaria di secondo grado)
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

    # GESTIONE UNIFICAZIONE E DOWNLOAD UNICO
    if "testo_verifica" in st.session_state:
        testo_grezzo = st.session_state['testo_verifica']
        
        # Sostituisce il tag con la formattazione grafica per la separazione di pagina
        blocco_salto_pagina = "\n\n=== [SALTO PAGINA DI STAMPA] ===\n\n🔑 CHIAVE DI CORREZIONE E CRITERI DI VALUTAZIONE (FOGLIO RISERVATO AL DOCENTE)\n\n"
        testo_per_download = "📝 VERIFICA DI CLASSE\n\n" + testo_grezzo.replace("[SOLUZIONI]", blocco_salto_pagina)

        # UNICO PULSANTE DI DOWNLOAD (Stile Word)
        st.write("### 💾 Salva il Compito sul PC")
        st.download_button(
            label="📥 Scarica Intero Documento Word (.txt)",
            data=testo_per_download,
            file_name=f"compito_superiori_{argomento.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            help="Scarica un unico file di testo contenente la verifica impaginata e, a seguire, il foglio delle correzioni per il docente."
        )

        # COSTRUZIONE ANTEPRIMA GRAFICA "STILE FOGLIO WORD A4"
        st.subheader("Anteprima di Stampa")
        
        # Divisione del testo per applicare le classi CSS di interruzione di pagina
        if "[SOLUZIONI]" in testo_grezzo:
            parti_html = testo_grezzo.split("[SOLUZIONI]")
            testo_compito_html = parti_html[0].replace('\n', '<br>')
            testo_soluzioni_html = parti_html[1].replace('\n', '<br>')
