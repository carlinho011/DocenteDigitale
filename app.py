import streamlit as st
import os
import io
from google import genai
from google.genai import types
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
    st.title("Area Riservata Docenti")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome:
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else:
            st.error("Accesso negato.")
    st.stop()

# --- FUNZIONI PDF ---
def genera_pdf_verifica(testo):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=os.path.abspath("A4")) # A4 standard
    c.drawString(50, 800, "VERIFICA CORRETTA (Esportazione)")
    c.drawString(50, 780, testo[:200] + "...") 
    c.save()
    buffer.seek(0)
    return buffer

# --- SIDEBAR E NAVIGAZIONE ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

# --- LOGICA: GENERA VERIFICA ---
if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    tipo = st.selectbox("Tipologia", ["Vero/Falso", "Scelta multipla", "Aperte", "Miste"])
    diff = st.select_slider("Difficoltà", options=["Facile", "Media", "Difficile"])
    num = st.slider("Numero di domande", 1, 20, 5)
    
    if st.button("Genera"):
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
            prompt = f"Crea una verifica di {materia} su {argomento}. Tipo: {tipo}. Difficoltà: {diff}. Numero: {num}."
            res = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt])
            st.session_state["risultato_gen"] = res.text
            st.success("Generazione completata!")
        except Exception as e:
            st.error(f"Errore: {e}")

    if "risultato_gen" in st.session_state:
        st.markdown(st.session_state["risultato_gen"])

# --- LOGICA: CORREGGI ---
elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    scelta = st.radio("Sorgente:", ["Carica File", "Scatta Foto"])
    file = st.camera_input("Scatta") if scelta == "Scatta Foto" else st.file_uploader("Carica", type=["jpg", "png", "pdf"])

    if file and st.button("Analizza e Correggi"):
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
            mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
            file_part = types.Part.from_bytes(data=file.getvalue(), mime_type=mime)
            
            prompt = "Analizza il compito. Estrai Nome, Classe, Voto e correggi le domande (✅/❌)."
            res = client.models.generate_content(model="gemini-2.0-flash", contents=[file_part, prompt])
            
            st.success("Correzione pronta!")
            st.download_button("Scarica Verifica Corretta", genera_pdf_verifica(res.text), "verifica.pdf")
            st.download_button("Scarica Griglia Voti", genera_pdf_verifica("Griglia Voti..."), "griglia.pdf")
        except Exception as e:
            st.error(f"Errore analisi: {e}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
