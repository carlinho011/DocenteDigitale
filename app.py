import streamlit as st, os, json, re, time
from google import genai
from google.genai import types

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# Funzione per caricare CSS locale
def carica_css():
    st.markdown("""
    <style>
        .tabella-intestazione { width: 100%; border-collapse: collapse; }
        .tabella-intestazione td { padding: 5px; border-bottom: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

carica_css()

# --- GESTIONE AUTH E CLIENT ---
if "GEMINI_KEY" not in st.secrets: 
    st.error("⚠️ Inserisci 'GEMINI_KEY' nei Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
UTENTI = json.loads(st.secrets.get("UTENTI_ABILITATI", '{"admin@educorrect.it": "AdminPass2026"}'))

if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state: st.session_state["utente_connesso"] = ""

# --- LOGICA DI RENDERIZZAZIONE (ex correttore.py) ---
def renderizza_documento_stampa(argomento, diffic, intestazione_html, domande_html, testo_domande, testo_soluzioni):
    st.markdown(intestazione_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(domande_html, unsafe_allow_html=True)
    
    with st.expander("🔑 Visualizza Soluzioni"):
        st.write(testo_soluzioni)

def mostra_interfaccia_correzione(client, types):
    st.title("🔍 Scansiona e Correggi")
    st.info("Funzionalità di correzione OCR/AI in fase di sviluppo.")

# --- SCHERMATA LOGIN ---
if not st.session_state["autenticato"]:
    st.markdown("<div style='max-width: 500px; margin: 80px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
    st.title("🔒 Area Riservata Docenti")
    em = st.text_input("Email:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if em in UTENTI and pw == UTENTI[em]: 
            st.session_state.update({"autenticato": True, "utente_connesso": em})
            st.rerun()
        else: st.error("Credenziali errate.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- APPLICAZIONE PRINCIPALE ---
st.sidebar.title("📝 EduCorrect AI")
modalita = st.sidebar.radio("FUNZIONALITÀ:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

if modalita == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore Integrato")
    col1, col2, col3 = st.columns(3)
    argomento = col1.text_input("Argomento:")
    stile = col2.selectbox("Tipologia:", ["Domande miste", "Risposte aperte"])
    diff = col3.selectbox("Difficoltà:", ["facile", "media", "difficile"])
    num = st.slider("Numero Domande:", 1, 20, 5)

    if st.button("Elabora"):
        sys_p = "Sei un assistente didattico. Genera la verifica. Inserisci [SOLUZIONI] prima delle risposte."
        user_p = f"Crea verifica di {diff} su {argomento}. Tipo: {stile}. Quesiti: {num}."
        
        with st.spinner("Elaborazione..."):
            risp = client.models.generate_content(model="gemini-2.0-flash", contents=user_p, config={'system_instruction': sys_p})
            st.session_state["testo_verifica"] = risp.text

    if "testo_verifica" in st.session_state:
        tg = st.session_state['testo_verifica']
        parti = tg.split("[SOLUZIONI]") if "[SOLUZIONI]" in tg else [tg, "Nessuna soluzione."]
        i_html = f"<h3>Verifica: {argomento}</h3>"
        renderizza_documento_stampa(argomento, diff, i_html, parti[0].replace('\n', '<br>'), parti[0], parti[1])

elif modalita == "🔍 Scansiona e Correggi":
    mostra_interfaccia_correzione(client, types)
