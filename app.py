import streamlit as st
import os
import base64
import json
from openai import OpenAI

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
# CONFIGURAZIONE CLIENT (GitHub Models tramite SDK OpenAI)
# ==========================================================
# Legge il token dai Secrets di Streamlit o dalle variabili d'ambiente
GITHUB_TOKEN = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

client = None
if GITHUB_TOKEN:
    client = OpenAI(
        base_url="https://azure.com",  # Endpoint ufficiale GitHub Models
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
                prompt_sistema = "Sei un assistente didattico per professori italiani. Genera la verifica e le risposte SOLO IN ITALIANO. Inserisci OBBLIGATORIAMENTE il tag [SOLUZIONI] subito prima di scrivere le risposte corrette o i criteri di valutazione."
                
                if stile_domande == "Domande miste (Vero/Falso, Crocette, Aperte)":
                    dettaglio_stile = "strutturata con un mix bilanciato di domande a scelta multipla, quesiti Vero o Falso e domande a risposta aperta."
                else:
                    dettaglio_stile = f"composta esclusivamente da domande di tipo: {stile_domande}."

                prompt_utente = f"Crea una verifica superiore su: {argomento}. Struttura: {dettaglio_stile}. Numero quesiti: {numero_domande}. Includi soluzioni in fondo anticipate dal tag richiesto."
                
                # Chiamata API protetta
                try:
                    risposta = client.chat.completions.create(
                        model="gpt-4o", 
                        messages=[
                            {"role": "system", "content": prompt_sistema}, 
                            {"role": "user", "content": prompt_utente}
                        ]
                    )
                    
                    testo_estratto = ""
                    try:
                        testo_estratto = risposta.choices[0].message.content
                    except Exception:
                        try:
                            testo_estratto = risposta.choices.message.content
                        except Exception:
                            try:
                                testo_estratto = risposta["choices"][0]["message"]["content"]
                            except Exception:
                                # MODIFICA DI DEBUG: Mostra a schermo l'errore effettivo inviato da GitHub
                                testo_estratto = f"Impossibile leggere i dati. Errore generato da GitHub: {str(risposta)}"
                    
                    st.session_state["testo_verifica"] = testo_estratto
                    st.success("Operazione completata!")
                except Exception as api_err:
                    st.session_state["testo_verifica"] = f"Errore di connessione API: {str(api_err)}"

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
        
        box_anteprima = """
        <div style="background-color: #f9f9f9; color: #111111 !important; padding: 25px; border-radius: 6px; border: 1px solid #ccc; font-family: sans-serif; line-height: 1.6; font-size: 16px;">
            {0}
            {1}
        </div>
        <br>
        <button onclick="window.print()" style="background-color: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
            🖨️ Stampa Verifica (Soluzioni separate)
        </button>
        """.format(intestazione_studente, testo_elaborato)
        
        st.html(box_anteprima)

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
