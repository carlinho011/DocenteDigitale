import streamlit as st
import os
from google import genai

# Configurazione Pagina
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# Caricamento Stile
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Gestione Sessione
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# Login
if not st.session_state["autenticato"]:
    st.title("Area Riservata 💜")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome:
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else: st.error("Password o nome errati.")
    st.stop()

# Interfaccia Principale
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Funzioni", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    with st.form("form_viola"):
        col1, col2 = st.columns(2)
        materia = col1.text_input("Materia")
        argomento = col2.text_input("Argomento")
        tipo = st.selectbox("Tipologia Quesiti", ["Vero/Falso", "Scelta multipla", "Risposte aperte", "Miste"])
        diff = st.select_slider("Difficoltà", options=["Facile", "Media", "Difficile"])
        num = st.slider("Numero di domande", 1, 20, 5)
        
        if st.form_submit_button("Genera Verifica"):
            try:
                with st.spinner("Sto scrivendo per te..."):
                    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                    prompt = [f"Crea una verifica di {materia} su {argomento}. Tipo: {tipo}. Difficoltà: {diff}. Numero quesiti: {num}. Inserisci le soluzioni alla fine."]
                    res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                    st.success("Ecco la tua verifica!")
                    st.markdown(res.text)
            except Exception as e:
                st.error(f"Errore API: {e}")

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    st.info("Funzionalità in fase di sviluppo.")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
