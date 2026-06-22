import streamlit as st
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="wide")

# --- FUNZIONE CARICAMENTO CSS ---
def carica_css(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Carica lo stile esterno
carica_css("stile.css")

# --- AUTENTICAZIONE (Semplificata) ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    st.title("🔒 Accesso Docenti")
    # ... (inserisci logica login) ...
    if st.button("Accedi"): st.session_state["autenticato"] = True; st.rerun()
    st.stop()

# --- SIDEBAR (NAVIGAZIONE) ---
with st.sidebar:
    st.markdown("## 📝 EduCorrect AI")
    menu = st.radio("SEZIONI OPERATIVE:", ["🚀 Generatore Verifiche", "🔍 Scanner Correzioni"])
    st.markdown("---")
    if st.button("🚪 Esci"): st.session_state.clear(); st.rerun()

# --- CORPO PRINCIPALE ---
if menu == "🚀 Generatore Verifiche":
    st.title("🚀 Generatore di Verifiche")
    with st.container():
        # Qui metti i tuoi controlli
        arg = st.text_input("Argomento:")
        if st.button("Genera"): st.success("Generazione...")

elif menu == "🔍 Scanner Correzioni":
    st.title("🔍 Assistente AI alla Correzione")
    metodo = st.radio("Metodo:", ["File", "Foto"], horizontal=True)
    if st.button("Correggi"): st.info("Analisi...")
