import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def genera_pdf_verifica(argomento, difficolta, testo_corpo):
    """Genera il file PDF nativo della verifica con intestazione ministeriale."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Stili personalizzati per il PDF
    stile_normale = ParagraphStyle('NormalePDF', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=16)
    stile_intestazione_l = ParagraphStyle('IntestazioneL', fontName='Helvetica-Bold', fontSize=10, leading=14)
    stile_intestazione_r = ParagraphStyle('IntestazioneR', fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=2)
    stile_titolo_l = ParagraphStyle('TitoloL', fontName='Helvetica-Bold', fontSize=12, leading=16)
    stile_titolo_r = ParagraphStyle('TitoloR', fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=2)

    # Costruzione della tabella ministeriale in ReportLab
    dati_tabella = [
        [Paragraph("Istituto Superiori", stile_intestazione_l), Paragraph("Data: ____/____/________", stile_intestazione_r)],
        [Paragraph("Alunno/a: ___________________________", stile_intestazione_l), Paragraph("Classe: ____ Sez. __", stile_intestazione_r)],
        [Paragraph(f"Verifica scritta ({difficolta})", stile_titolo_l), Paragraph(f"Oggetto: {argomento}", stile_titolo_r)]
    ]
    
    tabella = Table(dati_tabella, colWidths=[300, 204])
    tabella.setStyle(TableStyle([
        ('LINEBELOW', (0, 2), (1, 2), 1.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (1, 2), 6),
        ('TOPPADDING', (0, 0), (1, 2), 6),
        ('VALIGN', (0, 0), (1, 2), 'MIDDLE'),
    ]))
    
    story.append(tabella)
    story.append(Spacer(1, 20))
    
    # Pulizia del testo e conversione dei newline in paragrafi
    for linea in testo_corpo.split('\n'):
        linea = linea.strip()
        if linea:
            # Sostituzione base dei grassetti markdown per ReportLab (usa <b>)
            linea_formattata = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linea)
            linea_formattata = re.sub(r'\*(.*?)\*', r'<b>\1</b>', linea_formattata)
            story.append(Paragraph(linea_formattata, stile_normale))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 10))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_soluzioni(argomento, testo_soluzioni):
    """Genera il file PDF nativo con la chiave di correzione senza anteprima a schermo."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    stile_normale = ParagraphStyle('SoluzioniNormale', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=16)
    stile_chiave = ParagraphStyle('TitoloChiave', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#bf1515'))
    
    story.append(Paragraph(f"🔑 CHIAVE DI CORREZIONE: {argomento}", stile_chiave))
    story.append(Spacer(1, 15))
    
    for linea in testo_soluzioni.split('\n'):
        linea = linea.strip()
        if linea:
            linea_formattata = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linea)
            linea_formattata = re.sub(r'\*(.*?)\*', r'<b>\1</b>', linea_formattata)
            story.append(Paragraph(linea_formattata, stile_normale))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 10))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

import re

def renderizza_documento_stampa(argomento, diffic, intestazione_html, domande_html, testo_domande, testo_soluzioni):
    """Mostra l'anteprima a schermo del compito e fornisce i tasti per scaricare direttamente i PDF reali."""
    
    # ANTEPRIMA SOLO DOMANDE A SCHERMO
    st.subheader("📝 Anteprima del Compito (per gli Studenti)")
    st.markdown(f"""
    <div class="foglio-word">
        {intestazione_html}
        <div>{domande_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("💾 Scarica i Documenti in PDF")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generazione ed esportazione del PDF del compito alunni
        pdf_alunni = genera_pdf_verifica(argomento, diffic, testo_domande)
        st.download_button(
            label="📄 Scarica PDF Verifica Studenti",
            data=pdf_alunni,
            file_name=f"Verifica_{argomento.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
    with col2:
        # Generazione ed esportazione del PDF delle soluzioni (Nessuna anteprima grafica a schermo)
        pdf_soluzioni = genera_pdf_soluzioni(argomento, testo_soluzioni)
        st.download_button(
            label="🔑 Scarica PDF Chiave di Correzione",
            data=pdf_soluzioni,
            file_name=f"Soluzioni_{argomento.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="secondary",
            use_container_width=True
        )

def mostra_interfaccia_correzione(client, types):
    """Gestisce la sezione di scansione, correzione e valutazione dei compiti."""
    st.header("Scansione e Correzione AI")
    
    traccia = st.text_input("Traccia/Obiettivo dell'esercizio:", placeholder="Es. Risolvi la seguente equazione...")
    testo_alunno = st.text_area("Testo o trascrizione del compito dell'alunno:", height=200)
    
    if st.button("Avvia Correzione"):
        if not traccia or not testo_alunno:
            st.error("Inserisci sia la traccia che il testo dell'alunno!")
        else:
            with st.spinner("Analisi e correzione in corso..."):
                sys_p = "Sei un professore italiano severo ma giusto. Analizza il compito, evidenzia gli errori in rosso e fornisci un voto finale in decimi (es. 6½, 7, 8+)."
                user_p = f"Traccia: {traccia}\nSvolgimento Alunno: {testo_alunno}\n\nFornisci errori dettagliati e voto."
                
                try:
                    risp = client.models.generate_content(
                        model='gemini-2.5-flash', 
                        contents=user_p, 
                        config={'system_instruction': sys_p, 'temperature': 0.3}
                    )
                    st.session_state["analisi_correzione"] = risp.text
                except Exception as e:
                    st.error(f"Errore durante la correzione: {e}")
                    
    if "analisi_correzione" in st.session_state:
        st.subheader("📝 Esito della Correzione")
        st.markdown(f"""
        <div class="box-valutazione">
            {st.session_state["analisi_correzione"].replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
