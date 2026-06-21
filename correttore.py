import streamlit as st
import io, re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def genera_pdf_verifica(argomento, difficolta, testo_corpo):
    """Genera il file PDF nativo con la formattazione grafica per gli studenti."""
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
    
    # FISSO: Inserite le larghezze esplicite delle colonne per evitare il SyntaxError
    tabella = Table(dati_tabella, colWidths=[370, 170])
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
            linea_formattata = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linea)
            linea_formattata = re.sub(r'\*(.*?)\*', r'<b>\1</b>', linea_formattata)
            story.append(Paragraph(linea_formattata, stile_normale))
            story.append(Spacer(1, 8))
        else:
            story.append(Spacer(1, 12))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_soluzioni(argomento, testo_soluzioni):
    """Genera il file PDF nativo con la chiave di correzione per il docente."""
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
            linea_formattata = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linea)
            linea_formattata = re.sub(r'\*(.*?)\*', r'<b>\1</b>', linea_formattata)
            story.append(Paragraph(linea_formattata, stile_normale))
            story.append(Spacer(1, 8))
        else:
            story.append(Spacer(1, 12))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def renderizza_documento_stampa(argomento, diffic, intestazione_html, domande_html, testo_domande, testo_soluzioni):
    """Mostra la bellissima anteprima a schermo ed espone i pulsanti per il download immediato dei PDF."""
    st.markdown("<br><h3 class='titolo-anteprima'>📋 Anteprima Grafica del Compito</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="foglio-word">
        {intestazione_html}
        <div style='margin-top: 15px;'>{domande_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
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


# ==========================================================================
# 🔍 SEZIONE: ASSISTENTE CORREZIONE MULTIMODALE CON EXPORT PDF
# ==========================================================================

def genera_pdf_valutazione(nome_alunno, traccia, analisi_testo):
    """Genera un PDF formattato con i risultati della correzione e il voto."""
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
    story.append(Paragraph(f"<b>Traccia/Obiettivo:</b> {traccia}", stile_testo))
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

def mostra_interfaccia_correzione(client, types):
    """Gestisce l'interfaccia di acquisizione (foto/caricamento) e correzione dei compiti."""
    st.title("🔍 Assistente AI alla Correzione")
    st.markdown("<p style='color: #cbd5e1 !important;'>Compila i dati dell'alunno, acquisisci lo svolgimento tramite fotocamera o file e ricevi la correzione automatica.</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
    nome_alunno = st.text_input("Nome e Cognome dell'Alunno:", placeholder="Es. Mario Rossi")
    traccia = st.text_input("Traccia dell'Esercizio o Testo della Domanda:", placeholder="Es. Spiega la teoria della relatività o risolvi il quesito...")
    st.markdown("</div>", unsafe_allow_html=True)
    
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
        if not nome_alunno:
            st.error("Inserisci il nome dell'alunno prima di avviare l'analisi!")
        elif not traccia:
            st.error("Inserisci il testo della traccia originaria per permettere il confronto!")
        elif not file_immagine:
            st.error("Acquisisci lo svolgimento del compito scattando una foto o caricando un file immagine!")
        else:
            with st.spinner("Il docente AI sta analizzando l'immagine dell'elaborato..."):
                sys_p = (
                    "Sei un professor italiano severo ma giusto. Analizza l'immagine dell'elaborato dello studente fornito. "
                    "Trova gli errori ortografici, logici o matematici e commentali dettagliatamente. "
