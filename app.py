import streamlit as st
import os
import io
from google import genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Configurazione Pagina
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# --- CSS E LOGIN ---
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    st.title("Area Riservata 💜")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome:
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
    st.stop()

# --- FUNZIONI PDF ---
def genera_pdf_verifica(testo_correzione):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(50, 800, "VERIFICA CORRETTA")
    c.drawString(50, 780, testo_correzione) # Qui l'IA scriverà i dettagli
    c.save()
    buffer.seek(0)
    return buffer

def genera_griglia_voti():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(50, 800, "GRIGLIA DI VALUTAZIONE")
    c.save()
    buffer.seek(0)
    return buffer

# --- SIDEBAR E APP ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    # ... (il codice di generazione resta invariato) ...
    pass

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    
    scelta = st.radio("Sorgente:", ["Carica File", "Scatta Foto"])
    file = st.camera_input("Scatta") if scelta == "Scatta Foto" else st.file_uploader("Carica PDF/Foto", type=["jpg", "png", "pdf"])

    if file and st.button("Analizza e Correggi"):
        with st.spinner("L'IA sta analizzando il compito..."):
            try:
                client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                img_bytes = file.getvalue()
                
                prompt = "Analizza il compito. Estrai Nome, Data, Classe. Correggi le risposte (segna ✅ o ❌). Calcola voto 1/10 e scrivi un commento. Restituisci tutto per la creazione di un PDF."
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[{"mime_type": "image/jpeg", "data": img_bytes}, prompt]
                )
                
                st.success("Correzione completata!")
                
                # Download dei 2 file diversi
                st.download_button("Scarica Verifica Corretta", genera_pdf_verifica(response.text), "verifica_corretta.pdf")
                st.download_button("Scarica Griglia Voti", genera_griglia_voti(), "griglia_voti.pdf")
                
            except Exception as e:
                st.error(f"Errore durante l'analisi: {e}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
