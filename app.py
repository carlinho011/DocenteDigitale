import streamlit as st
import os
import json
import re
import time
import io
import jwt  # Ricorda di aggiungere PyJWT al tuo ambiente o requirements.txt
from streamlit_oauth import OAuth2Component
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")
if "tema_scelto" not in st.session_state: 
    st.session_state["tema_scelto"] = "Total Dark"

# --- CARICAMENTO CSS DINAMICO ---
def carica_css(nome_file, tema):
    if os.path.exists(nome_file):
        with open(nome_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style id='css-{time.time()}'>{f.read()}</style>", unsafe_allow_html=True)
    
    if tema == "Total Dark":
        bg = "linear-gradient(-45deg, #020b1e, #0a1931, #0b132b, #001233) !important;"
    else:
        bg = "#f8fafc !important;"
    st.markdown(f"<style>html, body, [data-testid='stAppViewContainer'], .stApp {{ background: {bg} }}</style>", unsafe_allow_html=True)

st.markdown(f"<div id='tema-attivo' class='tema-{st.session_state['tema_scelto'].lower().replace(' ', '-')} style='display:none;'></div>", unsafe_allow_html=True)
carica_css("stile.css", st.session_state["tema_scelto"])

# --- CONTROLLI DI SICUREZZA API E SDK ---
if "GEMINI_KEY" not in st.secrets: 
    st.error("⚠️ Inserisci 'GEMINI_KEY' nei Secrets.")
    st.stop()

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error(f"Errore SDK Gemini: {e}")
    st.stop()

# --- REQUISITI SEGRETI GOOGLE OAUTH ---
config_error = False
for chiave in ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REDIRECT_URI", "DOMINIO_ISTITUZIONALE"]:
    if chiave not in st.secrets:
        st.error(f"⚠️ Manca la chiave '{chiave}' nei tuoi Secrets di Streamlit.")
        config_error = True
if config_error:
    st.stop()

# --- AUTENTICAZIONE GOOGLE OAUTH2 ---
if "autenticato" not in st.session_state: 
    st.session_state["autenticato"] = False
if "info_utente" not in st.session_state:
    st.session_state["info_utente"] = None

CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets["GOOGLE_REDIRECT_URI"]
DOMINIO_SCUOLA = st.secrets["DOMINIO_ISTITUZIONALE"].lower().strip()

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)

if not st.session_state["autenticato"]:
    st.markdown("<div class='box-login'><h2>🔒 Area Riservata Docenti</h2><p>Accedi in modo sicuro con il tuo account istituzionale della scuola.</p>", unsafe_allow_html=True)
    
    result = oauth2.authorize_button(
        name="Accedi con Google",
        redirect_uri=REDIRECT_URI,
        scope="openid profile email",
        key="google_auth",
        use_container_width=True
    )
    
    if result and "token" in result:
        try:
            id_token = result["token"]["id_token"]
            payload = jwt.decode(id_token, options={"verify_signature": False})
            
            email_utente = payload.get("email", "").lower().strip()
            nome_utente = payload.get("name", "Docente")
            
            # Controllo di sicurezza: verifichiamo il finale della mail
            if email_utente.endswith(f"@{DOMINIO_SCUOLA}"):
                st.session_state["autenticato"] = True
                st.session_state["info_utente"] = {"email": email_utente, "nome": nome_utente}
                st.success(f"Benvenuto Prof. {nome_utente}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Accesso negato. Devi utilizzare l'account istituzionale @{DOMINIO_SCUOLA}")
        except Exception as e:
            st.error(f"Errore durante la lettura dei dati di login: {e}")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- GENERATORI PDF REPORTLAB NATIVI ---
def genera_pdf_verifica(argomento, difficolta, testo_corpo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    stile_normale = ParagraphStyle('NormalePDF', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=17)
    stile_intestazione_l = ParagraphStyle('IntestazioneL', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))
    stile_intestazione_r = ParagraphStyle('IntestazioneR', fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=2, textColor=colors.HexColor('#1e293b'))
    stile_titolo_l = ParagraphStyle('TitoloL', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#0f172a'))
    stile_titolo_r = ParagraphStyle('TitoloR', fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=2, textColor=colors.HexColor('#0f172a'))

    dati_tabella = [
        [Paragraph("Istituto Statale di Istruzione Superiore", stile_intestazione_l), Paragraph("Data: ____/____/________", stile_intestazione_r)],
        [Paragraph("Alunno/a: _________________________________________", stile_intestazione_l), Paragraph("Classe: ________ Sez. ____", stile_intestazione_r)],
        [Paragraph(f"Verifica Scritta Valutativa ({difficolta})", stile_titolo_l), Paragraph(f"Materia/Oggetto: {argomento}", stile_titolo_r)]
    ]
    
    tabella = Table(dati_tabella, colWidths=[300, 204])
    tabella.setStyle(TableStyle([
        ('LINEBELOW', (0, 2), (1, 2), 1.5, colors.HexColor('#0f172a')),
        ('BOTTOMPADDING', (0, 0), (1, 2), 8),
        ('TOPPADDING', (0, 0), (1, 2), 8),
        ('VALIGN', (0, 0), (1, 2), 'MIDDLE'),
    ]))
    
    story.append(tabella)
    story.append(Spacer(1, 25))
    
    for linea in testo_corpo.split('\n'):
        linea = linea.strip()
        if linea:
            linea_formattata = re.sub(r'<b>(.*?)</b>', r'<b>\1</b>', linea)
            story.append(Paragraph(linea_formattata, stile_normale))
            story.append(Spacer(1, 8))
        else:
            story.append(Spacer(1, 12))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_soluzioni(argomento, testo_soluzioni):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    stile_normale = ParagraphStyle('SoluzioniNormale', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=17)
    stile_chiave = ParagraphStyle('TitoloChiave', fontName='Helvetica-Bold', fontSize=15, leading=20, textColor=colors.HexColor('#b91c1c'))
    
    story.append(Paragraph(f"🔑 CHIAVE DI CORREZIONE: {argomento}", stile_chiave))
    story.append(Spacer(1, 20))
    
    for linea in testo_soluzioni.split('\n'):
        linea = linea.strip()
        if linea:
            story.append(Paragraph(linea, stile_normale))
            story.append(Spacer(1, 8))
        else:
            story.append(Spacer(1, 12))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_valutazione(nome_alunno, traccia, analisi_testo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    stile_testo = ParagraphStyle('ValNormale', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=16)
    stile_titolo = ParagraphStyle('ValTitolo', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#0f172a'))
    stile_sezione = ParagraphStyle('ValSez', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#1e293b'), spaceBefore=10)
    
    story.append(Paragraph(f"📄 REGISTRO DI VALUTAZIONE — EDULOGIC", stile_titolo))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>Studente/Alunno:</b> {nome_alunno}", stile_testo))
    story.append(Paragraph(f"<b>Traccia/Obiettivo rilevato:</b> {traccia}", stile_testo))
    story.append(Spacer(1, 10))
    story.append(Paragraph("📋 ESITO DELLA CORREZIONE E DETTAGLI:", stile_sezione))
    story.append(Spacer(1, 5))
    
    for linea in analisi_testo.split('\n'):
        linea = linea.strip()
        if linea:
            linea_f = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linea)
            linea_f = re.sub(r'\*(.*?)\*', r'<b>\1</b>', linea_f)
            story.append(Paragraph(linea_f, stile_testo))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 8))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# --- METODI DI RENDERIZZAZIONE INTERFACCIA ---
def renderizza_documento_stampa(argomento, diffic, intestazione_html, domande_html, testo_domande, testo_soluzioni):
    st.markdown("<h3>📋 Anteprima Grafica del Compito</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="foglio-word">
        {intestazione_html}
        <div style='margin-top: 25px;'>{domande_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-family:sans-serif;'>📦 Download File d'Esame Nativi in PDF</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        pdf_alunni = genera_pdf_verifica(argomento, diffic, testo_domande)
        st.download_button(
            label="📄 SCARICA VERIFICA STUDENTI (PDF)",
            data=pdf_alunni,
            file_name=f"Verifica_{argomento.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    with col2:
        pdf_soluzioni = genera_pdf_soluzioni(argomento, testo_soluzioni)
        st.download_button(
            label="🔑 SCARICA CHIAVE DI CORREZIONE (PDF)",
            data=pdf_soluzioni,
            file_name=f"Soluzioni_{argomento.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="secondary",
            use_container_width=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

def mostra_interfaccia_correzione(client, types):
    st.title("🔍 Assistente AI alla Correzione Automatica")
    st.markdown("<p>Carica l'immagine del compito o usa la fotocamera. L'AI rileverà l'alunno, la traccia ed eseguirà la valutazione.</p>", unsafe_allow_html=True)
    
    st.markdown("<h4>📷 Acquisizione Elaborato (Scatta Foto o Carica Immagine)</h4>", unsafe_allow_html=True)
    tab_carica, tab_scatta = st.tabs(["📁 Carica File Immagine", "📸 Usa Fotocamera"])
    file_immagine = None
    
    with tab_carica:
        file_caricato = st.file_uploader("Seleziona l'immagine del compito:", type=["png", "jpg", "jpeg"])
        if file_caricato:
            file_immagine = file_caricato.read()
            st.image(file_immagine, caption="Immagine caricata correttamente", width=300)
            
    with tab_scatta:
        foto_scattata = st.camera_input("Inquadra il foglio del compito e scatta:")
        if foto_scattata:
            file_immagine = foto_scattata.read()
            
    if st.button("🚀 Elabora, Valuta ed Evidenzia Errori", type="primary", use_container_width=True):
        if not file_immagine: 
            st.error("Acquisisci lo svolgimento del compito scattando una foto o caricando un file immagine!")
        else:
            with st.spinner("Il docente AI sta leggendo ed esaminando l'immagine dell'elaborato..."):
                sys_p = (
                    "Sei un profess
