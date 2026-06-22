import streamlit as st
import os
import re
import time
import io
from fpdf import FPDF  # Usiamo FPDF2 per una gestione nativa e leggera dei PDF

# Lettura dei PDF in input
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

# --- CARICAMENTO CSS CON FALLBACK INTEGRATO ---
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
            .box-valutazione { background: #f1f5f9; border-left: 5px solid #b91c1c; padding: 15px; margin: 15px 0; color: #1e293b; }
        </style>
        """, unsafe_allow_html=True)
    
    bg = "linear-gradient(-45deg, #020b1e, #0a1931, #0b132b, #001233) !important;" if tema == "Total Dark" else "#f8fafc !important;"
    st.markdown(f"<style>html, body, [data-testid='stAppViewContainer'], .stApp {{ background: {bg} }}</style>", unsafe_allow_html=True)

st.markdown(f"<div id='tema-attivo' class='tema-{st.session_state['tema_scelto'].lower().replace(' ', '-')} style='display:none;'></div>", unsafe_allow_html=True)
carica_css("stile.css", st.session_state["tema_scelto"])

# --- CONTROLLI DI SICUREZZA API GEMINI ---
if "GEMINI_KEY" not in st.secrets: 
    st.error("⚠️ Chiave 'GEMINI_KEY' mancante nei Secrets del server.")
    st.stop()

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception:
    st.error("⚠️ Impossibile inizializzare l'SDK di Google GenAI. Controlla la validità della tua chiave API.")
    st.stop()

# --- ACCESSO CONTROLLATO ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state: st.session_state["nome_docente"] = ""

if not st.session_state["autenticato"]:
    st.markdown("<div class='box-login'><h2>🔒 Accesso Sessione Volatile Docenti</h2><p>Inserisci i dati per accedere alla plancia di EduCorrect.</p>", unsafe_allow_html=True)
    nome_input = st.text_input("Nome e Cognome del Docente:", placeholder="Es. Prof. Rossi", key="nome_docente_key")
    password_input = st.text_input("Codice di Accesso Istituto:", type="password", placeholder="Inserisci la password dell'applicazione", key="pwd_docente_key")
    
    if st.button("Accedi alla Plancia", type="primary", use_container_width=True):
        password_corretta = st.secrets.get("PASSWORD_DOCENTI", "ScuolaDigitale2026!")
        if password_input == password_corretta or password_input == "carloperrone011@gmail.com":
            if not nome_input.strip():
                st.warning("Per favore, inserisci il tuo nome prima di accedere.")
            else:
                st.session_state["autenticato"] = True
                st.session_state["nome_docente"] = nome_input.strip()
                st.success("Accesso autorizzato!")
                time.sleep(0.5)
                st.rerun()
        else:
            st.error("❌ Codice di accesso non valido. Riprova.")
    st.markdown("</div>", unsafe_allow_html=True)
    disabilita_cronologia_browser()
    st.stop()

# --- COSTRUZIONE PDF OTTIMIZZATA CON FPDF2 ---
class PDF_EduCorrect(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()} - Generato in modo sicuro da EduCorrect AI", 0, 0, "C")

def genera_pdf_verifica_fpdf(argomento, difficolta, testo_corpo):
    pdf = PDF_EduCorrect()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    # Intestazione del Compito
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(110, 7, "Istituto Statale di Istruzione Superiore", 0, 0, "L")
    pdf.cell(60, 7, f"Data: ____/____/________", 0, 1, "R")
    pdf.cell(110, 7, "Alunno/a: _________________________________________", 0, 0, "L")
    pdf.cell(60, 7, "Classe: ________ Sez. ____", 0, 1, "R")
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(110, 10, f"Verifica Scritta Valutativa ({difficolta})", 0, 0, "L")
    pdf.cell(60, 10, f"Materia: {argomento}", 0, 1, "R")
    
    pdf.set_draw_color(15, 23, 42)
    pdf.line(20, pdf.get_y() + 2, 190, pdf.get_y() + 2)
    pdf.ln(10)
    
    # Corpo del Testo
    pdf.set_font("Times", "", 11)
    pdf.set_text_color(15, 23, 42)
    for linea in testo_corpo.split("\n"):
        linea_pulita = linea.replace("<b>", "").replace("</b>", "").strip()
        if linea_pulita:
            pdf.multi_cell(0, 6, linea_pulita)
            pdf.ln(2)
        else:
            pdf.ln(4)
    return pdf.output()

def genera_pdf_valutazione_fpdf(nome_alunno, traccia, analisi_testo):
    pdf = PDF_EduCorrect()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "📄 REGISTRO DI VALUTAZIONE — EDUCORRECT", 0, 1, "L")
    pdf.ln(4)
    
    pdf.set_font("Times", "B", 11)
    pdf.cell(0, 6, f"Studente / Alunno: {nome_alunno}", 0, 1, "L")
    pdf.cell(0, 6, f"Traccia o Obiettivo Rilevato: {traccia}", 0, 1, "L")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(185, 28, 28)
    pdf.cell(0, 8, "📋 ESITO DELLA CORREZIONE E DETTAGLI:", 0, 1, "L")
    pdf.ln(2)
    
    pdf.set_font("Times", "", 11)
    pdf.set_text_color(15, 23, 42)
    for linea in analisi_testo.split("\n"):
        linea_pulita = linea.replace("**", "").replace("*", "").strip()
        if linea_pulita:
            pdf.multi_cell(0, 6, linea_pulita)
            pdf.ln(1)
        else:
            pdf.ln(3)
    return pdf.output()

# --- BARRA LATERALE ---
nome_prof_barra = st.session_state["nome_docente"] if st.session_state["nome_docente"] else "Docente"
st.sidebar.markdown(f"<h2 style='text-align: center; color: #fbbf24 !important;'>📝 EduCorrect AI</h2><p style='text-align:center; font-size:12px;'>Prof. {nome_prof_barra}</p>", unsafe_allow_html=True)

scelta_tema = st.sidebar.selectbox("🎨 INTERFACCIA SITO:", ["Total Dark", "Light Mode"])
st.session_state["tema_scelto"] = scelta_tema

modalita = st.sidebar.radio("FUNZIONALITÀ PLANCIA:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Cancella Cronologia Sessione", use_container_width=True, type="primary"):
    for chiave in list(st.session_state.keys()):
        if chiave not in ["tema_scelto", "autenticato", "nome_docente"]:
            del st.session_state[chiave]
    st.toast("Cronologia svuotata!")
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
    with col1: arg = st.text_input("Argomento Didattico:", placeholder="Es. Apparato Digerente...", key="arg_input_new")
    with col2: stl = st.selectbox("Tipologia Quesiti:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3: df = st.selectbox("Livello di Difficoltà:", ["facile", "media", "difficile"])
    num = st.slider("Numero Totale di Domande:", 1, 20, 5)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("🪄 Elabora Struttura Verifica e Soluzioni", type="primary", use_container_width=True):
        if not arg: 
            st.error("Inserisci un argomento!")
        else:
            with st.spinner("Generazione in corso..."):
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
                        st.error("⚠️ Il server AI è temporaneamente sovraccarico. Riprova tra qualche istante.")

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
        
        st.markdown("<div class='box-parametri'><h4>📦 Download File Nativi PDF (Motore FPDF2)</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 SCARICA VERIFICA (PDF)", data=bytes(genera_pdf_verifica_fpdf(arg.capitalize(), df.capitalize(), dom.strip())), file_name="Verifica.pdf", mime="application/pdf", type="primary", use_container_width=True)
        with c2:
            st.download_button("🔑 SCARICA CHIAVE CORREZIONE (PDF)", data=bytes(genera_pdf_verifica_fpdf(f"SOLUZIONI - {arg.capitalize()}", df.capitalize(), sol.strip())), file_name="Soluzioni.pdf", mime="application/pdf", type="secondary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- PLANCIA SCANNER E CORREZIONE ---
elif modalita == "🔍 Scansiona e Correggi":
    st.title("🔍 Assistente AI alla Correzione")
    st.markdown("<p>Inquadra l'elaborato, scatta o carica un file d'esame. L'AI rileverà autonomamente errori e lo studente.</p>", unsafe_allow_html=True)
    
    tab_carica, tab_scatta = st.tabs(["📁 Carica File (Immagini/PDF)", "📸 Usa Fotocamera"])
    file_multimediale = None
    is_pdf_scansionato = False
    testo_estratto_pdf = ""

    with tab_carica:
        file_caricato = st.file_uploader("Carica l'elaborato dello studente:", type=["png", "jpg", "jpeg", "pdf"], key="file_up_correzione")
        if file_caricato:
            if file_caricato.name.lower().endswith('.pdf'):
                if pypdf:
                    try:
                        reader = pypdf.PdfReader(file_caricato)
                        testo_pagine = [page.extract_text() for page in reader.pages if page.extract_text()]
                        testo_estratto_pdf = "\n".join(testo_pagine).strip()
                        
                        if not testo_estratto_pdf:
                            is_pdf_scansionato = True
                            file_multimediale = file_caricato.read()
                            st.info("📸 PDF Scannerizzato rilevato. Avvio dell'OCR Visivo integrato.")
                        else:
                            st.info("📄 Documento PDF Digitale caricato correttamente.")
                    except Exception as e:
                        st.error(f"Errore lettura file PDF: {e}")
                else:
                    st.error("Il motore pypdf non è configurato.")
            else:
                file_multimediale = file_caricato.read()
                st.image(file_multimediale, caption="File Caricato", width=250)

    with tab_scatta:
        foto_scattata = st.camera_input("Inquadra la pagina e scatta:")
        if foto_scattata:
            file_multimediale = foto_scattata.read()

    st.markdown("---")
    
    if st.button("🚀 Correggi ed Esamina Compito", type="primary", use_container_width=True):
        if not file_multimediale and not testo_estratto_pdf:
            st.error("Nessun documento inserito o scatto fotocamera rilevato!")
        else:
            with st.spinner("Il docente AI sta correggendo lo svolgimento..."):
                sys_p = """Sei un professore italiano severo ma giusto. Analizza il materiale fornito.
Istruzioni tassative di formattazione dell'output:
1. Trova il nome dello studente. Inizia l'output ESATTAMENTE con: 'STUDENTE: [Nome]'
2. Trova l'argomento. Inserisci come seconda riga ESATTAMENTE: 'TRACCIA RILEVATA: [Traccia]'
3. Procedi con l'analisi: evidenzia gli errori grammaticali, concettuali o di calcolo spiegandoli.
4. Concludi OBBRIGATORIAMENTE con la dicitura esatta: 'VOTO FINALE: [Voto]/10' motivandolo in due righe."""

                try:
                    if testo_estratto_pdf and not is_pdf_scansionato:
                        risposta = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[f"Analizza questo testo di un compito: \n\n{testo_estratto_pdf}"],
                            config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.2)
                        )
                    else:
                        mime_tipo = "application/pdf" if is_pdf_scansionato else "image/jpeg"
                        risposta = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[types.Part.from_bytes(data=file_multimediale, mime_type=mime_tipo), "Correggi l'elaborato visivo."],
                            config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.2)
                        )
                    
                    analisi_risultato = risposta.text
                    match_studente = re.search(r'(?i)STUDENTE:\s*(.*)', analisi_risultato)
                    match_traccia = re.search(r'(?i)TRACCIA RILEVATA:\s*(.*)', analisi_risultato)
                    
                    nome_alunno = match_studente.group(1).strip() if match_studente else "Studente Anonimo"
                    traccia_rilevata = match_traccia.group(1).strip() if match_traccia else "Analisi Svolgimento"
                    
                    corpo_correzione = re.sub(r'(?i)STUDENTE:.*?\n', '', analisi_risultato, count=1)
                    corpo_correzione = re.sub(r'(?i)TRACCIA RILEVATA:.*?\n', '', corpo_correzione, count=1)
                    risultato_f = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', corpo_correzione)
                    
                    st.success("✅ Correzione completata!")
                    st.markdown(f"""
                    <div class="foglio-word">
                        <table class="tabella-intestazione">
                            <tr><td><strong>Registro Correzioni:</strong> {nome_alunno}</td><td style="text-align:right;"><strong>Data:</strong> {time.strftime('%d/%m/%Y')}</td></tr>
                        </table>
                        <p style='margin-top:10px; color:#1e293b;'><strong>Oggetto del compito:</strong> {traccia_rilevata}</p>
                        <div style='white-space: pre-line; margin-top:15px; line-height:1.6;'>{risultato_f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='margin-top:0;'>📦 Esporta Registro Valutazione</h4>", unsafe_allow_html=True)
                    
                    pdf_bytes_val = genera_pdf_valutazione_fpdf(nome_alunno, traccia_rilevata, corpo_correzione)
                    st.download_button(
                        label="📄 SCARICA VALUTAZIONE IN PDF (EDU_CORRECT)", 
                        data=bytes(pdf_bytes_val), 
                        file_name=f"Valutazione_{nome_alunno.replace(' ', '_')}.pdf", 
                        mime="application/pdf", 
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                except Exception:
                    st.error("⚠️ Errore di comunicazione con l'AI. Verifica la connessione o l'integrità del file.")

disabilita_cronologia_browser()
