import streamlit as st
import os
import base64
import json
from openai import OpenAI

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# Stili CSS per la stampa pulita (Nasconde la sidebar e i pulsanti di Streamlit quando stampi)
st.markdown("""
    <style>
    @media print {
        header, [data-testid="stSidebar"], .stButton, [data-testid="stHeader"] {
            display: none !map-important;
            visibility: hidden;
        }
        .main .block-container {
            padding-top: 0px;
            padding-bottom: 0px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# CONFIGURAZIONE CLIENT (GitHub Models tramite SDK OpenAI)
# ==========================================================
GITHUB_TOKEN = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

client = None
if GITHUB_TOKEN:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",  # URL CORRETTO per GitHub Models
        api_key=GITHUB_TOKEN
    )

# ==========================================================
# GESTIONE ACCOUNT MULTIPLI TRAMITE SECRETS
# ==========================================================
UTENTI_DEFAULT = {
    "admin@educorrect.it": "AdminPass2026",
    "prof.test@scuola.it": "TestScuola99"
}

if "UTENTI_ABILITATI" in st.secrets:
    try:
        UTENTI_ATTIVI = json.loads(st.secrets["UTENTI_ABILITATI"])
    except Exception:
        UTENTI_ATTIVI = UTENTI_DEFAULT
else:
    UTENTI_ATTIVI = UTENTI_DEFAULT

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
    st.rerun()

if not GITHUB_TOKEN:
    st.error("⚠️ Errore di sistema: Manca la configurazione del server (Configura il tuo GITHUB TOKEN nei Secrets).")

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
                    st.session_state["testo_verifica"] = risposta.choices[0].message.content
                    st.success("Verifica Generata con Successo!")
                except Exception as e:
                    st.error(f"Errore: {str(e)}")

    # Se la verifica è stata generata, mostra l'anteprima e il pulsante Stampa
    if "testo_verifica" in st.session_state:
        st.subheader("Anteprima della Verifica")
        
        # Mostriamo il testo formattato in un box visivo
        st.markdown(f"<div style='background-color: #f9f9f9; padding: 20px; border-radius: 5px; border: 1px solid #ddd;'>{st.session_state['testo_verifica'].replace('\n', '<br>')}</div>", unsafe_allow_html=True)
        
        # Pulsante HTML/JS nativo per avviare la stampa della pagina del browser
        st.html("""
            <br>
            <button onclick="window.print()" style="
                background-color: #4CAF50; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 16px;">
                🖨️ Stampa questa Verifica
            </button>
        """)

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
                    st.session_state["testo_correzione"] = risposta.choices[0].message.content
                    st.success("Correzione Completata!")
                except Exception as e:
                    st.error(f"Errore durante la scansione: {str(e)}")

    # Se la correzione esiste, mostra l'anteprima e il pulsante per stamparla
    if "testo_correzione" in st.session_state:
        st.subheader("Report della Correzione")
        st.markdown(f"<div style='background-color: #fff3cd; padding: 20px; border-radius: 5px; border: 1px solid #ffeeba;'>{st.session_state['testo_correzione'].replace('\n', '<br>')}</div>", unsafe_allow_html=True)
        
        st.html("""
            <br>
            <button onclick="window.print()" style="
                background-color: #008CBA; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 16px;">
                🖨️ Stampa Report Correzione
            </button>
        """)


