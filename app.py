import streamlit as st
import os
import io
import time
from google import genai
from google.genai import types
from reportlab.pdfgen import canvas

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# Inizializza il client usando la chiave da secrets.toml
try:
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error(f"Errore caricamento chiave API: {e}")
    st.stop()

# --- LOGICA API ---
def chiama_gemini(prompt, file_bytes=None, mime_type=None):
    # Usiamo gemini-1.5-flash (il più stabile)
    model_name = "gemini-1.5-flash"
    
    contents = []
    if file_bytes and mime_type:
        contents.append(types.Part.from_bytes(data=file_bytes, mime_type=mime_type))
    contents.append(prompt)
    
    # Pausa di sicurezza per i limiti di quota
    time.sleep(1)
    
    response = client.models.generate_content(
        model=model_name,
        contents=contents
    )
    return response.text

# --- FUNZIONI PDF ---
def genera_pdf_base(titolo, contenuto):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595, 842))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, titolo)
    c.setFont("Helvetica", 12)
    # Gestione testo lungo
    c.drawString(50, 770, contenuto[:80] + "...")
    c.save()
    buffer.seek(0)
    return buffer

# --- SESSIONE ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# --- UI LOGIN ---
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

# --- INTERFACCIA PRINCIPALE ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    tipo = st.selectbox("Tipologia", ["Vero/Falso", "Scelta multipla", "Aperte"])
    num = st.slider("Numero di domande", 1, 10, 5)
    
    if st.button("Genera"):
        with st.spinner("Generazione in corso..."):
            try:
                res = chiama_gemini(f"Crea una verifica di {materia} su {argomento}. Tipo: {tipo}. Numero: {num}.")
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
                res = chiama_gemini("Analizza il compito e correggi.", file.getvalue(), mime)
                st.success("Correzione eseguita!")
                st.markdown(res)
                st.download_button("Scarica PDF", genera_pdf_base("Correzione", res), "correzione.pdf")
            except Exception as e: st.error(f"Errore: {e}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
