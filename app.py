import streamlit as st
import os
import base64
import json
from openai import OpenAI

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# ==========================================================
# CONFIGURAZIONE CLIENT (GitHub Models tramite SDK OpenAI)
# ==========================================================
# Legge il token dai Secrets di Streamlit o dalle variabili d'ambiente
GITHUB_TOKEN = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

client = None
if GITHUB_TOKEN:
    client = OpenAI(
        base_url="https://azure.com",  # Endpoint corretto per GitHub Models
        api_key=GITHUB_TOKEN
    )

# ==========================================================
# GESTIONE ACCOUNT MULTIPLI TRAMITE SECRETS
# ==========================================================
# Credenziali di default per i tuoi test iniziali
UTENTI_DEFAULT = {
    "admin@educorrect.it": "AdminPass2026",
    "prof.test@scuola.it": "TestScuola99"
}

# Caricamento dinamico degli utenti dai Secrets di Streamlit
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
            
    st.stop() # Blocca l'esecuzione se non si è loggati

# ==========================================================
# INTERFACCIA PRINCIPALE (UTENTE LOGGATO)
# ==========================================================
st.title("📝 EduCorrect: Crea e Correggi Verifiche con l'IA")
st.sidebar.write(f"👤 Connesso come: **{st.session_state['utente_connesso']}**")

# Pulsante per effettuare il Logout
if st.sidebar.button("Disconnetti / Esci"):
    st.session_state["autenticato"] = False
    st.session_state["utente_connesso"] = ""
    st.rerun()

if not GITHUB_TOKEN:
    st.error("⚠️ Errore di sistema: Manca la configurazione del server (Configura il tuo GITHUB TOKEN nei Secrets).")

# SCHEDE DI NAVIGAZIONE IN ITALIANO
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
        if not client:
            st.error("Il sistema non è configurato correttamente con il token di GitHub.")
        elif not argomento:
            st.error("Scrivi un argomento prima di generare!")
        else:
            with st.spinner("L'intelligenza artificiale sta scrivendo il compito in italiano..."):
                try:
                    prompt_sistema = "Sei un assistente didattico per professori italiani. Genera la verifica e le risposte SOLO IN ITALIANO."
                    if stile_domande == "Domande miste (Vero/Falso, Crocette, Aperte)":
                        dettaglio_stile = "strutturata con un mix bilanciato di domande a scelta multipla, quesiti Vero o Falso e domande a risposta aperta."
                    else:
                        dettaglio_stile = f"composta esclusivamente da domande di tipo: {stile_domande}."

                    prompt_utente = f"Crea una verifica superiore su: {argomento}. Struttura: {dettaglio_stile}. Numero quesiti: {numero_domande}. Includi soluzioni in fondo."
                    
                    risposta = client.chat.completions.create(
                        model="gpt-4o", 
                        messages=[
                            {"role": "system", "content": prompt_sistema}, 
                            {"role": "user", "content": prompt_utente}
                        ]
                    )
                    st.success("Verifica Generata con Successo!")
                    st.text_area("Copia il testo qui sotto:", value=risposta.choices[0].message.content, height=400)
                except Exception as e:
                    st.error(f"Errore: {str(e)}")

# --- SCHEDA 2: SCANNER E CORRETTORE ---
with tab2:
    st.header("Scanner e Correttore Automatico")
    soluzioni_prof = st.text_area("Incolla qui le soluzioni corrette della verifica (o i criteri di valutazione):")
    foto_caricata = st.file_uploader("Scegli o trascina la foto della verifica (.jpg, .jpeg, .png):", type=["jpg", "jpeg", "png"])
    
    if foto_caricata is not None:
        st.image(foto_caricata, caption="Anteprima del compito dello studente", width=400)
        
    if st.button("Scansiona e Correggi Compito"):
        if not client:
            st.error("Il sistema non è configurato correttamente con il token di GitHub.")
        elif not soluzioni_prof or not foto_caricata:
            st.error("Devi inserire sia le soluzioni sia la foto del compito!")
        else:
            with st.spinner("L'IA sta leggendo la calligrafia..."):
                try:
                    bytes_data = foto_caricata.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    prompt_sistema = "Sei un professore italiano. Analizza la foto, decifra la scrittura a mano, confrontala con le soluzioni e restituisci in italiano: VOTO FINALE (1-10), RISPOSTE CORRETTE, ERRORI RISCONTRATI e NOTA DEL DOCENTE."
                    
                    risposta = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": [
                                {"type": "text", "text": f"Soluzioni: {soluzioni_prof}"}, 
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]}
                        ],
                        temperature=0.2
                    )
                    st.success("Correzione Completata!")
                    st.markdown(risposta.choices[0].message.content)
                except Exception as e:
                    st.error(f"Errore durante la scansione: {str(e)}")

