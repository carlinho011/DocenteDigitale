import streamlit as st
import os
import io
import time
from google import genai
from google.genai import types
from reportlab.pdfgen import canvas

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# --- INIZIALIZZAZIONE ---
try:
    # Cerchiamo di inizializzare in modo standard
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error(f"Errore inizializzazione: {e}")
    st.stop()

# --- LOGICA API ---
def chiama_gemini(prompt, file_bytes=None, mime_type=None):
    # La lista dei nomi validi che l'API accetta spesso senza il prefisso 'models/'
    # Se il tuo account è limitato, prova a cambiare questo nome
    model_name = "gemini-1.5-flash"
    
    contents = []
    if file_bytes and mime_type:
        contents.append(types.Part.from_bytes(data=file_bytes, mime_type=mime_type))
    contents.append(prompt)
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents
        )
        return response.text
    except Exception as e:
        # Se fallisce, mostriamo l'errore completo per capire cosa succede
        return f"ERRORE API: {str(e)}"

# --- UI (SESSIONE E LOGIN) ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

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

# --- UI INTERFACCIA ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    if st.button("Genera"):
        with st.spinner("Generazione..."):
            res = chiama_gemini(f"Crea una verifica di {materia} su {argomento}.")
            st.markdown(res)

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica File", type=["jpg", "png", "pdf"])
    if file and st.button("Analizza"):
        with st.spinner("Analisi..."):
            mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
            res = chiama_gemini("Correggi questo compito.", file.getvalue(), mime)
            st.markdown(res)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# --- DIAGNOSTICA (SOTTO IL CODICE) ---
if st.sidebar.checkbox("Mostra Diagnostica API"):
    try:
        models = client.models.list()
        st.write("Modelli disponibili nel tuo account:")
        for m in models:
            st.write(f"- {m.name}")
    except Exception as e:
        st.error(f"Non riesco a leggere i modelli: {e}")
