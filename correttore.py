import streamlit as st

def renderizza_documento_stampa(titolo, argomento, intestazione_html, domande_html, soluzioni_html):
    """Mostra l'anteprima del compito e fornisce pulsanti separati per Stampa e Download PDF."""
    
    # MOSTRA SOLO LA VERIFICA NELL'ANTEPRIMA A SCHERMO
    st.subheader("📝 Anteprima del Compito (per gli Studenti)")
    st.markdown(f"""
    <div class="foglio-word" id="sezione-domande">
        {intestazione_html}
        <div>{domande_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SEZIONE 1: SCARICAMENTO E STAMPA VERIFICA ALUNNI
    st.subheader("🖨️ Opzioni Verifica Studenti")
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        if st.button("🖨️ Apri Finestra di Stampa Compito", type="primary", use_container_width=True):
            st.components.v1.html(f"""
            <script>
                var doc = window.open('', '_blank');
                doc.document.write('<html><head><title>{titolo}</title><style>');
                doc.document.write('.foglio-word {{ padding: 40px; font-family: "Times New Roman", serif; line-height: 1.6; font-size: 16px; }}');
                doc.document.write('.tabella-intestazione {{ width: 100%; border-collapse: collapse; border-bottom: 2px solid #000; margin-bottom: 25px; font-family: Arial, sans-serif; font-size: 14px; }}');
                doc.document.write('.tabella-intestazione td {{ padding: 6px 0; }}');
                doc.document.write('</style></head><body>');
                doc.document.write('<div class="foglio-word">{intestazione_html.replace("'", "\\\'")}{domande_html.replace("'", "\\\'")}</div>');
                doc.document.write('</body></html>');
                doc.document.close();
                doc.print();
            </script>
            """, height=0)

    with col_a2:
        # Crea un file HTML scaricabile che esegue l'auto-stampa in PDF all'apertura
        html_alunni_download = f"""<html><head><title>{titolo}</title><style>
        .foglio-word {{ padding: 50px; font-family: "Times New Roman", serif; line-height: 1.6; font-size: 16px; }}
        .tabella-intestazione {{ width: 100%; border-collapse: collapse; border-bottom: 2px solid #000; margin-bottom: 25px; font-family: Arial, sans-serif; font-size: 14px; }}
        .tabella-intestazione td {{ padding: 6px 0; }}
        </style></head><body onload="window.print();">
        <div class="foglio-word">{intestazione_html}{domande_html}</div>
        </body></html>"""
        
        st.download_button(
            label="💾 Scarica PDF Verifica (.html)",
            data=html_alunni_download,
            file_name=f"Verifica_{argomento.replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True
        )

    st.markdown("---")

    # SEZIONE 2: SCARICAMENTO E STAMPA CHIAVE DI CORREZIONE
    st.subheader("🔑 Opzioni Chiave di Correzione (Risposte)")
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        if st.button("🖨️ Apri Finestra di Stampa Soluzioni", type="secondary", use_container_width=True):
            st.components.v1.html(f"""
            <script>
                var doc = window.open('', '_blank');
                doc.document.write('<html><head><title>Soluzioni - {argomento}</title><style>');
                doc.document.write('.foglio-word {{ padding: 40px; font-family: "Times New Roman", serif; line-height: 1.6; font-size: 16px; }}');
                doc.document.write('h3 {{ color: #bf1515; font-family: Arial, sans-serif; border-bottom: 2px dashed #bf1515; padding-bottom: 10px; }}');
                doc.document.write('</style></head><body>');
                doc.document.write('<div class="foglio-word"><h3>🔑 CHIAVE DI CORREZIONE: {argomento.replace("'", "\\\'")}</h3><br>{soluzioni_html.replace("'", "\\\'")}</div>');
                doc.document.write('</body></html>');
                doc.document.close();
                doc.print();
            </script>
            """, height=0)

    with col_s2:
        # File delle risposte scaricabile con comando auto-stampa incorporato
        html_soluzioni_download = f"""<html><head><title>Soluzioni - {argomento}</title><style>
        .foglio-word {{ padding: 50px; font-family: "Times New Roman", serif; line-height: 1.6; font-size: 16px; }}
        h3 {{ color: #bf1515; font-family: Arial, sans-serif; border-bottom: 2px dashed #bf1515; padding-bottom: 10px; }}
        </style></head><body onload="window.print();">
        <div class="foglio-word"><h3>🔑 CHIAVE DI CORREZIONE: {argomento}</h3><br>{soluzioni_html}</div>
        </body></html>"""
        
        st.download_button(
            label="💾 Scarica PDF Soluzioni (.html)",
            data=html_soluzioni_download,
            file_name=f"Soluzioni_{argomento.replace(' ', '_')}.html",
            mime="text/html",
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
