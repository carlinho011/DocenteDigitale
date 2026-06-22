import streamlit as st
from google import genai

# Configurazione Pagina
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="centered")

# Caricamento CSS
def carica_css():
    try:
        with open("stile.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except: pass
carica_css()

# Session State
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# --- LOGICA LOGIN ---
if not st.session_state["autenticato"]:
    st.markdown("## 👋 Benvenuto Prof!")
    st.write("Inserisci la password per iniziare la magia.")
    nome = st.text_input("Come ti chiami?")
    pw = st.text_input("Password:", type="password")
    if st.button("Entra nell'area"):
        if pw == "MATTEI" and nome:
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else: st.error("Password errata o nome mancante!")
    st.stop()

# --- APP ---
st.sidebar.title(f"Ciao Prof. {st.session_state['nome_docente']}!")
funzione = st.sidebar.radio("Cosa facciamo oggi?", ["🚀 Genera Compito", "🔍 Correggi"])

if funzione == "🚀 Genera Compito":
    st.title("🚀 Generiamo qualcosa di unico!")
    with st.form("gen_form"):
        materia = st.text_input("Materia")
        argomento = st.text_input("Argomento")
        tipo = st.selectbox("Tipo domande", ["Vero/Falso", "Scelta multipla", "Aperte", "Miste"])
        num = st.slider("Quante domande?", 1, 10, 5)
        if st.form_submit_button("Crea verifica"):
            with st.spinner("La mia IA sta scrivendo per te..."):
                try:
                    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                    prompt = f"Crea una verifica di {materia} su {argomento}. Tipo: {tipo}. Numero domande: {num}. Inserisci le soluzioni alla fine."
                    res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                    st.success("Ecco la tua verifica!")
                    st.markdown(res.text)
                except Exception as e: st.error(f"Errore: {e}")

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    st.info("Funzionalità in fase di sviluppo.")

if st.sidebar.button("Esci"):
    st.session_state.clear()
    st.rerun()
