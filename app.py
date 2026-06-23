import streamlit as st
import io
import re
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

# --- CONFIGURAZIONE GRAFICA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

st.markdown("""
    <style>
    /* Stile "Foglio Bianco" con ombra elegante */
    .foglio-bianco {
        background-color: white;
        color: #333;
        padding: 50px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 8px;
        margin-bottom: 30px;
        font-family: 'Helvetica', sans-serif;
        line-height: 1.6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNZIONE PDF CON FORMATTAZIONE TIPOGRAFICA ---
def genera_pdf_grafico(titolo, testo_md):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Stile personalizzato per il testo
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=10
    )
    
    story = [
        Paragraph(titolo, styles['Title']),
        Spacer(1, 24)
    ]
    
    # Processo di formattazione
    for riga in testo_md.split('\n'):
        riga = riga.strip()
        if not riga: continue
        
        if riga.startswith('#'):
            story.append(Paragraph(riga.replace('#', '').strip(), styles['Heading1']))
        elif riga.startswith(('-', '*')):
            story.append(Paragraph("• " + riga.replace('-', '').replace('*', '').strip(), body_style))
        else:
            riga = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', riga)
            story.append(Paragraph(riga, body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- LOGICA APP (Identica alla precedente, ma ora con la nuova funzione grafica) ---
# [La logica di autenticazione e navigazione rimane invariata]
# Usa genera_pdf_grafico("Lezione", st.session_state["dispensa"]) invece della vecchia funzione
