import streamlit as st
import io
import re
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

st.markdown("""
    <style>
    .foglio-bianco { background-color: white; color: black; padding: 30px; border: 1px solid #ddd; margin-bottom: 20px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE API ---
genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNZIONE PDF MIGLIORATA ---
def genera_pdf_formattato(titolo, testo_md):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"<b>{titolo}</b>", styles['Title']), Spacer(1, 12)]
    
    # Analisi riga per riga per mantenere la formattazione Markdown
    for riga in testo_md.split('\n'):
        riga = riga.strip()
        if not riga:
            story.append(Spacer(1, 6))
            continue
            
        # Titoli (Markdown #)
        if riga.startswith('#'):
            livello = len(riga.split(' ')[0])
            testo = riga.replace('#', '').strip()
            style = styles[f'Heading{min(livello, 3)}']
            story.append(Paragraph(testo, style))
        # Elenchi puntati
        elif riga.startswith(('-', '*')):
            testo = '• ' + riga.replace('-', '').replace('*', '').strip()
            story.append(Paragraph(testo, styles['Normal']))
        # Grassetto (**text**)
        else:
            testo = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', riga)
            story.append(Paragraph(testo, styles['Normal']))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- LOGICA APP ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    st.title("Area Riservata Docente")
    if st.text_input("Password:", type="password") == "MATTEI":
        st.session_state["autenticato"] = True
        st.rerun()
    st.stop()

# --- INTERFACCIA ---
funzione = st.sidebar.radio("Navigazione", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Generatore Didattico")
    argomento = st.text_input("Argomento")
    if st.button("Genera"):
        st.session_state["dispensa"] = model.generate_content(f"Scrivi una lezione su {argomento} in Markdown").text
        st.session_state["verifica"] = model.generate_content(f"Crea 5 domande su {argomento} in Markdown").text

    if "dispensa" in st.session_state:
        st.markdown(f'<div class="foglio-bianco">{st.session_state["dispensa"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="foglio-bianco">{st.session_state["verifica"]}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.download_button("📥 Scarica Lezione", genera_pdf_formattato("Lezione", st.session_state["dispensa"]), "lezione.pdf")
        c2.download_button("📥 Scarica Verifica", genera_pdf_formattato("Verifica", st.session_state["verifica"]), "verifica.pdf")

elif funzione == "🔍 Correggi":
    file = st.file_uploader("Carica", type=["pdf"])
    if file and st.button("Analizza"):
        res = model.generate_content("Correggi il compito").text
        st.markdown(f'<div class="foglio-bianco">{res}</div>', unsafe_allow_html=True)
        st.download_button("Scarica Correzione", genera_pdf_formattato("Correzione", res), "correzione.pdf")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
