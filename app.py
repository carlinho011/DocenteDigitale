import streamlit as st
import os
import json
import google.generativeai as genai

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# STILE GRAFICO APPLICATO ALL'INTERA APPLICAZIONE (Anteprima a schermo stile foglio A4)
st.markdown("""
    <style>
    .foglio-word {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 50px 60px !important;
        margin: 20px auto !important;
        max-width: 800px !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.15) !important;
        border: 1px solid #d3d3d3 !important;
        font-family: 'Times New Roman', Times, serif !important;
        line-height: 1.6 !important;
        font-size: 16px !important;
    }
    .tabella-intestazione {
        width: 100% !important;
        border-collapse: collapse !important;
        border-bottom: 2px solid #000000 !important;
        margin-bottom: 25px !important;
        font-family: Arial, sans-serif !important;
        font-size: 14px !important;
        color: #000000 !important;
    }
    .tabella-intestazione td {
        border: none !important;
        padding: 6px 0 !important;
    }
    .salto-pagina {
        page-break-before: always !important;
        break-before: page !important;
        margin-top: 50px !important;
        border-top: 2px dashed #000000 !important;
        padding-top: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# CONFIGURAZIONE CLIENT (Google Generative AI SDK Stabile)
# ==========================================================
if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Configurazione incompleta: Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])

# ==========================================================
# GESTIONE ACCOUNT (LOGIN)
# ==========================================================
UTENTI_DEFAULT = {"admin@educorrect.it": "AdminPass2026", "prof.test@scuola.it": "TestScuola99"}
UTENTI_ATTIVI = UTENTI_DEFAULT
if "UTENTI_ABILITATI" in st.secrets:
    try:
        UTENTI_ATTIVI = json.loads(st.secrets["UTENTI_ABILITATI"])
    except Exception:
        UTENTI_ATTIVI = UTENTI_DEFAULT

if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state:
    st.session_state["utente_connesso"] = ""

if not st.session_state["autenticato"]:
    st.title("🔒 Area Riservata Docenti - EduCorrect")
    email_inserita = st.text_input("Inserisci la tua Email:")
    password_inserita = st.text_input("Inserisci la tua Password:", type="password")
    if st.button("Accedi al Sistema"):
        if email_inserita in UTENTI_ATTIVI and password_inserita == UTENTI_ATTIVI[email_inserita]:
            st.session_state["autenticato"] = True
            st.session_state["utente_connesso"] = email_inserita
            st.rerun()
        else:
            st.error("❌ Credenziali errate.")
    st.stop()

# ==========================================================
# INTERFACCIA PRINCIPALE CON NAVIGAZIONE IN SIDEBAR
# ==========================================================
st.sidebar.title("🛠️ Menu EduCorrect")
st.sidebar.write(f"👤 Utente: **{st.session_state['utente_connesso']}**")

modalita = st.sidebar.radio(
    "Scegli l'operazione da eseguire:",
    ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"]
)

st.sidebar.markdown("---")
if st.sidebar.button("Disconnetti / Esci"):
    st.session_state["autenticato"] = False
    st.session_state["utente_connesso"] = ""
    if "testo_verifica" in st.session_state:
        del st.session_state["testo_verifica"]
    if "analisi_correzione" in st.session_state:
        del st.session_state["analisi_correzione"]
    st.rerun()

# ==========================================================
# LOGICA DI CONTROLLO DELLE SEZIONI
# ==========================================================

# --- SEZIONE 1: GENERATORE DI VERIFICHE ---
if modalita == "🚀 Genera Nuova Verifica":
    st.header("Generatore di Compiti in Classe")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        argomento = st.text_input("Inserisci l'argomento della verifica:", placeholder="Es. I vulcani...")
    with col2:
        stile_domande = st.selectbox("Tipo di domande:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3:
        difficolta = st.selectbox("Livello di difficoltà:", ["facile", "media", "difficile"])
    
    numero_domande = st.slider("Numero di domande totali:", min_value=1, max_value=20, value=5)
    
    if st.button("Genera Testo Verifica"):
        if not argomento:
            st.error("Scrivi un argomento prima di generare!")
        else:
            with st.spinner("Generazione compito in corso con Gemini..."):
                prompt_sistema = (
                    "Sei un assistente didattico esperto per i licei e gli istituti tecnici italiani (Scuola Superiore). "
                    "Genera la verifica e le relative risposte esclusivamente in lingua italiana. "
                    f"Il livello di complessità generale deve essere calibrato come '{difficolta}' per gli standard delle scuole superiori. "
                    "Inserisci obbligatoriamente il tag specifico [SOLUZIONI] subito prima di iniziare a scrivere le chiavi di correzione."
                )
                prompt_utente = f"Crea una verifica superiore di livello '{difficolta}' su '{argomento}'. Tipo domande: {stile_domande}. Numero quesiti: {numero_domande}."
                
                try:
                    # Impostato gemini-1.5-flash per evitare i blocchi di quota 429 dell'altro modello
                    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=prompt_sistema)
                    risposta = model.generate_content(prompt_utente)
                    st.session_state["testo_verifica"] = risposta.text
                    st.success("Verifica generata!")
                except Exception as e:
                    st.error(f"⚠️ Errore di generazione: {e}")

    if "testo_verifica" in st.session_state:
        testo_grezzo = st.session_state['testo_verifica']
        st.write("### 📄 Esporta Documento")
        
        # Nome del file PDF dinamico basato sull'argomento
        slug_argomento = argomento.lower().replace(' ', '_')
        nome_file_pdf = f"verifica_{difficolta}_{slug_argomento}.pdf"

        # IL TASTO PDF REALE CLICCABILE (Niente comandi da tastiera, usa html2pdf da sorgente esterna)
        script_pdf_pulsante = f"""
            <div style="margin-bottom: 20px;">
                <button onclick="scaricaFilePDF()" style="
                    background-color: #2e7d32;
                    color: white;
                    padding: 14px 28px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.15);
                ">
                    📥 Scarica Verifica in PDF (Tasto Diretto)
                </button>
            </div>
            <script src="https://cloudflare.com"></script>
            <script>
                function scaricaFilePDF() {{
                    var target = window.parent.document.getElementById("blocco-foglio-word-target");
                    if (!target) {{
                        alert("Attendi il caricamento completo dell'anteprima prima di scaricare.");
                        return;
                    }}
                    var configurazione = {{
                        margin: 12,
                        filename: '{nome_file_pdf}',
                        image: {{ type: 'jpeg', quality: 0.98 }},
                        html2canvas: {{ scale: 2, useCORS: true, letterRendering: true }},
                        jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }}
                    }};
                    html2pdf().set(configurazione).from(target).save();
                }}
            </script>
        """
        # Renderizza il pulsante grafico visibile a schermo
        st.components.v1.html(script_pdf_pulsante, height=75)

        # Costruzione dell'anteprima grafica (Foglio Word A4 bianco)
        testo_html = testo_grezzo.replace('\n', '<br>')
        div_salto_pagina = "<div class='salto-pagina'><h3 style='color: #000000; border-bottom: 2px solid #000000; padding-bottom: 5px;'>🔑 CHIAVE DI CORREZIONE (FOGLIO DOCENTE)</h3><br>"
        corpo_documento_html = testo_html.replace("[SOLUZIONI]", div_salto_pagina + "</div>")

        intestazione_word_html = f"<table class='tabella-intestazione'><tr><td style='width: 60%; font-weight: bold;'>Istituto d'Istruzione Superiore</td><td style='width: 40%; text-align: right; font-weight: bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: _____________________________________</td><td style='text-align: right;'>Classe: ____________  Sez. ____</td></tr><tr><td style='padding-top: 10px; font-size: 16px; font-weight: bold;'>Materia: Verifica scritta di approfondimento ({difficolta.capitalize()})</td><td style='padding-top: 10px; text-align: right; font-size: 16px; font-weight: bold;'>Oggetto: {argomento.capitalize()}</td></tr></table>"
        
        # Mostra il foglio Word con l'ID agganciato dal pulsante JavaScript sopra
        st.markdown(f"<div id='blocco-foglio-word-target' class='foglio-word'>{intestazione_word_html}{corpo_documento_html}</div>", unsafe_allow_html=True)


# --- SEZIONE 2: SCANSIONA E CORREGGI ---
elif modalita == "🔍 Scansiona e Correggi":
    st.header("🔍 Correttore Intelligente di Compiti")
    st.write("Inserisci l'elaborato dell'alunno per correggerlo ed emettere il voto in decimi.")
