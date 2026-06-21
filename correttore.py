import streamlit as st
import io, re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
    
    tabella = Table(dati_tabella, colWidths=[350, 154])
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
    st.markdown("<br><h3 style='color: #f8fafc;'>📋 Anteprima Grafica del Compito</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="foglio-word">
        {intestazione_html}
        <div style='margin-top: 15px;'>{domande_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: rgba(255,255,255,0.03); padding: 30px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color:#f8fafc; font-family:sans-serif;'>📦 Download File d'Esame Nativi in PDF</h4>", unsafe_allow_html=True)
    
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
    st.title("🔍 Assistente AI alla Correzione")
    st.markdown("<p style='color: #94a3b8; margin-top: -15px;'>Incolla il testo del compito consegnato dall'alunno per ricevere l'analisi degli errori e la proposta di voto.</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='background-color: rgba(255,255,255,0.02); padding: 25px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;'>", unsafe_allow_html=True)
    traccia = st.text_input("Traccia dell'Esercizio o Testo della Domanda:", placeholder="Es. Descrivi il concetto di inconscio per Sigmund Freud...")
    testo_alunno = st.text_area("Trascrizione dello Svolgimento dell'Alunno:", height=220, placeholder="Incolla qui la risposta scritta dallo studente...")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("🚀 Elabora ed Evidenzia Errori", type="primary"):
        if not traccia or not testo_alunno:
            st.error("Compila sia la traccia dell'esercizio che lo svolgimento scritto dall'alunno!")
        else:
            with st.spinner("Il docente AI sta analizzando il compito in base ai criteri ministeriali..."):
                sys_p = "Sei un professore italiano severo ma giusto. Analizza il compito, evidenzia gli errori in modo professionale e fornisci un voto finale in decimi (es. 6½, 7, 8+)."
                user_p = f"Traccia: {traccia}\nSvolgimento Alunno: {testo_alunno}\n\nFornisci errori dettagliati e voto."
                
                try:
                    risp = client.models.generate_content(model='gemini-2.5-flash', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.3})
                    st.session_state["analisi_correzione"] = risp.text
                except Exception as e:
                    st.error(f"Errore di rete durante la correzione: {e}")
                    
    if "analisi_correzione" in st.session_state:
        st.markdown("<br><h3 style='color: #f8fafc;'>📝 Registro di Valutazione AI</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="box-valutazione">
            {st.session_state["analisi_correzione"].replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
