import streamlit as st, re

def converti_markdown_in_html(testo):
    testo_pulito = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', testo)
    testo_pulito = re.sub(r'^\s*\*\s+', r'• ', testo_pulito, flags=re.MULTILINE)
    return testo_pulito

def renderizza_documento_stampa(titolo, info_scuola_html, voto_html, corpo_testo_html):
    blocco_stampa_iframe = f"<div style='margin-bottom:15px;'><button onclick='window.print()' style='background-color:#0288d1;color:white;padding:12px 24px;border:none;border-radius:6px;cursor:pointer;font-size:15px;font-weight:bold;box-shadow:0 3px 5px rgba(0,0,0,0.1);'>📥 Scarica / Stampa PDF della Correzione</button></div><div style='background-color:#ffffff;color:#000000;padding:40px;font-family:\"Times New Roman\",serif;line-height:1.6;font-size:16px;border:1px solid #d3d3d3;max-width:800px;margin:0 auto;'>{info_scuola_html}<h1 style='text-align:center;font-size:22px;margin-top:10px;margin-bottom:5px;'>{titolo}</h1>{voto_html}<br><div>{corpo_testo_html}</div></div><style>@media print {{ button {{ display: none !important; }} body {{ background-color: #ffffff !important; padding: 0 !important; }} }}</style>"
    st.components.v1.html(blocco_stampa_iframe, height=950, scrolling=True)

def mostra_interfaccia_correzione(client, types):
    st.header("🔍 Valutazione dello Studente")
    
    col1, col2 = st.columns(2)
    with col1: nome_alunno = st.text_input("Alunno/a:", placeholder="Nome dello studente")
    with col2: arg_compito = st.text_input("Materia/Argomento:", placeholder="Es. Storia del Novecento")
    
    testo_m = st.text_area("✍️ Incolla qui l'elaborato svolto:", height=180)
    file_c = st.file_uploader("📂 Oppure carica foto/PDF dell'elaborato:", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("🔎 Avvia Valutazione Formativa"):
        if not nome_alunno or not arg_compito:
            st.error("Inserisci il nome dell'alunno e la materia!")
        elif not testo_m and not file_c:
            st.error("Inserisci l'elaborato da analizzare!")
        else:
            with st.spinner("Analisi delle competenze in corso..."):
                sys_c = (
                    "Sei un docente italiano esperto in valutazione formativa e orientativa. "
                    "Non limitarti a correggere l'esercizio: valuta la preparazione, le competenze e le lacune dello STUDENTE stesso. "
                    "Rivolgiti sempre a lui in seconda persona ('Tu'). Non dire 'Il testo presenta', ma di' 'Tu hai dimostrato di...'. "
                    "Stabilisci tu autonomamente i criteri accademici ideali per l'argomento.\n\n"
                    
                    "La struttura della tua risposta deve essere RIGIDAMENTE questa:\n"
                    "Inizia la primissima riga scrivendo ESATTAMENTE: VOTO: X/10\n"
                    "Nella seconda riga scrivi un profilo riassuntivo dello studente (es. 'Studente preparato ma frettoloso...').\n"
                    "Lascia una riga vuota e organizza il resto della risposta ESATTAMENTE in queste 3 macro-aree visive utilizzando queste precise intestazioni:\n\n"
                    
                    "🟢 LE TUE COMPETENZE ACQUISITE\n"
                    "(Evidenzia qui cosa lo studente ha capito, le sue abilità logiche e i suoi punti di forza personali)\n\n"
                    
                    "🔴 LE TUE LACUNE DA COLMARE\n"
                    "(Elenca qui in modo chiaro e schematico dove lo studente si è confuso, cosa non ha assimilato o gli errori concettuali ripetuti)\n\n"
                    
                    "🚀 IL TUO PIANO DI MIGLIORAMENTO\n"
                    "(Fornisci consigli pratici sul metodo di studio, argomenti specifici da ripassare ed esercizi futuri da fare)"
                )
                
                contenuto_input = [f"Studente da valutare: {nome_alunno}\nAmbito didattico: {arg_compito}\n\nElaborato prodotto:\n"]
                if testo_m: contenuto_input.append(testo_m)
                if file_c:
                    m_type = "application/pdf" if file_c.name.endswith(".pdf") else "image/jpeg"
                    contenuto_input.append(types.Part.from_bytes(data=file_c.getvalue(), mime_type=m_type))
                
                try:
                    risp = client.models.generate_content(model='gemini-2.5-pro', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                    st.session_state["analisi_correzione"] = risp.text
                    st.success("Valutazione completata!")
                except Exception:
                    try:
                        risp = client.models.generate_content(model='gemini-2.5-flash', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                        st.session_state["analisi_correzione"] = risp.text
                        st.success("Valutazione completata!")
                    except Exception as e:
                        st.error(f"Errore di connessione: {e}")

    if "analisi_correzione" in st.session_state:
        cx = st.session_state["analisi_correzione"]
        linee = [l.strip() for l in cx.split("\n") if l.strip()]
        
        voto_rilevato = "N/D"
        profilo_studente = ""
        corpo_linee = []
        
        for l in linee:
            if l.upper().startswith("VOTO:"):
                voto_rilevato = l.replace("VOTO:", "").replace("Voto:", "").strip()
            elif not profilo_studente and voto_rilevato != "N/D":
                profilo_studente = l
            else:
                corpo_linee.append(l)
                
        corpo_testo = "\n\n".join(corpo_linee)
        
        # Sostituzione icone standard con box grafici HTML più eleganti per gli studenti
        corpo_testo = corpo_testo.replace("🟢 LE TUE COMPETENZE ACQUISITE", "<h3 style='color:#2e7d32; border-bottom:1px solid #2e7d32; padding-bottom:5px; margin-top:20px;'>🟢 Le Tue Competenze Acquisite</h3>")
        corpo_testo = corpo_testo.replace("🔴 LE TUE LACUNE DA COLMARE", "<h3 style='color:#c62828; border-bottom:1px solid #c62828; padding-bottom:5px; margin-top:20px;'>🔴 Le Tue Lacune da Colmare</h3>")
        corpo_testo = corpo_testo.replace("🚀 IL TUO PIANO DI MIGLIORAMENTO", "<h3 style='color:#ef6c00; border-bottom:1px solid #ef6c00; padding-bottom:5px; margin-top:20px;'>🚀 Il Tuo Piano di Miglioramento</h3>")
        
        st.metric(label="Valutazione Finale", value=voto_rilevato)
        
        info_html = f"<div style='border-bottom:2px solid #000; padding-bottom:8px; font-family:Arial, sans-serif; font-size:14px;'><b>Studente:</b> {nome_alunno} <br> <b>Materia/Ambito:</b> {arg_compito}</div>"
        voto_html = f"<div style='background-color:#f8f9fa; border:1px solid #0288d1; padding:15px; margin-top:15px; text-align:center; border-radius:4px;'><span style='font-size:22px; font-weight:bold; color:#0288d1;'>Esito: Voto {voto_rilevato}</span><br><p style='margin:5px 0 0 0; font-style:italic; color:#555;'><b>Profilo Studente:</b> {profilo_studente}</p></div>"
        
        corpo_html = converti_markdown_in_html(corpo_testo).replace('\n', '<br>')
        
        renderizza_documento_stampa("SCHEDA DI VALUTAZIONE E ORIENTAMENTO", info_html, voto_html, corpo_html)
