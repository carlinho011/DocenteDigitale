import streamlit as st

def esporta_in_doc_nativo(titolo, intestazione, testo_principale):
    # Genera un file HTML formattato leggibile nativamente da Microsoft Word e Google Doc
    c_html = testo_principale.replace('\n', '<br>').replace("[SOLUZIONI]", "<br><br><hr><h2>🔑 CHIAVE DI CORREZIONE (DOCENTE)</h2><br>")
    documento_completo = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://w3.org'>
    <head><title>{titolo}</title><style>body {{ font-family: "Times New Roman", serif; font-size: 12pt; line-height: 1.5; }}</style></head>
    <body>
        <h2>Istituto Superiore - EduCorrect</h2>
        <h3>Oggetto: {intestazione}</h3>
        <hr>
        <h1 style='text-align:center;'>{titolo}</h1>
        <br>
        <p>{c_html}</p>
    </body>
    </html>
    """
    return documento_completo.encode('utf-8')

def mostra_interfaccia_correzione(client, types):
    st.header("🔍 Correttore Intelligente di Compiti")
    col_stud, col_arg = st.columns(2)
    with col_stud: nome_alunno = st.text_input("Nome Alunno/a:", placeholder="Es. Mario Rossi")
    with col_arg: arg_compito = st.text_input("Materia o Argomento:", placeholder="Es. Matematica")
    col_in, col_cr = st.columns(2)
    with col_in:
        foto = st.camera_input("📸 OPZIONE A:")
        file_c = st.file_uploader("📂 OPZIONE B:", type=["png", "jpg", "jpeg", "pdf"])
        testo_m = st.text_area("✍️ OPZIONE C:", height=100)
    with col_cr: griglia = st.text_area("🔑 Criteri di riferimento:", value=st.session_state.get("testo_verifica", ""), height=260)

    if st.button("🔎 Avvia Correzione Automatica"):
        if not foto and not file_c and not testo_m: st.error("Inserisci un compito!")
        elif not nome_alunno or not arg_compito: st.error("Compila nome e argomento!")
        else:
            with st.spinner("Correzione in corso con modello Pro ad alta precisione..."):
                sys_c = "Sei un docente superiore italiano. Analizza il compito confrontandolo con i criteri. Restituisci l'analisi in italiano. Inserisci OBBLIGATORIAMENTE all'inizio della risposta la stringa [VALUTAZIONE_BOX] seguita dal voto in decimi e una nota motivazionale breve. Subito dopo scrivi il corpo della correzione."
                contenuto_input = [f"Criteri:\n{griglia}\n\nCompito:\nAlunno: {nome_alunno}\nOggetto: {arg_compito}"]
                if testo_m: contenuto_input.append(testo_m)
                if foto: contenuto_input.append(types.Part.from_bytes(data=foto.getvalue(), mime_type="image/jpeg"))
                if file_c:
                    m_type = "application/pdf" if file_c.name.endswith(".pdf") else "image/jpeg"
                    contenuto_input.append(types.Part.from_bytes(data=file_c.getvalue(), mime_type=m_type))
                
                risposta_ricevuta = None
                try:
                    risp_pro = client.models.generate_content(model='gemini-2.5-pro', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                    risposta_ricevuta = risp_pro.text
                except Exception:
                    st.warning("⚠️ Linea Pro satura. Switch automatico su Gemini Flash...")
                    try:
                        risp_flash = client.models.generate_content(model='gemini-2.5-flash', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                        risposta_ricevuta = risp_flash.text
                    except Exception as err_flash: st.error(f"❌ Server saturi: {err_flash}")
                
                if risposta_ricevuta: 
                    st.session_state["analisi_correzione"] = risposta_ricevuta
                    st.success("Correzione completata!")

    if "analisi_correzione" in st.session_state:
        cx = st.session_state["analisi_correzione"]
        fn_corr = f"corr_{nome_alunno.lower().replace(' ', '_')}.doc"
        t_pdf = f"Correzione: {nome_alunno}"
        text_p = cx.replace("[VALUTAZIONE_BOX]", "")
        
        # SISTEMA SCARICAMENTO WORD DOCUMENT (Indistruttibile)
        doc_bytes = esporta_in_doc_nativo(t_pdf, arg_compito.capitalize(), text_p)
        st.download_button(label="📥 Scarica file Word Correzione", data=doc_bytes, file_name=fn_corr, mime="application/msword")
        
        tag_trovato = None
        for t in ["[VALUTAZIONE_BOX]", "[valutazione_box]", "VALUTAZIONE_BOX", "valutazione_box"]:
            if t in cx: tag_trovato = t; break
        
        if tag_trovato:
            parti = cx.split(tag_trovato)
            testo_da_dividere = parti if len(parti) > 1 else cx
            paragrafi = [p.strip() for p in testo_da_dividere.split("\n\n") if p.strip()]
            primo_paragrafo = paragrafi if len(paragrafi) > 0 else ""
            corpo_esteso = "\n\n".join(paragrafi[1:]) if len(paragrafi) > 1 else ""
            
            st.markdown(f"<div class='box-valutazione'><h3>📊 Valutazione Docente</h3>{primo_paragrafo.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
            i_corr_html = f"<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;'>Istituto Superiori</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: 2026</td></tr><tr><td>Alunno/a: {nome_alunno}</td><td style='text-align:right;'>Oggetto: {arg_compito}</td></tr></table>"
            st.markdown(f"<div class='foglio-word'>{i_corr_html}<h3>🔍 Analisi degli Errori e Soluzioni</h3><br>{corpo_esteso.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='foglio-word'><h3>🔍 Analisi di Correzione</h3><br>{cx.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
