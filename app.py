    if "testo_verifica" in st.session_state:
        tg = st.session_state['testo_verifica']
        
        # 1. Rimuoviamo eventuali intestazioni ripetute generate accidentalmente dall'AI
        # (Pulisce pattern comuni come "Nome:___", "Classe:___", "Data:___")
        tg_pulito = re.sub(r'(?i)(Nome|Cognome|Alunno|Classe|Data|Istituto):\s*[_.]+', '', tg)
        tg_pulito = re.sub(r'(?i)(Nome e Cognome|Classe e Sezione):?\s*___________________________', '', tg_pulito)
        
        # 2. Converte la sintassi degli asterischi Markdown in tag HTML <b> (Grassetto) in modo sicuro
        tg_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', tg_pulito)
        tg_html = re.sub(r'\*(.*?)\*', r'<b>\1</b>', tg_html)
        
        # 3. Gestione del tag delle soluzioni: separiamo nettamente le domande dalle risposte
        if "[SOLUZIONI]" in tg_html:
            parti = tg_html.split("[SOLUZIONI]")
            # Domande (senza la chiusura del div che spezzerebbe il layout)
            corpo_domande = parti[0].replace('\n', '<br>')
            # Soluzioni (inserite in un blocco dedicato che va in una nuova pagina)
            corpo_soluzioni = "<div style='page-break-before:always; border-top:2px dashed #000; padding-top:20px;'><h3>🔑 CHIAVE DI CORREZIONE</h3><br>" + parti[1].replace('\n', '<br>') + "</div>"
            c_html = corpo_domande + corpo_soluzioni
        else:
            c_html = tg_html.replace('\n', '<br>')
        
        # 4. Layout tabella di intestazione ministeriale (appare una sola volta in cima)
        i_html = f"<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;'>Istituto Superiori</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: ___________________________</td><td style='text-align:right;'>Classe: ____ Sez. __</td></tr><tr><td style='padding-top:10px;font-size:16px;font-weight:bold;'>Verifica scritta ({diff.capitalize()})</td><td style='padding-top:10px;text-align:right;font-size:16px;font-weight:bold;'>Oggetto: {argomento.capitalize()}</td></tr></table>"
        
        # Esegui il render dell'unica intestazione + contenuto pulito
        correttore.renderizza_documento_stampa(f"Verifica Scritta ({diff.capitalize()})", argomento.capitalize(), i_html, c_html, "#2e7d32")
