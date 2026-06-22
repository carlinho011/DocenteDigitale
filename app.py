import streamlit as st
import os
import io
from google import genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Configurazione Pagina
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# Caricamento CSS (stile Deep Purple)
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session State
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# --- LOGICA LOGIN ---
if not st.session_state["autenticato"]:
    st.title("Area Riservata 💜")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
    st.stop()

# --- FUNZIONI UTILITY ---
def crea_pdf_correzione(dati):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Studente: {dati['nome']}")
    c.drawString(100, 780, f"Voto: {dati['voto']}/10")
    # Qui aggiungeresti il loop per stampare domande e icone ✅/❌
    c.save()
    buffer.seek(0)
    return buffer

# --- APP ---
funzione = st.sidebar.radio("Funzioni", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Crea il tuo compito")
    # ... (il codice di generazione che avevamo già) ...

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica foto/PDF verifica", type=["jpg", "png", "pdf"])
    
    if file and st.button("Avvia Correzione IA"):
        with st.spinner("Analisi in corso..."):
            try:
                client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                
                # Prompt per estrazione dati e correzione
                prompt = """Analizza questo compito. 
                1. Estrai Nome, Data, Classe.
                2. Correggi le risposte e assegna voto in decimi.
                3. Restituisci il risultato in formato JSON con: nome, classe, voto, commento, domande(lista con stato e correzione)."""
                
                # Invia l'immagine a Gemini
                # (Nota: qui useresti l'API per inviare l'immagine come bytes)
                st.success("Compito analizzato!")
                
                # Simulazione dati estratti
                dati_esempio = {"nome": "Mario Rossi", "voto": 8, "commento": "Ottimo lavoro!"}
                
                # Generazione PDF
                pdf_verifica = crea_pdf_correzione(dati_esempio)
                
                st.download_button("Scarica Verifica Corretta", pdf_verifica, "verifica_corretta.pdf")
                st.download_button("Scarica Griglia Valutazione", pdf_verifica, "griglia_voti.pdf")
                
            except Exception as e:
                st.error(f"Errore: {e}")
