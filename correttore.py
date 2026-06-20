import streamlit as st, re

def converti_markdown_in_html(testo):
    testo_pulito = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', testo)
    testo_pulito = re.sub(r'^\s*\*\s+', r'• ', testo_pulito, flags=re.MULTILINE)
    return testo_pulito

def renderizza_documento_stampa(titolo, info_scuola_html, voto_html, corpo_testo_html):
    blocco_stampa_iframe = f"<div style='margin-bottom:15px;'><button onclick='window.print()' style='background-color:#0288d1;color:white;padding:12px 24px;border:none;border-radius:6px;cursor:pointer;font-size:15px;font-weight:bold;box-shadow:0 3px 5px rgba(0,0,0,0.1);'>📥 Scarica / Stampa PDF della Correzione</button></div><div style='background-color:#ffffff;color:#000000;padding:40px;font-family:\"Times New Roman\",serif;line-height:1.6;font-size:16px;border:1px solid #d3d3d3;max-width:800px;margin:0 auto;'>{info_scuola_html}<h1 style='text-align:center;font-size:22px;margin-top:10px;margin-bottom:5px;'>{titolo}</h1>{voto_html}<br><div>{corpo_testo_html}</div></div><style>@media print {{ button {{ display: none !important; }} body {{ background-color: #ffffff !important; padding: 0 !important; }} }}</style>"
    st.components.v1.html(blocco_stampa_iframe, height=900, scrolling=True)

def mostra_interfaccia_correzione(client, types):
    st.header("🔍 Correttore Didattico Avanzato")
    
    col1, col2 = st.columns(2)
    with col1: nome_alunno = st.text_input("Alunno/a:", placeholder="Nome dello studente")
    with col2: arg_compito = st.text_input("Materia/Argomento:", placeholder="Es. Saggio breve su Dante")
    
    testo_m = st.text_area("✍️ Incolla il testo del compito:", height=180)
    file_c = st.file_uploader("📂 Oppure carica una foto o un PDF:", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("🔎 Avvia Correzione Complessa"):
        if not nome_alunno or not arg_compito:
            st.error("Inserisci il nome dell'alunno e la materia!")
        elif not testo_m and not file_c:
            st.error("Inserisci il compito da correggere!")
        else:
            with st.spinner("Generazione correzione approfondita in corso..."):
                sys_c = (
                    "Sei un docente italiano esperto. Devi generare una correzione complessa, dettagliata e pedagogica. "
                    "Rivolgiti DIRETTAMENTE allo studente usando la seconda persona singolare (es. 'Hai svolto...', 'Ti consiglio di...'). "
                    "Usa un tono chiaro, incoraggiante ma rigoroso, spiegando gli errori in modo che lo studente capisca come migliorare. "
                    "Stabilisci tu autonomamente i criteri accademici ideali per questo argomento senza chiederli. "
                    "La struttura della tua risposta deve essere RIGIDAMENTE questa:\n"
                    "Inizia la primissima riga scrivendo ESATTAMENTE: VOTO: X/10 (dove X è il voto meritato).\n"
                    "Nella seconda riga scrivi un breve giudizio riassuntivo per lo studente.\n"
                    "Lascia una riga vuota e poi scrivi l'analisi dettagliata divisa in sezioni chiare (es. Punti di forza, Errori rilevati, Consigli per il futuro)."
                )
                
                contenuto_input = [f"Studente: {nome_alunno}\nArgomento del compito: {arg_compito}\n\nCompito da analizzare:\n"]
                if testo_m: contenuto_input.append(testo_m)
                if file_c:
                    m_type = "application/pdf" if file_c.name.endswith(".pdf") else "image/jpeg"
                    contenuto_input.append(types.Part.from_bytes(data=file_c.getvalue(), mime_type=m_type))
                
                try:
                    # Utilizziamo gemini-2.5-pro per garantire una correzione complessa e di alta qualità didattica
                    risp = client.models.generate_content(model='gemini-2.5-pro', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.4})
                    st.session_state["analisi_correzione"] = risp.text
                    st.success("Correzione completata con successo!")
                except Exception:
                    # Linea di riserva se il modello pro è saturo
                    try:
                        risp = client.models.generate_content(model='gemini-2.5-flash', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.4})
                        st.session_state["analisi_correzione"] = risp.text
                        st.success("Correzione completata!")
                    except Exception as e:
                        st.error(f"Errore di connessione: {e}")

    if "analisi_correzione" in st.session_state:
        cx = st.session_state["analisi_correzione"]
        linee = [l.strip() for l in cx.split("\n") if l.strip()]
        
        # Estrazione sicura del voto e del giudizio iniziale
        voto_rilevato = "N/D"
        giudizio_rilevato = ""
        corpo_linee = []
        
        for l in linee:
            if l.upper().startswith("VOTO:"):
                voto_rilevato = l.replace("VOTO:", "").replace("Voto:", "").strip()
            elif not giudizio_rilevato and voto_rilevato != "N/D":
                giudizio_rilevato = l
            else:
                corpo_linee.append(l)
                
        corpo_testo = "\n\n".join(corpo_linee)
        
        # Interfaccia Streamlit: Mostra il widget del voto in alto per il docente
        st.metric(label="Voto Assegnato", value=voto_rilevato)
        
        # Generazione layout per il file PDF stampabile
        info_html = f"<div style='border-bottom:2px solid #000; padding-bottom:8px; font-family:Arial, sans-serif; font-size:14px;'><b>Studente:</b> {nome_alunno} <br> <b>Materia/Argomento:</b> {arg_compito}</div>"
        
        # Box del voto integrato direttamente nel foglio Word/PDF
        voto_html = f"<div style='background-color:#f8f9fa; border:1px dashed #0288d1; padding:15px; margin-top:15px; text-align:center; border-radius:4px;'><span style='font-size:24px; font-weight:bold; color:#0288d1;'>Valutazione Finale: {voto_rilevato}</span><br><p style='margin:5px 0 0 0; font-style:italic;'>{giudizio_rilevato}</p></div>"
        
        corpo_html = converti_markdown_in_html(corpo_testo).replace('\n', '<br>')
        
        renderizza_documento_stampa("SCHEDA DI CORREZIONE INDIVIDUALE", info_html, voto_html, corpo_html)

