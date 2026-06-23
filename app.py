import streamlit as st
import io
import re
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
        background-color: white; color: black; padding: 30px; 
        border: 1px solid #ddd; margin-bottom: 20px; border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE API ---
try:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Errore API: {e}")
    st.stop()

# --- FUNZIONE PDF (FORMATTAZIONE NATIVA) ---
def genera_pdf_formattato(titolo, testo_md):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Pulizia Markdown -> HTML compatibile con ReportLab
    testo_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', testo_md) # Grassetto
    testo_html = re.sub(r'\n- (.*?)', r'<br/>• \1', testo_html)   # Liste
    testo_html = testo_html.replace('\n', '<br/>')               # A capo
    
    story = [Paragraph(f"<h1>{titolo}</h1>", styles['Title']), Spacer(1, 12)]
    story.append(Paragraph(testo_html, styles['Normal']))
    
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

# --- INTERFACCIA ---
st.sidebar.title(f"Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Generatore Didattico")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    
    if st.button("Genera Materiale e Verifica"):
        with st.spinner("Creazione in corso..."):
            st.session_state["dispensa"] = model.generate_content(f"Scrivi una breve lezione su {argomento}").text
            st.session_state["verifica"] = model.generate_content(f"Crea 5 domande su {argomento}").text

    if "dispensa" in st.session_state:
        st.subheader("Anteprima")
        with st.container():
            st.markdown(f'<div class="foglio-bianco">{st.session_state["dispensa"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="foglio-bianco">{st.session_state["verifica"]}</div>', unsafe_allow_html=True)
        
        st.write("### Scarica i file")
        c1, c2 = st.columns(2)
        c1.download_button("📥 Scarica Lezione", genera_pdf_formattato("Lezione", st.session_state["dispensa"]), "lezione.pdf")
        c2.download_button("📥 Scarica Verifica", genera_pdf_formattato("Verifica", st.session_state["verifica"]), "verifica.pdf")

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica File", type=["pdf"])
    if file and st.button("Analizza"):
        res = model.generate_content("Correggi questo compito e dai un voto").text
        st.markdown(f'<div class="foglio-bianco">{res}</div>', unsafe_allow_html=True)
        st.download_button("Scarica Correzione", genera_pdf_formattato("Correzione", res), "correzione.pdf")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
