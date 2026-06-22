import streamlit as st
import os
import json
import re
import time
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")
if "tema_scelto" not in st.session_state: 
    st.session_state["tema_scelto"] = "Total Dark"

# --- CARICAMENTO CSS DINAMICO ---
def carica_css(nome_file, tema):
    if os.path.exists(nome_file):
        with open(nome_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style id='css-{time.time()}'>{f.read()}</style>", unsafe_allow_html=True)
    
    if tema == "Total Dark":
        bg = "linear-gradient(-45deg, #020b1e, #0a1931, #0b132b, #001233) !important;"
    else:
        bg = "#f8fafc !important;"
    st.markdown(f"<style>html, body, [data-testid='stAppViewContainer'], .stApp {{ background: {bg} }}</style>", unsafe_allow_html=True)

st.markdown(f"<div id='tema-attivo' class='tema-{st.session_state['tema_scelto'].lower().replace(' ', '-')} style='display:none;'></div>", unsafe_allow_html=True)
carica_css("stile.css", st.session_state["tema_scelto"])

# --- CONTROLLI DI SICUREZZA API GEMINI ---
if "GEMINI_KEY" not in st.secrets: 
    st.error("⚠️ Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error(f"Errore SDK Gemini: {e}")
    st.stop()

# --- AUTENTICAZIONE COMPATTA CON PASSWORD ---
if "autenticato" not in st.session_state: 
    st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state:
    st.session_state["nome_docente"] = ""

if not st.session_state["autenticato"]:
    st.markdown("<div class='box-login'><h2>🔒 Area Riservata Docenti</h2><p>Inserisci il tuo nome e il codice di accesso per utilizzare la piattaforma.</p>", unsafe_allow_html=True)
    
    nome_input = st.text_input("Nome e Cognome del Docente:", placeholder="Es. Prof. Rossi")
    password_input = st.text_input("Codice di Accesso Istituto:", type="password", placeholder="Inserisci la password dell'applicazione")
    
    if st.button("Accedi alla Plancia", type="primary", use_container_width=True):
        password_corretta = st.secrets.get("PASSWORD_DOCENTI", "ScuolaDigitale2026!")
        
        # Sblocca l'accesso se inseriscono la password dell'istituto OPPURE la tua email personale
        if password_input == password_corretta or password_input == "carloperrone011@gmail.com":
            if nome_input.strip() == "":
                st.warning("Per favore, inserisci il tuo nome prima di accedere.")
            else:
                st.session_state["autenticato"] = True
                st.session_state["nome_docente"] = nome_input.strip()
                st.success("Accesso autorizzato!")
                time.sleep(1)
                st.rerun()
        else:
            st.error("❌ Codice di accesso non valido. Riprova.")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- GENERATORI PDF REPORTLAB NATIVI ---
def genera_pdf_verifica(argomento, difficolta, testo_corpo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    stile_normale = ParagraphStyle('NormalePDF', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=17)
    stile_intestazione_l = ParagraphStyle('IntestazioneL', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))
    stile_intestazione_r = ParagraphStyle('IntestazioneR', fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=2, textColor=colors.HexColor('#1e293b'))
    stile_titolo_l = ParagraphStyle('TitoloL', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#0f172a'))
    stile_titolo_r = ParagraphStyle('TitoloR', fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=2, textColor=colors.HexColor('#0f172a'))

    dati_tabella = [
        [Paragraph("Istituto Statale di Istruzione Superiore", stile_intestazione_l), Paragraph("Data: ____/____/________", stile_intestazione_r)],
        [Paragraph("Alunno/a: _________________________________________", stile_intestazione_l), Paragraph("Classe: ________ Sez. ____", stile_intestazione_r)],
        [Paragraph(f"Verifica Scritta Valutativa ({difficolta})", stile_titolo_l), Paragraph(f"Materia/Oggetto: {argomento}", stile_titolo_r)]
    ]
    
    tabella = Table(dati_tabella, colWidths=[300, 204])
    tabella.setStyle(TableStyle([
        ('LINEBELOW', (0, 2), (1, 2), 1.5, colors.HexColor('#0f172a')),
        ('BOTTOMPADDING', (0, 0), (1, 2), 8),
        ('TOPPADDING', (0, 0), (1, 2), 8),
        ('VALIGN', (0, 0), (1, 2), 'MIDDLE'),
    ]))
    
    story.append(tabella)
    story.append(Spacer(1, 25))
    
    for linea in testo_corpo.split('\n'):
        linea = linea.strip()
        if linea:
            linea_formattata = re.sub(r'<b>(.*?)</b>', r'<b>\1</b>', linea)
            story.append(Paragraph(linea_formattata, stile_normale))
            story.append(Spacer(1, 8))
        else:
            story.append(Spacer(1, 12))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_soluzioni(argomento, testo_soluzioni):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    stile_normale = ParagraphStyle('SoluzioniNormale', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=17)
    stile_chiave = ParagraphStyle('TitoloChiave', fontName='Helvetica-Bold', fontSize=15, leading=20, textColor=colors.HexColor('#b91c1c'))
    
    story.append(Paragraph(f"🔑 CHIAVE DI CORREZIONE: {argomento}", stile_chiave))
    story.append(Spacer(1, 20))
    
    for linea in testo_soluzioni.split('\n'):
        linea = linea.strip()
        if linea:
            story.append(Paragraph(linea, stile_normale))
            story.append(Spacer(1, 8))
        else:
            story.append(Spacer(1, 12))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_valutazione(nome_alunno, traccia, analisi_testo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    stile_testo = ParagraphStyle('ValNormale', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=16)
    stile_titolo = ParagraphStyle('ValTitolo', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#0f172a'))
    stile_sezione = ParagraphStyle('ValSez', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#1e293b'), spaceBefore=10)
    
    story.append(Paragraph(f"📄 REGISTRO DI VALUTAZIONE — EDULOGIC", stile_titolo))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>Studente/Alunno:</b> {nome_alunno}", stile_testo))
    story.append(Paragraph(f"<b>Traccia/Obiettivo rilevato:</b> {traccia}", stile_testo))
    story.append(Spacer(1, 10))
    story.append(Paragraph("📋 ESITO DELLA CORREZIONE E DETTAGLI:", stile_sezione))
    story.append(Spacer(1, 5))
    
    for linea in analisi_testo.split('\n'):
        linea = linea.strip()
        if linea:
            linea_f = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linea)
            linea_f = re.sub(r'\*(.*?)\*', r'<b>\1</b>', linea_f)
            story.append(Paragraph(linea_f, stile_testo))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 8))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# --- METODI DI RENDERIZZAZIONE INTERFACCIA ---
def renderizza_documento_stampa(argomento, diffic, intestazione_html, domande_html, testo_domande, testo_soluzioni):
    st.markdown("<h3>📋 Anteprima Grafica del Compito</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="foglio-word">
        {intestazione_html}
        <div style='margin-top: 25px;'>{domande_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-family:sans-serif;'>📦 Download File d'Esame Nativi in PDF</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        pdf_alunni = genera_pdf_verifica(argomento, diffic, testo_domande)
        st.download_button(
            label="📄 SCARICA VERIFICA STUDENTI (PDF)",
            data=pdf_alunni,
            file_name=f"Verifica_{argomento.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    with col2:
        pdf_soluzioni = genera_pdf_soluzioni(argomento, testo_soluzioni)
        st.download_button(
            label="🔑 SCARICA CHIAVE DI CORREZIONE (PDF)",
            data=pdf_soluzioni,
            file_name=f"Soluzioni_{argomento.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="secondary",
            use_container_width=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

def mostra_interfaccia_correzione(client, types):
    st.title("🔍 Assistente AI alla Correzione Automatica")
    st.markdown("<p>Carica l'immagine del compito o usa la fotocamera. L'AI rileverà l'alunno, la traccia ed eseguirà la valutazione.</p>", unsafe_allow_html=True)
    
    st.markdown("<h4>📷 Acquisizione Elaborato (Scatta Foto o Carica Immagine)</h4>", unsafe_allow_html=True)
    tab_carica, tab_scatta = st.tabs(["📁 Carica File Immagine", "📸 Usa Fotocamera"])
    file_immagine = None
    
    with tab_carica:
        file_caricato = st.file_uploader("Seleziona l'immagine del compito:", type=["png", "jpg", "jpeg"])
        if file_caricato:
            file_immagine = file_caricato.read()
            st.image(file_immagine, caption="Immagine caricata correttamente", width=300)
            
    with tab_scatta:
        foto_scattata = st.camera_input("Inquadra il foglio del compito e scatta:")
        if foto_scattata:
            file_immagine = foto_scattata.read()
            
    if st.button("🚀 Elabora, Valuta ed Evidenzia Errori", type="primary", use_container_width=True):
        if not file_immagine: 
            st.error("Acquisisci lo svolgimento del compito scattando una foto o caricando un file immagine!")
        else:
            with st.spinner("Il docente AI sta leggendo ed esaminando l'immagine dell'elaborato..."):
                sys_p = """Sei un professore italiano severo ma giusto. Analizza l'immagine dell'elaborato dello studente fornito.
Istruzioni tassative di formattazione dell'output:
1. Trova e leggi il nome dello studente scritto sul foglio. Inizia il testo ESATTAMENTE con la riga: 'STUDENTE: [Nome Rilevato]'
2. Trova e capisci l'argomento o la traccia della domanda. Inserisci come seconda riga ESATTAMENTE: 'TRACCIA RILEVATA: [Traccia o Argomento Rilevato]'
3. Procedi con l'analisi: trascrivi brevemente il testo se scritto a mano, trova gli errori ortografici, logici o matematici e commentali dettagliatamente.
4. Al termine della tua analisi inserisci OBBLIGATORIAMENTE una sezione finale chiara chiamata 'VOTO FINALE' con una valutazione espressa in decimi (es. VOTO FINALE: 7/10) motivandola brevemente."""
                
                contenuto_prompt = "Analizza l'immagine allegata. Estrai il nome dello studente, la traccia/argomento, correggi tutti gli errori ed esprimi il voto finale."
                
                try:
                    risposta = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_bytes(data=file_immagine, mime_type="image/jpeg"),
                            contenuto_prompt
                        ],
                        config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.3)
                    )
                    
                    analisi_risultato = risposta.text
                    
                    match_studente = re.search(r'(?i)STUDENTE:\s*(.*)', analisi_risultato)
                    match_traccia = re.search(r'(?i)TRACCIA RILEVATA:\s*(.*)', analisi_risultato)
                    
                    nome_alunno = match_studente.group(1).strip() if match_studente else "Non rilevato dal foglio"
                    traccia_rilevata = match_traccia.group(1).strip() if match_traccia else "Non rilevata dal foglio"
                    
                    corpo_correzione = re.sub(r'(?i)STUDENTE:.*?\n', '', analisi_risultato, count=1)
                    corpo_correzione = re.sub(r'(?i)TRACCIA RILEVATA:.*?\n', '', corpo_correzione, count=1)
                    
                    risultato_f = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', corpo_correzione)
                    
                    st.success("✅ Analisi completata con successo!")
                    st.markdown("<h3>📝 Esito della Correzione Docente</h3>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="foglio-word">
                        <table class="tabella-intestazione">
                            <tr>
                                <td style="width:60%; font-weight:bold;">Registro Nazionale Correzioni AI</td>
                                <td style="width:40%; text-align:right; font-weight:bold;">Data Revisione: {time.strftime('%d/%m/%Y')}</td>
                            </tr>
                            <tr>
                                <td>Alunno/a: <strong>{nome_alunno}</strong></td>
                                <td style="text-align:right;">Esaminatore: AI Professore</td>
                            </tr>
                        </table>
                        <div class="box-valutazione">
                            <h4>📋 VERBALE DI VALUTAZIONE DIRETTA</h4>
                            <p><strong>Traccia Rilevata:</strong> {traccia_rilevata}</p>
                        </div>
                        <div style='white-space: pre-line; margin-top:20px; line-height:1.6;'>{risultato_f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='margin-top:0; font-family:sans-serif;'>📦 Esporta Verbale di Valutazione</h4>", unsafe_allow_html=True)
                    
                    pdf_valutazione = genera_pdf_valutazione(nome_alunno, traccia_rilevata, corpo_correzione)
                    st.download_button(
                        label="📄 SCARICA VALUTAZIONE IN PDF",
                        data=pdf_valutazione,
                        file_name=f"Valutazione_{nome_alunno.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Si è verificato un errore durante l'invocazione dell'AI: {e}")

# --- BARRA LATERALE E SWITCH TEMA ---
nome_prof_barra = st.session_state["nome_docente"] if st.session_state["nome_docente"] else "Docente"
st.sidebar.markdown(f"<h2 style='text-align: center; color: #fbbf24 !important;'>📝 EduCorrect AI</h2><p style='text-align:center; font-size:12px;'>Prof. {nome_prof_barra}</p>", unsafe_allow_html=True)
scelta_tema = st.sidebar.selectbox("🎨 INTERFACCIA SITO:", ["Total Dark", "Light Mode"], index=0 if st.session_state["tema_scelto"] == "Total Dark" else 1)
if scelta_tema != st.session_state["tema_scelto"]: 
    st.session_state["tema_scelto"] = scelta_tema
    st.rerun()

modalita = st.sidebar.radio("FUNZIONALITÀ PLANCIA:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])
if st.sidebar.button("🚪 Esci", use_container_width=True, type="secondary"): 
    st.session_state["autenticato"] = False
    st.session_state["nome_docente"] = ""
    st.rerun()

# --- PLANCIA GENERATORE VERIFICHE ---
if modalita == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore Integrato di Verifiche")
    st.markdown("<div class='box-parametri'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: arg = st.text_input("Argomento Didattico:", placeholder="Es. Sigmund Freud...")
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
                    risp = client.models.generate_content(
                        model='gemini-2.5-pro', 
                        contents=user_p, 
                        config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.5)
                    )
                    st.session_state["testo_verifica"] = risp.text
                    st.success("Generata con successo!")
                except Exception:
                    try:
                        risp = client.models.generate_content(
                            model='gemini-2.5-flash', 
                            contents=user_p, 
                            config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.5)
                        )
                        st.session_state["testo_verifica"] = risp.text
                        st.success("Generata con successo (Flash)!")
                    except Exception as e: 
                        st.error(f"Errore server: {e}")

    if "testo_verifica" in st.session_state:
        tg = re.sub(r'(?i)^[^1A-Za-z]*(Ecco|Questo|Di seguito|Verifica).*?(\n|\r)+', '', st.session_state['testo_verifica'])
        tg = re.sub(r'(?i)(Nome|Cognome|Alunno|Classe|Data|Istituto|Materia).*?(\[.*?\]|__+)', '', tg)
        tg = re.sub(r'\*\*(.*?)\*\*|\*(.*?)\*', r'<b>\1\2</b>', tg.strip())
        dom, sol = tg.split("[SOLUZIONI]") if "[SOLUZIONI]" in tg else (tg, "Nessuna chiave di correzione.")
        
        i_html = f"""
        <table class='tabella-intestazione'>
            <tr>
                <td style='width:60%; font-weight:bold;'>Istituto Statale di Istruzione Superiore</td>
                <td style='width:40%; text-align:right; font-weight:bold;'>Data: ____/____/________</td>
            </tr>
            <tr>
                <td>Alunno/a: _________________________________________</td>
                <td style='text-align:right;'>Classe: ________ Sez. ____</td>
            </tr>
            <tr>
                <td style='padding-top:15px; font-weight:bold;'>Verifica Scritta ({df.capitalize()})</td>
                <td style='padding-top:15px; text-align:right; font-weight:bold;'>Oggetto: {arg.capitalize()}</td>
            </tr>
        </table>
        """
        renderizza_documento_stampa(arg.capitalize(), df.capitalize(), i_html, dom.replace('\n', '<br>'), dom.strip(), sol.strip())

# --- PLANCIA SCANNER E CORREZIONE ---
elif modalita == "🔍 Scansiona e Correggi":
    mostra_interfaccia_correzione(client, types)
