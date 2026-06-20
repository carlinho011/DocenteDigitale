import streamlit as st, re

def converti_markdown_in_html(testo):
    # Sostituisce i doppi asterischi con i tag di grassetto HTML e pulisce i singoli asterischi degli elenchi
    testo_pulito = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', testo)
    testo_pulito = re.sub(r'^\s*\*\s+', r'• ', testo_pulito, flags=re.MULTILINE)
    return testo_pulito

def renderizza_documento_stampa(titolo, intestazione, info_scuola_html, corpo_testo_html, colore_bottone):
    blocco_stampa_iframe = f"<div style='margin-bottom:15px;'><button onclick='window.print()' style='background-color:{colore_bottone};color:white;padding:12px 24px;border:none;border-radius:6px;cursor:pointer;font-size:15px;font-weight:bold;box-shadow:0 3px 5px rgba(0,0,0,0.1);'>📥 Scarica / Stampa come PDF</button></div><div class='foglio-word' style='background-color:#ffffff;color:#000000;padding:40px;font-family:\"Times New Roman\",serif;line-height:1.6;font-size:16px;border:1px solid #d3d3d3;box-shadow:0px 4px 15px rgba(0,0,0,0.1);max-width:800px;margin:0 auto;'>{info_scuola_html}<h1 style='text-align:center;font-size:22px;border-bottom:2px solid #000;padding-bottom:10px;margin-top:10px;'>{titolo}</h1><br><div>{corpo_testo_html}</div></div><style>.tabella-intestazione {{ width: 100% !important; border-collapse: collapse !important; border-bottom: 2px solid #000000 !important; margin-bottom: 25px !important; font-family: Arial, sans-serif !important; font-size: 14px; }} .tabella-intestazione td {{ border: none !important; padding: 6px 0 !important; }} @media print {{ button {{ display: none !important; }} body {{ background-color: #ffffff !important; padding: 0 !important; margin: 0 !important; }} .foglio-word {{ border: none !important; box-shadow: none !important; padding: 0 !important; max-width: 100% !important; }} }}</style>"
    st.components.v1.html(blocco_stampa_iframe, height=900, scrolling=True)

def mostra_interfaccia_correzione(client, types):
    st.header("🔍 Correttore Intelligente di Compiti")
    col_stud, col_arg = st.columns(2)
    with col_stud: nome_alunno = st.text_input("Nome Alunno/a:", placeholder="Es. Mario Rossi")
    with col_arg: arg_compito = st.text_input("Materia o Argomento:", placeholder="Es. Matematica")
    
    # Rimosso il secondo layout a colonne con la griglia dei criteri. Ora l'input occupa l'intera larghezza.
    foto = st.camera_input("📸 OPZIONE A: Scatta foto al compito")
    file_c = st.file_uploader("📂 OPZIONE B: Carica file (Immagine o PDF)", type=["png", "jpg", "jpeg", "pdf"])
    testo_m = st.text_area("✍️ OPZIONE C: Incolla o scrivi il testo del compito", height=150)

    if st.button("🔎 Avvia Correzione Automatica"):
        if not foto and not file_c and not testo_m: st.error("Inserisci un compito!")
        elif not nome_alunno or not arg_compito: st.error("Compila nome e argomento!")
        else:
            with st.spinner("Correzione in corso..."):
                # Istruzioni aggiornate: l'AI decide da sola i criteri e inserisce il voto alla fine
                sys_c = (
                    "Sei un docente superiore italiano. Analizza il compito in base all'argomento indicato. "
                    "Non chiedere all'utente i criteri di valutazione: stabilisci tu autonomamente i criteri accademici standard più adatti a questo argomento. "
                    "Sviluppa l'analisi dettagliata in italiano. "
                    "Alla fine di tutta la valutazione inserisci OBBLIGATORIAMENTE la stringa [VALUTAZIONE_BOX] seguita dal voto finale espresso esclusivamente in frazione decimale (es. Voto: 7/10 o Voto: 5/10) e una riga di nota motivazionale riassuntiva."
                )
                
                contenuto_input = [f"Compito da analizzare:\nAlunno: {nome_alunno}\nMateria/Argomento: {arg_compito}"]
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
                    try:
                        risp_flash = client.models.generate_content(model='gemini-2.5-flash', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                        risposta_ricevuta = risp_flash.text
                    except Exception:
                        st.warning("⚠️ Linee 2.5 sature. Attivazione linea d'emergenza Gemini 1.5...")
                        try:
                            risp_15 = client.models.generate_content(model='gemini-1.5-flash', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                            risposta_ricevuta = risp_15.text
                        except Exception as err_critico: st.error(f"❌ Server di Google saturi: {err_critico}")
                
                if risposta_ricevuta: 
                    st.session_state["analisi_correzione"] = risposta_ricevuta
                    st.success("Correzione completata!")

    if "analisi_correzione" in st.session_state:
        cx = st.session_state["analisi_correzione"]
        tag_trovato = None
        for t in ["[VALUTAZIONE_BOX]", "[valutazione_box]", "VALUTAZIONE_BOX", "valutazione_box"]:
            if t in cx: tag_trovato = t; break
        
        if tag_trovato:
            parti = cx.split(tag_trovato)
            # Ora il corpo principale è prima del tag, il voto e la nota finale sono dopo il tag
            corpo_esteso = parti[0].strip()
            voto_finale_testo = parti[1].strip() if len(parti) > 1 else ""
            
            corpo_esteso_html = converti_markdown_in_html(corpo_esteso).replace('\n', '<br>')
            voto_finale_html = converti_markdown_in_html(voto_finale_testo).replace('\n', '<br>')
            
            # Mostra prima il foglio di correzione e poi in basso il box con il voto finale in decimi
            i_corr_html = f"<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;'>Istituto Superiori</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: 2026</td></tr><tr><td>Alunno/a: {nome_alunno}</td><td style='text-align:right;'>Oggetto: {arg_compito}</td></tr></table>"
            renderizza_documento_stampa(f"Scheda di Correzione: {nome_alunno}", arg_compito.capitalize(), i_corr_html, corpo_esteso_html, "#0288d1")
            
            st.markdown(f"<div class='box-valutazione' style='background-color:#f0f7f4; border-left: 5px solid #2e7d32; padding:15px; margin-top:20px; border-radius:4px;'><h3>📊 Esito e Voto Finale</h3>{voto_finale_html}</div>", unsafe_allow_html=True)
        else:
            cx_html = converti_markdown_in_html(cx).replace('\n', '<br>')
            st.markdown(f"<div class='foglio-word'><h3>🔍 Analisi di Correzione</h3><br>{cx_html}</div>", unsafe_allow_html=True)
