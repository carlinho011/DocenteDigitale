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
    st.title("Area Riservata Docente")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome:
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else: st.error("Password errata.")
    st.stop()

# --- LOGICA API (SENZA PREFISSI) ---
def chiama_gemini(prompt, file_part=None):
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
    # Nomi modelli puliti per evitare 404
    for model in ["gemini-2.0-flash", "gemini-1.5-flash"]:
        try:
            contents = [file_part, prompt] if file_part else [prompt]
            return client.models.generate_content(model=model, contents=contents)
        except Exception as e:
            # Continua se la risorsa non è trovata o la quota è esaurita
            if "404" in str(e) or "429" in str(e): continue
            raise e
    raise Exception("Nessun modello disponibile o quota esaurita.")

# --- FUNZIONI PDF ---
def genera_pdf_base(titolo, contenuto):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595, 842))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, titolo)
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, contenuto[:100] + "...")
    c.save()
    buffer.seek(0)
    return buffer

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
                st.session_state["risultato"] = res.text
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
                f_part = types.Part.from_bytes(data=file.getvalue(), mime_type=mime)
                res = chiama_gemini("Analizza il compito, correggi, assegna voto e commento.", f_part)
                st.success("Correzione eseguita!")
                st.download_button("Scarica Verifica Corretta", genera_pdf_base("Verifica Corretta", res.text), "verifica.pdf")
                st.download_button("Scarica Griglia", genera_pdf_base("Griglia Voti", "Analisi punteggi..."), "griglia.pdf")
            except Exception as e: st.error(f"Errore: {e}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
