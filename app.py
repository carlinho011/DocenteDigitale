import streamlit as st
import os
import json

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
# CONFIGURAZIONE CLIENT (Doppio supporto SDK Google)
# ==========================================================
if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Configurazione incompleta: Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

# Sistema di compatibilità automatica per evitare blocchi legati a requirements.txt
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
                    if usa_sdk_nuovo:
                        risposta = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_utente,
                            config={'system_instruction': prompt_sistema, 'temperature': 0.7}
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
                    st.success("Operazione completata con Gemini!")
                
                except Exception as e:
                    st.error(f"⚠️ Errore durante la generazione con Gemini: {e}")

    # GESTIONE SEPARAZIONE E DOWNLOAD FILE
    if "testo_verifica" in st.session_state:
        intero_testo = st.session_state['testo_verifica']
        
        # Separa il testo della verifica dalle soluzioni usando il tag [SOLUZIONI]
        if "[SOLUZIONI]" in intero_testo:
            parti = intero_testo.split("[SOLUZIONI]")
            solo_verifica = parti[0].strip()
            solo_soluzioni = parti[1].strip()
        else:
            solo_verifica = intero_testo
            solo_soluzioni = "Le soluzioni non sono state generate separatamente dall'IA."

        # SEZIONE PULSANTI DI DOWNLOAD (Visualizzati affiancati)
        st.write("### 💾 Scarica i Documenti Generati")
        down_col1, down_col2 = st.columns(2)
        
        with down_col1:
            st.download_button(
                label="📥 Scarica Solo Verifica (Per Studenti)",
                data=solo_verifica,
                file_name=f"verifica_{argomento.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                help="Scarica il testo del compito senza le risposte"
            )
            
        with down_col2:
            st.download_button(
                label="📥 Scarica Solo Soluzioni (Per Docente)",
                data=solo_soluzioni,
                file_name=f"soluzioni_{argomento.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                help="Scarica solo le risposte corrette e i criteri di valutazione"
            )

        # ANTEPRIMA WEB CON INTESTAZIONE SCOLASTICA
        st.subheader("Anteprima Grafica del Compito")
        testo_html = solo_verifica.replace('\n', '<br>')
        soluzioni_html = solo_soluzioni.replace('\n', '<br>')
        
        blocco_salto_pagina = f"<div class='salto-pagina'><h3>🔑 Soluzioni e Criteri di Valutazione (Foglio Docente)</h3><br>{soluzioni_html}</div>"
        
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
        
        # Mostra a schermo l'intera struttura impaginata
        st.markdown(intestazione_studente + testo_html + blocco_salto_pagina, unsafe_allow_html=True)

# --- SCHEDA 2: SCANSIONA E CORREGGI ---
with tab2:
    st.header("Correttore di Compiti")
    st.write("Qui puoi implementare la logica per correggere i testi dei tuoi studenti.")
