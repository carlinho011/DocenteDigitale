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

    def get_first_available_model():
        """Trova il primo modello valido disponibile nel tuo account."""
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        raise Exception("Nessun modello trovato nel tuo account.")

    model = get_first_available_model()
except Exception as e:
    st.error(f"Errore di configurazione API: {e}")
    st.stop()

# --- LOGICA API ---
def chiama_gemini(prompt, file_data=None, mime_type=None):
    if file_data and mime_type:
        response = model.generate_content([prompt, {"mime_type": mime_type, "data": file_data}])
    else:
        response = model.generate_content(prompt)
    return response.text

# --- FUNZIONI PDF ---
def genera_pdf_base(titolo, contenuto):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595, 842))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, titolo)
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, contenuto[:80] + "...")
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
    tipo = st.selectbox("Tipologia", ["Vero/Falso", "Scelta multipla", "Aperte", "Miste"])
    diff = st.select_slider("Difficoltà", ["Facile", "Media", "Difficile"])
    num = st.slider("Numero di domande", 1, 20, 5)
    
    if st.button("Genera"):
        with st.spinner("Generazione in corso..."):
            try:
                res = chiama_gemini(f"Crea una verifica di {materia} su {argomento}. Tipo: {tipo}. Difficoltà: {diff}. Numero: {num}.")
                st.session_state["risultato"] = res
                st.success("Pronto!")
            except Exception as e: st.error(f"Errore API: {e}")
    if "risultato" in st.session_state: st.markdown(st.session_state["risultato"])

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica File", type=["jpg", "png", "pdf"])
    if file and st.button("Analizza"):
        with st.spinner("Analisi IA in corso..."):
            try:
                mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                res = chiama_gemini("Analizza il compito, correggi, assegna voto e commento.", file.getvalue(), mime)
                st.success("Correzione eseguita!")
                st.markdown(res)
                st.download_button("Scarica Verifica Corretta", genera_pdf_base("Verifica Corretta", res), "verifica.pdf")
            except Exception as e: st.error(f"Errore: {e}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
