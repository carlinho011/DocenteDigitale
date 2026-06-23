import streamlit as st
import io
import markdown # Assicurati di aver installato: pip install markdown
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# CSS per l'effetto "Foglio Bianco" nell'anteprima
st.markdown("""
    <style>
    .foglio-bianco {
        background-color: white; color: black; padding: 30px; 
        border: 1px solid #ddd; margin-bottom: 20px; border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNZIONE PDF CON FORMATTAZIONE MANTENUTA ---
def genera_pdf_formattato(titolo, testo_md):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titolo
    story.append(Paragraph(titolo, styles['Title']))
    story.append(Spacer(1, 12))
    
    # Converte Markdown in HTML che ReportLab può interpretare
    html_testo = markdown.markdown(testo_md)
    # Pulizia base per compatibilità ReportLab
    html_testo = html_testo.replace('<ul>', '').replace('</ul>', '').replace('<li>', '• ').replace('</li>', '<br/>')
    
    story.append(Paragraph(html_testo, styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- LOGICA PRINCIPALE (Estratto) ---
# ... [Logica di accesso rimasta invariata] ...

if funzione == "🚀 Genera Verifica":
    # ... [Input materia/argomento] ...
    
    if st.button("Genera"):
        # Chiamate IA
        st.session_state["dispensa"] = model.generate_content(f"Scrivi una lezione su {argomento} in formato Markdown.").text
        st.session_state["verifica"] = model.generate_content(f"Crea una verifica su {argomento} in formato Markdown.").text

    if "dispensa" in st.session_state:
        # Anteprima su foglio bianco
        st.subheader("Anteprima Lezione")
        st.markdown(f'<div class="foglio-bianco">{st.session_state["dispensa"]}</div>', unsafe_allow_html=True)
        
        st.subheader("Anteprima Verifica")
        st.markdown(f'<div class="foglio-bianco">{st.session_state["verifica"]}</div>', unsafe_allow_html=True)
        
        # Tasti Download affiancati
        c1, c2 = st.columns(2)
        c1.download_button("📥 Scarica Lezione", genera_pdf_formattato("Lezione", st.session_state["dispensa"]), "lezione.pdf")
        c2.download_button("📥 Scarica Verifica", genera_pdf_formattato("Verifica", st.session_state["verifica"]), "verifica.pdf")
