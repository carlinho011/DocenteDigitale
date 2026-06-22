import streamlit as st
import os
from google import genai

# Setup
st.set_page_config(page_title="EduCorrect", page_icon="📝")

# Caricamento CSS
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sessione
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# Login
if not st.session_state["autenticato"]:
    st.title("Area Riservata Docenti")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
    st.stop()

# App
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
            with st.spinner("Elaborazione in corso..."):
                client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                prompt = f"Crea una verifica di {materia} su {argomento}. Tipo: {tipo}. Difficoltà: {diff}. Numero quesiti: {num}. Inserisci le soluzioni alla fine."
                res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                st.markdown(res.text)

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    st.info("Funzionalità in fase di sviluppo.")
