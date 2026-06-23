import streamlit as st
import os
import io
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# --- CSS PER ANTEPRIMA A FOGLIO BIANCO ---
st.markdown("""
    <style>
    .foglio-bianco {
        background-color: white;
        color: black;
        padding: 40px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE API ---
try:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    def get_model():
        return genai.GenerativeModel('gemini-1.5-flash')
    model = get_model()
except Exception as e:
    st.error(f"Errore API: {e}")
    st.stop()

# --- FUNZIONI PDF ---
def genera_pdf_avanzato(titolo, contenuto):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"<b>{titolo}</b>", styles['Title']), Spacer(1, 12)]
    
    # Sostituisce i ritorni a capo con i tag HTML per il PDF
    testo_formattato = contenuto.replace('\n', '<br/>')
    story.append(Paragraph(testo_formattato, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- LOGICA APPLICAZIONE ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    st.title("Area Riservata Docente")
    nome = st.text_input("Nome:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else: st.error("Password errata.")
    st.stop()

st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Generatore Didattico")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    
    if st.button("Genera Materiale e Verifica"):
        with st.spinner("Creazione in corso..."):
            # Generazione separata
            dispensa = model.generate_content(f"Scrivi una lezione sintetica su {argomento}").text
            verifica = model.generate_content(f"Crea 5 domande di verifica su {argomento} basate su: {dispensa}").text
            
            st.session_state["dispensa"] = dispensa
            st.session_state["verifica"] = verifica

    if "dispensa" in st.session_state:
        # Area Anteprima
        st.subheader("Anteprima")
        with st.container():
            st.markdown(f'<div class="foglio-bianco">{st.session_state["dispensa"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="foglio-bianco">{st.session_state["verifica"]}</div>', unsafe_allow_html=True)
        
        # Download
        st.write("### Scarica i file")
        c1, c2 = st.columns(2)
        c1.download_button("📥 Scarica Lezione", genera_pdf_avanzato("Lezione", st.session_state["dispensa"]), "lezione.pdf")
        c2.download_button("📥 Scarica Verifica", genera_pdf_avanzato("Verifica", st.session_state["verifica"]), "verifica.pdf")

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica", type=["pdf"])
    if file and st.button("Analizza"):
        res = model.generate_content("Correggi questo compito e dai un voto").text
        st.markdown(f'<div class="foglio-bianco">{res}</div>', unsafe_allow_html=True)
        st.download_button("Scarica Correzione", genera_pdf_avanzato("Correzione", res), "correzione.pdf")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
