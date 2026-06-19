import streamlit as st
import os
import json

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# STILE GRAFICO: Forza l'applicazione a mostrare un vero foglio A4 bianco simulato
st.markdown("""
    <style>
    /* Contenitore stile foglio Word A4 */
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
    
    /* Intestazione formale per Scuola Superiore */
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
    
    /* Salto pagina visivo ed effettivo per la stampa */
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

# Controllo autenticazione
if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state:
    st.session_state["utente_connesso"] = ""

# SCHERMATA DI LOGIN
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
                    "Il livello di complessità deve essere calibrati per studenti delle scuole superiori. "
                    "Inserisci obbligatoriamente il tag [SOLUZIONI] subito prima di iniziare a scrivere le chiavi di correzione."
                )
                
                prompt_utente = f"Crea una verifica superiore su '{argomento}'. Tipo: {stile_domande}. Numero quesiti: {numero_domande}. Includi le soluzioni in fondo precedute dal tag richiesto."
                
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
                    st.success("Verifica generata!")
                except Exception as e:
                    st.error(f"⚠️ Errore: {e}")

    # RENDERING ANTEPRIMA E TASTO DI SCARICAMENTO DIRETTO IN FORMATO WORD (.DOC)
    if "testo_verifica" in st.session_state:
        testo_grezzo = st.session_state['testo_verifica']
        
        st.write("### 📄 Esporta e Visualizza")

        # Conversione e preparazione del testo compatibile per Microsoft Word (.doc)
        testo_pulito_per_word = testo_grezzo.replace("[SOLUZIONI]", "\n\n--- FOGLIO CHIAVE DI CORREZIONE DOCENTE ---\n\n")

        # PULSANTE DI DOWNLOAD DIRETTO CONFIGURATO IN FORMATO MICROSOFT WORD
        st.download_button(
            label="📥 Clicca qui per Scaricare la Verifica in formato Word (.doc)",
            data=testo_pulito_per_word,
            file_name=f"verifica_{argomento.lower().replace(' ', '_')}.doc",
            mime="application/msword",
            help="Salva immediatamente il file sul PC come documento Word modificabile"
        )

        # COSTRUZIONE DELL'ANTEPRIMA GRAFICA (Foglio Word A4 bianco sullo schermo)
        testo_html = testo_grezzo.replace('\n', '<br>')
        div_salto_pagina = "<div class='salto-pagina'><h3 style='color: #000000; border-bottom: 2px solid #000000; padding-bottom: 5px; font-family: Arial, sans-serif;'>🔑 CHIAVE DI CORREZIONE (FOGLIO DOCENTE)</h3><br>"
        corpo_documento_html = testo_html.replace("[SOLUZIONI]", div_salto_pagina + "</div>")

        intestazione_word_html = f"<table class='tabella-intestazione'><tr><td style='width: 60%; font-weight: bold;'>Istituto d'Istruzione Superiore</td><td style='width: 40%; text-align: right; font-weight: bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: _____________________________________</td><td style='text-align: right;'>Classe: ____________  Sez. ____</td></tr><tr><td style='padding-top: 10px; font-size: 16px; font-weight: bold;'>Materia: Verifica scritta di approfondimento</td><td style='padding-top: 10px; text-align: right; font-size: 16px; font-weight: bold;'>Oggetto: {argomento.capitalize()}</td></tr></table>"

        # Mostra il foglio Word formattato a schermo
        st.markdown("<div class='foglio-word'>" + intestazione_word_html + corpo_documento_html + "</div>", unsafe_allow_html=True)

# --- SCHEDA 2: SCANSIONA E CORREGGI ---
with tab2:
    st.header("Correttore di Compiti")
    st.write("Sviluppo della sezione di valutazione automatica.")
