import streamlit as st, json
from google import genai
from google.genai import types

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# --- GESTIONE AUTH ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state: st.session_state["nome_docente"] = ""

# --- SCHERMATA LOGIN ---
if not st.session_state["autenticato"]:
    st.markdown("<div style='max-width: 400px; margin: 80px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.title("🔒 Accesso Docente")
    
    nome = st.text_input("Inserisci il tuo Nome:")
    pw = st.text_input("Password:", type="password")
    
    if st.button("Entra"):
        if pw == "MATTEI" and nome.strip() != "":
            st.session_state["autenticato"] = True
            st.session_state["nome_docente"] = nome
            st.rerun()
        elif pw != "MATTEI":
            st.error("❌ Password errata.")
        else:
            st.warning("⚠️ Inserisci il tuo nome per procedere.")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- APPLICAZIONE PRINCIPALE (dopo login) ---
st.sidebar.markdown(f"### Benvenuto, Prof. {st.session_state['nome_docente']}")
if st.sidebar.button("Logout"):
    st.session_state["autenticato"] = False
    st.rerun()

st.title("🚀 EduCorrect AI")
st.write("Puoi procedere con la generazione delle verifiche.")

# Qui continua la tua logica (Genera Verifica / Scansiona)
