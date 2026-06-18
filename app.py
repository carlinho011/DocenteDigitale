import streamlit as st
import os
import base64
from openai import OpenAI

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# LETTURA DELLA CHIAVE OPENAI (Nascosta nei Secrets di Streamlit per sicurezza)
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# ==========================================
# GESTIONE ACCESSO CON PASSWORD PERSONALE
# ==========================================
# Definiamo la password che i professori dovranno usare per entrare
PASSWORD_CORRETTA = "PROF2026"  # Puoi cambiare questa parola con quella che vuoi

# Controlliamo se l'utente ha già effettuato l'accesso
if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False

# Se l'utente NON è autenticato, mostra la schermata di login
if not st.session_state["autenticato"]:
    st.title("🔒 Accesso Riservato - EduCorrect")
    st.write("Inserisci la password fornita dall'amministratore per utilizzare il software.")
    
    password_inserita = st.text_input("Password di accesso:", type="password")
    
    if st.button("Accedi"):
        if password_inserita == PASSWORD_CORRETTA:
            st.session_state["autenticato"] = True
            st.rerun()
        else:
            st.error("❌ Password errata! Riprova o contatta l'assistenza.")
            
    st.stop() # Blocca il resto del codice se la password è sbagliata

# ==========================================
# SE LA PASSWORD È GIUSTA, MOSTRA L'APP VERA
# ==========================================
st.title("📝 EduCorrect: Crea e Correggi Verifiche con l'IA")
st.write("Semplifica il tuo lavoro di docente. Genera compiti e correggi le foto delle verifiche in pochi secondi.")

# Tasto per fare il Logout nella barra laterale
if st.sidebar.button("Esci dal profilo"):
    st.session_state["autenticato"] = False
    st.rerun()

if not OPENAI_KEY:
    st.error("⚠️ Errore di sistema: Manca la configurazione del server (Configura la API KEY nei Secrets di Streamlit).")

# SCHEDE (TABS) IN ITALIANO
tab1, tab2 = st.tabs(["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

# --- SCHEDA 1: GENERATORE ---
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
            st.error("Il sistema non è configurato con OpenAI.")
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
                    
                    risposta = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_utente}])
                    st.success("Verifica Generata con Successo!")
                    st.text_area("Copia il testo qui sotto:", value=risposta.choices.message.content, height=400)
                except Exception as e:
                    st.error(f"Errore: {str(e)}")

# --- SCHEDA 2: SCANNER ---
with tab2:
    st.header("Scanner e Correttore Automatico")
    soluzioni_prof = st.text_area("Incolla qui le soluzioni corrette della verifica (o i criteri di valutazione):")
    foto_caricata = st.file_uploader("Scegli o trascina la foto della verifica (.jpg, .jpeg, .png):", type=["jpg", "jpeg", "png"])
    
    if foto_caricata is not None:
        st.image(foto_caricata, caption="Anteprima del compito dello studente", width=400)
        
    if st.button("Scansiona e Correggi Compito"):
        if not client:
            st.error("Il sistema non è configurato con OpenAI.")
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
                            {"role": "user", "content": [{"type": "text", "text": f"Soluzioni: {soluzioni_prof}"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}
                        ],
                        temperature=0.2
                    )
                    st.success("Correzione Completata!")
                    st.markdown(risposta.choices.message.content)
                except Exception as e:
                    st.error(f"Errore durante la scansione: {str(e)}")
