import streamlit as st, re

def converti_markdown_in_html(testo):
    testo_pulito = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', testo)
    testo_pulito = re.sub(r'^\s*\*\s+', r'• ', testo_pulito, flags=re.MULTILINE)
    return testo_pulito

def renderizza_documento_stampa(titolo, info_scuola_html, corpo_testo_html):
    blocco_stampa_iframe = f"<div style='margin-bottom:15px;'><button onclick='window.print()' style='background-color:#0288d1;color:white;padding:12px 24px;border:none;border-radius:6px;cursor:pointer;font-size:15px;font-weight:bold;'>📥 Scarica / Stampa PDF</button></div><div style='background-color:#ffffff;color:#000000;padding:40px;font-family:\"Times New Roman\",serif;line-height:1.6;font-size:16px;border:1px solid #d3d3d3;max-width:800px;margin:0 auto;'>{info_scuola_html}<h1 style='text-align:center;font-size:22px;border-bottom:2px solid #000;padding-bottom:10px;'>{titolo}</h1><br><div>{corpo_testo_html}</div></div><style>@media print {{ button {{ display: none !important; }} }}</style>"
    st.components.v1.html(blocco_stampa_iframe, height=800, scrolling=True)

def mostra_interfaccia_correzione(client, types):
    st.header("🔍 Correttore Compiti")
    
    # Dati essenziali in una riga
    col1, col2 = st.columns(2)
    with col1: nome_alunno = st.text_input("Alunno/a:")
    with col2: arg_compito = st.text_input("Materia/Argomento:")
    
    # Unico spazio per il compito (Testo o File)
    testo_m = st.text_area("✍️ Incolla qui il testo del compito:", height=180)
    file_c = st.file_uploader("📂 Oppure carica un file (Immagine o PDF):", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("🔎 Correggi Compito"):
        if not nome_alunno or not arg_compito:
            st.error("Inserisci nome e argomento!")
        elif not testo_m and not file_c:
            st.error("Inserisci il contenuto del compito!")
        else:
            with st.spinner("Analisi in corso..."):
                sys_c = (
                    "Sei un docente italiano. Analizza il compito in base all'argomento. "
                    "Genera da solo i criteri di valutazione senza chiederli. "
                    "Inizia la risposta ESATTAMENTE con il voto in decimi scritto così: 'VOTO: X/10' "
                    "seguito da un breve giudizio. Poi, dopo una riga vuota, scrivi i dettagli della correzione."
                )
                
                contenuto_input = [f"Alunno: {nome_alunno}\nArgomento: {arg_compito}\n\nCompito:\n"]
                if testo_m: contenuto_input.append(testo_m)
                if file_c:
                    m_type = "application/pdf" if file_c.name.endswith(".pdf") else "image/jpeg"
                    contenuto_input.append(types.Part.from_bytes(data=file_c.getvalue(), mime_type=m_type))
                
                try:
                    risp = client.models.generate_content(model='gemini-2.5-flash', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                    st.session_state["analisi_correzione"] = risp.text
                    st.success("Correzione completata!")
                except Exception as e:
                    st.error(f"Errore: {e}")

    if "analisi_correzione" in st.session_state:
        cx = st.session_state["analisi_correzione"]
        
        # Separa il voto iniziale dal resto della correzione
        linee = cx.split("\n")
        voto_testo = linee[0] if linee else "Valutazione completata"
        corpo_testo = "\n".join(linee[1:]) if len(linee) > 1 else cx
        
        # Mostra il voto gigante in alto
        st.metric(label="Esito Valutazione", value=voto_testo.replace("VOTO:", "").strip())
        
        # Genera foglio di stampa pulito
        corpo_html = converti_markdown_in_html(corpo_testo).replace('\n', '<br>')
        info_html = f"<div style='border-bottom:2px solid #000; padding-bottom:5px; margin-bottom:20px;'><b>Studente:</b> {nome_alunno} | <b>Materia:</b> {arg_compito}</div>"
        
        renderizza_documento_stampa(f"Correzione Compito", info_html, corpo_html)
