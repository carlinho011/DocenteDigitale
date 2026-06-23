import streamlit as st
import os
import io
import google.generativeai as genai
from reportlab.pdfgen import canvas

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# --- CARICAMENTO CSS ---
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE API ---
try:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    
    # Trova un modello valido automaticamente
    def get_available_model():
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        return None

    model = get_available_model()
    if model is None:
        st.error("Nessun modello disponibile trovato con questa API Key.")
        st.stop()
except Exception as e:
    st.error(f"Errore di configurazione API: {e}")
    st.stop()
# --- FUNZIONI PDF ---
def genera_pdf_base(titolo, contenuto):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595, 842))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, titolo)
    c.setFont("Helvetica", 12)
    # Gestione semplice del testo nel PDF
    y = 770
    for linea in contenuto.split('\n'):
        c.drawString(50, y, linea)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

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
        else: st.error("Password errata.")
    st.stop()

# --- INTERFACCIA ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    num = st.slider("Numero di domande", 1, 20, 5)
    
    if st.button("Genera"):
        with st.spinner("Generazione in corso..."):
            # Generazione separata
            st.session_state["dispensa"] = model.generate_content(f"Crea un testo informativo su {argomento} per {materia}").text
            st.session_state["verifica"] = model.generate_content(f"Crea una verifica di {num} domande su {argomento}").text

    if "dispensa" in st.session_state:
        st.subheader("Anteprima Lezione")
        st.markdown(st.session_state["dispensa"])
        st.subheader("Anteprima Verifica")
        st.markdown(st.session_state["verifica"])
        
        # Due tasti download separati
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Scarica Lezione PDF", genera_pdf_base("Lezione", st.session_state["dispensa"]), "lezione.pdf")
        with col2:
            st.download_button("Scarica Verifica PDF", genera_pdf_base("Verifica", st.session_state["verifica"]), "verifica.pdf")

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica File", type=["jpg", "png", "pdf"])
    if file and st.button("Analizza"):
        with st.spinner("Analisi IA in corso..."):
            res = model.generate_content("Analizza il compito, correggi, assegna voto e commento.").text
            st.success("Correzione eseguita!")
            st.markdown(res)
            st.download_button("Scarica Verifica Corretta", genera_pdf_base("Verifica Corretta", res), "verifica_corretta.pdf")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
