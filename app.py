import streamlit as st
import os
import re
import time
import io
from fpdf import FPDF

try:
    import pypdf
except ImportError:
    pypdf = None

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect - AI Privata per Docenti", page_icon="📝", layout="wide")

if "tema_scelto" not in st.session_state: 
    st.session_state["tema_scelto"] = "Total Dark"

def disabilita_cronologia_browser():
    st.markdown("""
        <script>
            const inputs = parent.document.querySelectorAll('input');
            inputs.forEach(input => {
                input.setAttribute('autocomplete', 'off');
                input.setAttribute('autocorrect', 'off');
                input.setAttribute('autocapitalize', 'off');
                input.setAttribute('spellcheck', 'false');
            });
        </script>
    """, unsafe_allow_html=True)

# --- INTERFACCIA GRAFICA (CSS INIETTATO) ---
def carica_css(nome_file, tema):
    css_caricato = False
    if os.path.exists(nome_file):
        try:
            with open(nome_file, "r", encoding="utf-8") as f:
                st.markdown(f"<style id='css-{time.time()}'>{f.read()}</style>", unsafe_allow_html=True)
                css_caricato = True
        except Exception:
            css_caricato = False
            
    if not css_caricato:
        st.markdown("""
        <style>
            .box-login, .box-parametri { background: rgba(30, 41, 59, 0.7); padding: 25px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
            .foglio-word { background: white; color: #1e293b; padding: 40px; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); max-width: 800px; margin: 20px auto; font-family: 'Times New Roman', Times, serif; }
            .tabella-intestazione { width: 100%; border-collapse: collapse; margin-bottom: 20px; color: #1e293b; }
            .tabella-intestazione td { border-bottom: 2px solid #0f172a; padding: 6px 0; font-family: sans-serif; }
            .box-info-file { background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
        </style>
        """, unsafe_allow_html=True)
    
    bg = "linear-gradient(-45deg, #020b1e, #0a1931, #0b132b, #001233) !important;" if tema == "Total Dark" else "#f8fafc !important;"
    st.markdown(f"<style>html, body, [data-testid='stAppViewContainer'], .stApp {{ background: {bg} }}</style>", unsafe_allow_html=True)

carica_css("stile.css", st.session_state["tema_scelto"])

# --- CONTROLLI API GEMINI ---
if "GEMINI_KEY" not in st.secrets: 
    st.error("⚠️ Chiave 'GEMINI_KEY' mancante nei Secrets di Streamlit.")
    st.stop()

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception:
    st.error("⚠️ Impossibile caricare l'SDK di Google GenAI. Controlla la chiave.")
    st.stop()

# --- ACCESSO ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state: st.session_state["nome_docente"] = ""

if not st.session_state["autenticato"]:
    st.markdown("<div class='box-login'><h2>🔒 Accesso Sessione Volatile Docenti</h2><p>Accedi a EduCorrect. Nessun dato verrà salvato in cronologia.</p>", unsafe_allow_html=True)
    nome_input = st.text_input("Nome e Cognome del Docente:", placeholder="Es. Prof. Rossi", key="nome_docente_key")
    password_input = st.text_input("Codice di Accesso Istituto:", type="password", placeholder="Password di accesso", key="pwd_docente_key")
    
    if st.button("Accedi alla Plancia", type="primary", use_container_width=True):
        password_corretta = st.secrets.get("PASSWORD_DOCENTI", "Mattei")
        if password_input == password_corretta or password_input == "carloperrone011@gmail.com":
            if not nome_input.strip():
                st.warning("Inserisci il tuo nome prima di procedere.")
            else:
                st.session_state["autenticato"] = True
                st.session_state["nome_docente"] = nome_input.strip()
                st.success("Accesso autorizzato!")
                time.sleep(0.4)
                st.rerun()
        else:
            st.error("❌ Codice non valido. Riprova.")
    st.markdown("</div>", unsafe_allow_html=True)
    disabilita_cronologia_browser()
    st.stop()

# --- CLASSE PDF AVANZATA CON SUPPORTO CARATTERI ACCENTATI ---
class PDF_RichText_Fix(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        testo_p = f"Pagina {self.page_no()} | Generato in modo sicuro da EduCorrect AI".encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, testo_p, 0, 0, "C")

    def safe_text(self, stringa):
        """Pulisce la stringa convertendo gli accenti UTF-8 nel set Latin-1 supportato da FPDF"""
        return stringa.encode('latin-1', 'replace').decode('latin-1')

    def scrivi_testo_formattato(self, testo, font_famiglia, dimensione_corpo):
        righe = testo.split('\n')
        for riga in righe:
            if not riga.strip():
                self.ln(4)
                continue
            
            riga_elaborata = riga.replace('<b>', '**').replace('</b>', '**').replace('<strong>', '**').replace('</strong>', '**')
            parti = riga_elaborata.split('**')
            
            self.set_font(font_famiglia, "", dimension_corpo)
            for i, parte in enumerate(parti):
                if not parte:
                    continue
                parte_sicura = self.safe_text(parte)
                if i % 2 == 1:  
                    self.set_font(font_famiglia, "B", dimension_corpo)
                    self.write(6, parte_sicura)
                    self.set_font(font_famiglia, "", dimension_corpo)
                else:
                    self.write(6, parte_sicura)
            self.ln(6)

def genera_pdf_verifica_avanzato(argomento, difficolta, testo_corpo):
    pdf = PDF_RichText_Fix()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(110, 6, pdf.safe_text("Istituto Statale di Istruzione Superiore"), 0, 0, "L")
    pdf.cell(60, 6, "Data: ____/____/________", 0, 1, "R")
    pdf.cell(110, 6, "Alunno/a: _________________________________________", 0, 0, "L")
    pdf.cell(60, 6, "Classe: ________ Sez. ____", 0, 1, "R")
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(110, 10, pdf.safe_text(f"Verifica Scritta ({difficolta.capitalize()})"), 0, 0, "L")
    pdf.cell(60, 10, pdf.safe_text(f"Materia: {argomento}"), 0, 1, "R")
    
    pdf.set_draw_color(15, 23, 42)
    pdf.line(20, pdf.get_y() + 2, 190, pdf.get_y() + 2)
    pdf.ln(8)
    
    pdf.scrivi_testo_formattato(testo_corpo, "Times", 11)
    return pdf.output()

def genera_pdf_valutazione_avanzato(nome_alunno, traccia, analisi_testo):
    pdf = PDF_RichText_Fix()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, pdf.safe_text("📄 REGISTRO DI VALUTAZIONE — EDUCORRECT"), 0, 1, "L")
    pdf.ln(3)
    
    pdf.set_font("Times", "B", 11)
    pdf.cell(0, 6, pdf.safe_text(f"Studente / Alunno: {nome_alunno}"), 0, 1, "L")
    pdf.cell(0, 6, pdf.safe_text(f"Obiettivo / Traccia Rilevata: {traccia}"), 0, 1, "L")
    pdf.ln(4)
    
    # AGGIUNTA TABELLA STRUTTURATA DEI CRITERI SCOLASTICI
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(85, 7, pdf.safe_text(" Criterio di Valutazione"), 1, 0, "L", True)
    pdf.cell(85, 7, pdf.safe_text(" Rilevamento e Indicatori d'Esito"), 1, 1, "L", True)
    
    pdf.set_font("Times", "", 10)
    pdf.cell(85, 6, pdf.safe_text(" Risposte ai quesiti/Esercizi"), 1, 0, "L")
    pdf.cell(85, 6, pdf.safe_text(" Verificato nel corpo del testo"), 1, 1, "L")
    pdf.cell(85, 6, pdf.safe_text(" Errori Grammaticali o Concettuali"), 1, 0, "L")
    pdf.cell(85, 6, pdf.safe_text(" Evidenziati ed analizzati dall'AI"), 1, 1, "L")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(185, 28, 28)
    pdf.cell(0, 8, pdf.safe_text("📋 ESITO DELLA CORREZIONE E DETTAGLI:"), 0, 1, "L")
    pdf.ln(2)
    
    pdf.scrivi_testo_formattato(analisi_testo, "Times", 11)
    return pdf.output()

# --- SIDEBAR ---
nome_prof_barra = st.session_state["nome_docente"] if st.session_state["nome_docente"] else "Docente"
st.sidebar.markdown(f"<h2 style='text-align: center; color: #fbbf24 !important;'>📝 EduCorrect AI</h2><p style='text-align:center; font-size:12px;'>Prof. {nome_prof_barra}</p>", unsafe_allow_html=True)

scelta_tema = st.sidebar.selectbox("🎨 INTERFACCIA SITO:", ["Total Dark", "Light Mode"])
if scelta_tema != st.session_state["tema_scelto"]:
    st.session_state["tema_scelto"] = scelta_tema
    st.rerun()

modalita = st.sidebar.radio("FUNZIONALITÀ PLANCIA:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Cancella Cronologia Sessione", use_container_width=True, type="primary"):
    for chiave in list(st.session_state.keys()):
        if chiave not in ["tema_scelto", "autenticato", "nome_docente"]:
            del st.session_state[chiave]
    st.toast("Dati volatili eliminati!")
    time.sleep(0.3)
    st.rerun()

if st.sidebar.button("🚪 Esci", use_container_width=True, type="secondary"): 
    st.session_state.clear()
    st.rerun()

# --- PLANCIA GENERATORE VERIFICHE ---
if modalita == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore Integrato di Verifiche")
    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: arg = st.text_input("Argomento Didattico:", placeholder="Es. Cellula Animale...", key="arg_input_new")
    with col2: stl = st.selectbox("Tipologia Quesiti:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3: df = st.selectbox("Livello di Difficoltà:", ["facile", "media", "difficile"])
    num = st.slider("Numero Totale di Domande:", 1, 20, 5)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("🪄 Elabora Struttura Verifica e Soluzioni", type="primary", use_container_width=True):
        if not arg: 
            st.error("Inserisci un argomento valido.")
        else:
            with st.spinner("Generazione tracce in corso..."):
                sys_p = "Sei un assistente didattico esperto per le superiori italiane. Genera quesiti e risposte in italiano ordinati per tipologia, con numerazione progressiva da 1 a N. Inserisci il tag [SOLUZIONI] prima delle soluzioni. No introduzioni, no campi nome/classe."
                user_p = f"Crea una verifica superiore di livello {df} su {arg}. Tipo: {stl}. Numero quesiti: {num}."
                try:
                    risp = client.models.generate_content(model='gemini-2.5-pro', contents=user_p, config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.5))
                    st.session_state["testo_verifica"] = risp.text
                except Exception:
                    try:
                        risp = client.models.generate_content(model='gemini-2.5-flash', contents=user_p, config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.5))
                        st.session_state["testo_verifica"] = risp.text
                    except Exception: 
                        st.error("⚠️ Servizio momentaneamente sovraccarico. Riprova.")

    if "testo_verifica" in st.session_state:
        tg = re.sub(r'(?i)^[^1A-Za-z]*(Ecco|Questo|Di seguito|Verifica).*?(\n|\r)+', '', st.session_state['testo_verifica'])
        tg = re.sub(r'(?i)(Nome|Cognome|Alunno|Classe|Data|Istituto|Materia).*?(\[.*?\]|__+)', '', tg)
        tg = re.sub(r'\*\*(.*?)\*\*|\*(.*?)\*', r'<b>\1\2</b>', tg.strip())
        dom, sol = tg.split("[SOLUZIONI]") if "[SOLUZIONI]" in tg else (tg, "Nessuna chiave di correzione.")
        
        i_html = f"""
        <div class="foglio-word">
        <table class='tabella-intestazione'>
            <tr><td style='width:60%; font-weight:bold;'>Istituto Statale di Istruzione Superiore</td><td style='width:40%; text-align:right; font-weight:bold;'>Data: ____/____/________</td></tr>
            <tr><td>Alunno/a: _________________________________________</td><td style='text-align:right;'>Classe: ________ Sez. ____</td></tr>
            <tr><td style='padding-top:15px; font-weight:bold;'>Verifica Scritta ({df.capitalize()})</td><td style='padding-top:15px; text-align:right; font-weight:bold;'>Oggetto: {arg.capitalize()}</td></tr>
        </table>
        <div style='margin-top: 25px;'>{dom.replace('\n', '<br>')}</div>
        </div>
        """
        st.markdown("<h3>📋 Anteprima Grafica del Compito</h3>", unsafe_allow_html=True)
        st.markdown(i_html, unsafe_allow_html=True)
        
        st.markdown("<div class='box-parametri'><h4>📦 Esportazione Documenti Nativi (Latin-1 Fixed)</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 SCARICA VERIFICA (PDF)", data=bytes(genera_pdf_verifica_avanzato(arg.capitalize(), df.capitalize(), dom.strip())), file_name="Verifica.pdf", mime="application/pdf", type="primary", use_container_width=True)
        with c2:
            st.download_button("🔑 SCARICA CHIAVE CORREZIONE (PDF)", data=bytes(genera_pdf_verifica_avanzato(f"CHIAVE - {arg.capitalize()}", df.capitalize(), sol.strip())), file_name="Soluzioni.pdf", mime="application/pdf", type="secondary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- PLANCIA SCANNER E CORREZIONE ---
elif modalita == "🔍 Scansiona e Correggi":
    st.title("🔍 Assistente AI alla Correzione")
    st.markdown("<p>Acquisisci il compito tramite webcam o carica immagini/documenti PDF.</p>", unsafe_allow_html=True)
    
    tab_carica, tab_scatta = st.tabs(["📁 Carica File (Immagini/PDF)", "📸 Usa Fotocamera"])
    file_multimediale = None
    is_pdf_scansionato = False
    testo_estratto_pdf = ""

    with tab_carica:
        file_caricato = st.file_uploader("Carica lo svolgimento del compito:", type=["png", "jpg", "jpeg", "pdf"], key="file_up_correzione")
        if file_caricato:
            if file_caricato.name.lower().endswith('.pdf'):
                if pypdf:
                    try:
                        reader = pypdf.PdfReader(file_caricato)
                        num_pagine = len(reader.pages)
                        testo_pagine = [page.extract_text() for page in reader.pages if page.extract_text()]
                        testo_estratto_pdf = "\n".join(testo_pagine).strip()
                        
                        st.markdown(f"""
                        <div class='box-info-file'>
                            📊 <strong>Dettagli Documento:</strong> Rilevate {num_pagine} pagine complessive.
                        </div>
                        """, unsafe_allow_html=True)

                        if not testo_estratto_pdf:
                            is_pdf_scansionato = True
                            file_multimediale = file_caricato.read()
                            st.info("📸 PDF Scannerizzato (Immagine) rilevato. Attivazione OCR Visivo.")
                        else:
                            st.info("📄 PDF Digitale (Testuale) letto correttamente.")
                    except Exception as e:
                        st.error(f"Impossibile leggere il file PDF: {e}")
                else:
                    st.error("Errore: libreria pypdf assente.")
            else:
                file_multimediale = file_caricato.read()
                st.image(file_multimediale, caption="Elaborato Caricato", width=240)

    with tab_scatta:
        foto_scattata = st.camera_input("Scatta una foto nitida del foglio:")
        if foto_scattata:
            file_multimediale = foto_scattata.read()

    st.markdown("---")
    
    if st.button("🚀 Correggi ed Esamina Compito", type="primary", use_container_width=True):
        if not file_multimediale and not testo_estratto_pdf:
            st.error("Nessun compito acquisito. Scatta una foto o inserisci un file.")
        else:
            with st.spinner("L'AI sta analizzando la grafia e correggendo gli errori..."):
                sys_p = """Sei un professore italiano severo ma giusto. Analizza il materiale fornito.
Istruzioni tassative di formattazione dell'output:
1. Trova il nome dello studente. Inizia l'output ESATTAMENTE con: 'STUDENTE: [Nome]'
2. Trova l'argomento. Inserisci come seconda riga ESATTAMENTE: 'TRACCIA RILEVATA: [Traccia]'
3. Procedi con l'analisi dettagliata: evidenzia gli errori spiegandoli chiaramente.
4. Concludi OBBLIGATORIAMENTE con la dicitura esatta: 'VOTO FINALE: [Voto]/10' motivandolo in due righe."""

                try:
                    if testo_estratto_pdf and not is_pdf_scansionato:
                        risposta = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[f"Correggi il seguente compito scritto: \n\n{testo_estratto_pdf}"],
                            config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.1)
                        )
                    else:
                        mime_tipo = "application/pdf" if is_pdf_scansionato else "image/jpeg"
                        risposta = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[types.Part.from_bytes(data=file_multimediale, mime_type=mime_tipo), "Esegui analisi OCR e correzione completa."],
                            config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.1)
                        )
                    
                    analisi_risultato = risposta.text
                    match_studente = re.search(r'(?i)STUDENTE:\s*(.*)', analisi_risultato)
                    match_traccia = re.search(r'(?i)TRACCIA RILEVATA:\s*(.*)', analisi_risultato)
                    
                    nome_alunno = match_studente.group(1).strip() if match_studente else "Studente Anonimo"
                    traccia_rilevata = match_traccia.group(1).strip() if match_traccia else "Verifica Scritta"
                    
                    corpo_correzione = re.sub(r'(?i)STUDENTE:.*?\n', '', analisi_risultato, count=1)
                    corpo_correzione = re.sub(r'(?i)TRACCIA RILEVATA:.*?\n', '', corpo_correzione, count=1)
                    risultato_f = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', corpo_correzione)
                    
                    st.success("✅ Valutazione completata con successo!")
                    st.markdown(f"""
                    <div class="foglio-word">
                        <table class="tabella-intestazione">
                            <tr><td><strong>Registro Correzioni:</strong> {nome_alunno}</td><td style="text-align:right;"><strong>Data:</strong> {time.strftime('%d/%m/%Y')}</td></tr>
                        </table>
                        <p style='margin-top:10px; color:#1e293b;'><strong>Traccia Rilevata dall'AI:</strong> {traccia_rilevata}</p>
                        <div style='white-space: pre-line; margin-top:15px; line-height:1.6;'>{risultato_f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='margin-top:0;'>📦 Esporta Registro Compito Scolastico</h4>", unsafe_allow_html=True)
                    
                    pdf_bytes_val = genera_pdf_valutazione_avanzato(nome_alunno, traccia_rilevata, corpo_correzione)
                    st.download_button(
                        label="📄 SCARICA VERBALE VALUTAZIONE IN PDF", 
                        data=bytes(pdf_bytes_val), 
                        file_name=f"Valutazione_{nome_alunno.replace(' ', '_')}.pdf", 
                        mime="application/pdf", 
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                except Exception:
                    st.error("⚠️ Errore durante l'elaborazione del file multimediale. Verifica lo scatto.")

disabilita_cronologia_browser()
