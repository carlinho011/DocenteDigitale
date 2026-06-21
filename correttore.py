# ... (Funzioni precedenti per la generazione dei PDF di verifica, soluzioni e render stampa rimangono invariate) ...

# ==========================================================================
# 🔍 SEZIONE: ASSISTENTE CORREZIONE MULTIMODALE CON EXPORT PDF
# ==========================================================================

def genera_pdf_valutazione(nome_alunno, traccia, analisi_testo):
    """Genera un PDF formattato con i risultati della correzione e il voto."""
    buffer = io.BytesIO()
    # Usiamo SimpleDocTemplate per una gestione facile del layout
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    # Definiamo gli stili grafici
    stile_testo = ParagraphStyle('ValNormale', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=16)
    stile_titolo = ParagraphStyle('ValTitolo', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#0f172a'))
    stile_sezione = ParagraphStyle('ValSez', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#1e293b'), spaceBefore=10)
    
    # Intestazione del PDF
    story.append(Paragraph(f"📄 REGISTRO DI VALUTAZIONE — EDULOGIC", stile_titolo))
    story.append(Spacer(1, 15))
    
    # Dati dell'alunno e della traccia
    story.append(Paragraph(f"<b>Studente/Alunno:</b> {nome_alunno}", stile_testo))
    story.append(Paragraph(f"<b>Traccia/Obiettivo:</b> {traccia}", stile_testo))
    story.append(Spacer(1, 10))
    story.append(Paragraph("📋 ESITO DELLA CORREZIONE E DETTAGLI:", stile_sezione))
    story.append(Spacer(1, 5))
    
    # Cicliamo sul testo dell'analisi AI (markdown semplice) e convertiamo per il PDF
    for linea in analisi_testo.split('\n'):
        linea = linea.strip()
        if linea:
            # Sostituzione base markdown grassetto per ReportLab
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
            # Piccola anteprima a schermo
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
            # --- AVVIO ANALISI MULTIMODALE ---
            with st.spinner("Il docente AI sta analizzando l'immagine dell'elaborato..."):
                
                # Istruzione di sistema per forzare un formato di output specifico
                sys_p = (
                    "Sei un professore italiano severo ma giusto. Analizza l'immagine dell'elaborato dello studente fornito. "
                    "Trova gli errori ortografici, logici o matematici e commentali dettagliatamente. "
                    "Se il testo è scritto a mano, trascrivilo prima brevemente. "
                    "Al termine della tua analisi inserisci OBBLIGATORIAMENTE una sezione finale chiara chiamata 'VOTO FINALE' "
                    "con una valutazione espressa in decimi (es. VOTO FINALE: 7/10) motivandola brevemente."
                )
                
                # Prepariamo la richiesta multimodale per l'API (Testo + Immagine)
                contenuto_richiesta = [
                    types.Part.from_bytes(data=file_immagine, mime_type="image/jpeg"),
                    f"Traccia originale del compito: {traccia}\nStudente: {nome_alunno}\n\nAnalizza lo svolgimento nell'immagine fornita."
                ]
                
                try:
                    # Invocazione del modello multimodale (Gemini Pro Vision o successivi)
                    # Nota: l'utente deve fornire il client API configurato e i types (google.generativeai)
                    risposta = client.models.generate_content(
                        model='gemini-2.5-flash', # Modello ottimizzato per velocità/vision
                        contents=contenuto_richiesta,
                        config=types.GenerateContentConfig(
                            system_instruction=sys_p,
                            temperature=0.3 # Temperatura bassa per maggiore precisione sulla correzione
                        )
                    )
                    
                    # Recuperiamo il testo generato
                    analisi_risultato = risposta.text
                    
                    # --- VISUALIZZAZIONE RISULTATI ---
                    st.success("✅ Analisi completata!")
                    
                    # Mostriamo l'anteprima a schermo "stile foglio"
                    st.markdown("<br><h3 class='titolo-anteprima'>📝 Esito della Correzione AI</h3>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="foglio-word">
                        <p><b>Alunno:</b> {nome_alunno}</p>
                        <p><b>Traccia:</b> {traccia}</p>
                        <hr style='border: 0.5px solid #cbd5e1;'>
                        <div style='white-space: pre-line;'>{analisi_risultato}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- EXPORT IN PDF ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='margin-top:0; font-family:sans-serif;'>📦 Scarica Verbale di Valutazione Nativo PDF</h4>", unsafe_allow_html=True)
                    
                    # Generiamo il PDF dei risultati
                    pdf_voto = genera_pdf_valutazione(nome_alunno, traccia, analisi_risultato)
                    
                    st.download_button(
                        label="📄 SCARICA VALUTAZIONE (PDF)",
                        data=pdf_voto,
                        file_name=f"Valutazione_{nome_alunno.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Si è verificato un errore durante l'analisi dell'AI: {e}")
