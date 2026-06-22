import streamlit as st
from google import genai

# Configurazione Pagina
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="wide")

# Funzione per caricare il tuo CSS avanzato
def carica_css():
    try:
        with open("stile.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ File 'stile.css' non trovato.")

carica_css()

# --- SELETTORE TEMA ---
# Questo div serve al tuo CSS per attivare le regole (es. .tema-total-dark)
# Puoi rendere questo dinamico con uno slider in sidebar se vuoi
st.markdown('<div id="tema-attivo" class="tema-total-dark"></div>', unsafe_allow_html=True)

# --- LOGIN (Usa la classe box-login definita nel tuo CSS) ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    # Wrapping nel div con classe box-login come da tuo CSS
    st.markdown('<div class="box-login">', unsafe_allow_html=True)
    st.title("🔒 Area Docenti")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome.strip() != "":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- RESTO DELL'APP ---
# Assicurati di avvolgere i blocchi di contenuto in div con le classi 
# che hai definito nel CSS (es. class="foglio-word" o class="box-parametri")
