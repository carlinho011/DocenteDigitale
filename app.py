import streamlit as st
import os
import io
from google import genai
from reportlab.pdfgen import canvas

# Configurazione Pagina
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# --- CARICAMENTO CSS ---
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- SESSIONE ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# --- LOGIN ---
if not st.session_state["autenticato"]:
    st.title("Area Riservata Docente")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome:
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
    st.stop()

# --- SIDEBAR (DEFINIZIONE FUNZIONE) ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

# --- LOGICA APP ---
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
                client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                prompt = [f"Crea una verifica di {materia} su {argomento}. Tipo: {tipo}. Difficoltà: {diff}. Numero quesiti: {num}."]
                res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                st.markdown(res.text)
            except Exception as e:
                st.error(f"Errore: {e}")

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    st.info("Funzionalità in fase di sviluppo.")
    # Qui aggiungeremo in futuro la logica PDF per evitare conflitti

# Logout
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
