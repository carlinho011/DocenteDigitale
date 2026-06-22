import streamlit as st
from google import genai

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# --- GESTIONE AUTH ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state: st.session_state["nome_docente"] = ""

if not st.session_state["autenticato"]:
    st.markdown("<div style='max-width: 400px; margin: 80px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.title("🔒 Accesso Docente")
    nome = st.text_input("Nome Prof:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome.strip() != "":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else:
            st.error("Credenziali errate o nome mancante.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- BARRA LATERALE ---
st.sidebar.markdown(f"## 👤 Prof. {st.session_state['nome_docente']}")
st.sidebar.divider()
st.sidebar.header("📁 Strumenti Didattici")

# Radio button per navigare tra le sezioni
funzione = st.sidebar.radio(
    "Seleziona la modalità:",
    ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"]
)

st.sidebar.divider()
if st.sidebar.button("🚪 Disconnetti"):
    st.session_state["autenticato"] = False
    st.rerun()

# --- LOGICA CONTENUTI ---
if funzione == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore di Verifiche")
    st.write("Configura qui sotto i dettagli per creare il tuo compito in classe.")
    # Inserisci qui i tuoi widget per la generazione
    
elif funzione == "🔍 Scansiona e Correggi":
    st.title("🔍 Centro Correzione")
    st.write("Carica le scansioni dei compiti per avviare la correzione automatica.")
    # Inserisci qui la logica per il caricamento file
