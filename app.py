import streamlit as st
import os
import json
import google.generativeai as genai

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# STILE GRAFICO APPLICATO ALL'INTERA APPLICAZIONE
st.markdown("""
    <style>
    .foglio-word {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 40px 50px !important;
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
# CONFIGURAZIONE CLIENT (Google Generative AI SDK)
# ==========================================================
if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Configurazione incompleta: Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

# Configurazione standard e pulita
genai.configure(api_key=st.secrets["GEMINI_KEY"])

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
# INTERFACCIA PRINCIPALE CON NAVIGAZIONE IN SIDEBAR
# ==========================================================
st.sidebar.title("🛠️ Menu EduCorrect")
st.sidebar.write(f"👤 Utente: **{st.session_state['utente_connesso']}**")

modalita = st.sidebar.radio(
    "Scegli l'operazione da eseguire:",
    ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"]
)

st.sidebar.markdown("---")
if st.sidebar.button("Disconnetti / Esci"):
    st.session_state["autenticato"] = False
    st.session_state["utente_connesso"] = ""
    if "testo_verifica" in st.session_state:
        del st.session_state["testo_verifica"]
    if "analisi_correzione" in st.session_state:
        del st.session_state["analisi_correzione"]
    st.rerun()

# ==========================================================
# LOGICA DI CONTROLLO DELLE SEZIONI
# ==========================================================

# --- SEZIONE 1: GENERATORE DI VERIFICHE ---
if modalita == "🚀 Genera Nuova Verifica":
    st.header("Generatore di Compiti in Classe")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        argomento = st.text_input("Inserisci l'argomento della verifica:", placeholder="Es. I vulcani...")
    with col2:
        stile_domande = st.selectbox("Tipo di domande:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3:
        difficolta = st.selectbox("Livello di difficoltà:", ["facile", "media", "difficile"])
    
    numero_domande = st.slider("Numero di domande totali:", min_value=1, max_value=20, value=5)
    
    if st.button("Genera Testo Verifica"):
        if not argomento:
            st.error("Scrivi un argomento prima di generare!")
        else:
            with st.spinner("Generazione compito in corso con Gemini..."):
                prompt_sistema = (
                    "Sei un assistente didattico esperto per i licei e gli istituti tecnici italiani (Scuola Superiore). "
                    "Genera la verifica e le relative risposte esclusivamente in lingua italiana. "
                    f"Il livello di complessità generale deve essere calibrato come '{difficolta}' per gli standard delle scuole superiori. "
                    "Inserisci obbligatoriamente il tag specifico [SOLUZIONI] subito prima di iniziare a scrivere le chiavi di correzione."
                )
                prompt_utente = f"Crea una verifica superiore di livello '{difficolta}' su '{argomento}'. Tipo domande: {stile_domande}. Numero quesiti: {numero_domande}."
                
                try:
                    # AGGIORNATO: Utilizzo del modello di produzione gemini-2.5-flash
                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=prompt_sistema)
                    risposta = model.generate_content(prompt_utente)
                    st.session_state["testo_verifica"] = risposta.text
                    st.success("Verifica generata!")
                except Exception as e:
                    st.error(f"⚠️ Errore di generazione: {e}")

    if "testo_verifica" in st.session_state:
        testo_grezzo = st.session_state['testo_verifica']
        st.info("💡 Premi **CTRL + P** (Windows) o **CMD + P** (Mac) per stampare direttamente o salvare in PDF.")
        
        testo_html = testo_grezzo.replace('\n', '<br>')
        div_salto_pagina = "<div class='salto-pagina'><h3 style='color: #000000; border-bottom: 2px solid #000000; padding-bottom: 5px;'>🔑 CHIAVE DI CORREZIONE (FOGLIO DOCENTE)</h3><br>"
        corpo_documento_html = testo_html.replace("[SOLUZIONI]", div_salto_pagina + "</div>")

        intestazione_word_html = f"<table class='tabella-intestazione'><tr><td style='width: 60%; font-weight: bold;'>Istituto d'Istruzione Superiore</td><td style='width: 40%; text-align: right; font-weight: bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: _____________________________________</td><td style='text-align: right;'>Classe: ____________  Sez. ____</td></tr><tr><td style='padding-top: 10px; font-size: 16px; font-weight: bold;'>Materia: Verifica scritta di approfondimento ({difficolta.capitalize()})</td><td style='padding-top: 10px; text-align: right; font-size: 16px; font-weight: bold;'>Oggetto: {argomento.capitalize()}</td></tr></table>"
        st.markdown("<div class='foglio-word'>" + intestazione_word_html + corpo_documento_html + "</div>", unsafe_allow_html=True)


# --- SEZIONE 2: SCANSIONA E CORREGGI ---
elif modalita == "🔍 Scansiona e Correggi":
    st.header("🔍 Correttore Intelligente di Compiti")
    st.write("Inserisci l'elaborato dell'alunno per correggerlo ed emettere il voto in decimi.")
    
    col_input, col_criteri = st.columns(2)
    
    with col_input:
        file_compito = st.file_uploader("📂 Carica file (Immagine del compito o PDF):", type=["png", "jpg", "jpeg", "pdf"])
        testo_manuale = st.text_area("✍️ Incolla qui il testo scritto a mano:", height=150, placeholder="Risposte dello studente...")
        
    with col_criteri:
        griglia_riferimento = st.text_area("🔑 Criteri di valutazione o soluzioni di riferimento:", 
                                           value=st.session_state.get("testo_verifica", ""), height=230,
                                           placeholder="I dati della verifica generata nell'altra sezione vengono copiati qui in automatico.")

    if st.button("🔎 Avvia Correzione Automatica"):
        if not file_compito and not testo_manuale:
            st.error("Inserisci un compito inserendo del testo o caricando una foto.")
        else:
            with st.spinner("Analisi del compito e calcolo del voto in corso..."):
                prompt_correzione_sistema = (
                    "Sei un docente di scuola superiore italiana severo, preciso e costruttivo. "
                    "Analizza il compito dello studente confrontandolo con i criteri forniti. "
                    "Restituisci l'analisi strutturata in italiano secondo questo schema:\n"
                    "1. Riassunto del compito analizzato.\n"
                    "2. Analisi degli errori rilevati.\n"
                    "3. Elementi positivi riscontrati.\n"
                    "4. Suggerimenti mirati.\n"
                    "5. VALUTAZIONE FINALE: Voto numerico in decimi (da 2 a 10)."
                )
                
                contenuto_richiesta = []
                
                if file_compito:
                    file_bytes = file_compito.read()
                    immagine_struttura = {"mime_type": file_compito.type, "data": file_bytes}
                    contenuto_richiesta.append(immagine_struttura)
                
                testo_da_inviare = f"Compito dello studente:\n{testo_manuale}\n\nCriteri/Soluzioni:\n{griglia_riferimento}"
                contenuto_richiesta.append(testo_da_inviare)
                
