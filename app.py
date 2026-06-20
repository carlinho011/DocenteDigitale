import streamlit as st
import os
import json

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
# CONFIGURAZIONE CLIENT (Nuovo SDK Google GenAI Ufficiale)
# ==========================================================
if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Configurazione incompleta: Inserisci 'GEMINI_KEY' nei Secrets di Streamlit.")
    st.stop()

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error(f"Errore caricamento nuovo SDK Google: {e}")
    st.stop()

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
                
                # Linea principale Visiva e Testuale 2.5 Flash
                try:
                    risposta = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_utente,
                        config={'system_instruction': prompt_sistema, 'temperature': 0.6}
                    )
                    st.session_state["testo_verifica"] = risposta.text
                    st.success("Verifica generata!")
                except Exception as e:
                    # Backup 1: Gemini 2.5 Pro
                    if "429" in str(e) or "quota" in str(e).lower() or "exhausted" in str(e).lower():
                        st.warning("⚠️ Linea principale satura. Switch automatico su Gemini 2.5 Pro...")
                        try:
                            risposta = client.models.generate_content(
                                model='gemini-2.5-pro',
                                contents=prompt_utente,
                                config={'system_instruction': prompt_sistema, 'temperature': 0.6}
                            )
                            st.session_state["testo_verifica"] = risposta.text
                            st.success("Verifica generata con successo su linea Pro!")
                        except Exception as e2:
                            # Backup 2: Gemini 2.5 Flash-8B
                            st.warning("⚠️ Anche la linea Pro è carica. Tentativo finale su linea Flash-8B...")
                            try:
                                risposta = client.models.generate_content(
                                    model='gemini-2.5-flash-8b',
                                    contents=prompt_utente,
                                    config={'system_instruction': prompt_sistema, 'temperature': 0.6}
                                )
                                st.session_state["testo_verifica"] = risposta.text
                                st.success("Verifica generata con successo su linea Flash-8B!")
                            except Exception as final_err:
                                st.error(f"❌ Tutte le linee Google sono sature: {final_err}")
                    else:
                        st.error(f"⚠️ Errore di generazione: {e}")

    if "testo_verifica" in st.session_state:
        testo_grezzo = st.session_state['testo_verifica']
        st.write("### 📄 Esporta Documento")
        
        slug_argomento = argomento.lower().replace(' ', '_')
        nome_file_pdf = f"verifica_{difficolta}_{slug_argomento}.pdf"

        # Tasto download PDF diretto
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
elif modalita == "🔍 Scansiona e Correggi":
    st.header("🔍 Correttore Intelligente di Compiti")
    st.write("Inserisci l'elaborato dell'alunno per correggerlo ed emettere il voto in decimi.")
    col_input, col_criteri = st.columns(2)
    
    with col_input:
        file_compito = st.file_uploader("📂 Carica file o seleziona foto (da galleria o fotocamera):", type=["png", "jpg", "jpeg", "pdf"])
        testo_manuale = st.text_area("✍️ Testo incollato dello studente:", height=150, placeholder="Risposte dello studente...")
        
    with col_criteri:
        griglia_riferimento = st.text_area("🔑 Criteri di valutazione o soluzioni di riferimento:",
                                           value=st.session_state.get("testo_verifica", ""), height=230,
                                           placeholder="I dati della verifica generata nell'altra sezione vengono copiati qui in automatico.")

    if st.button("🔎 Avvia Correzione Automatica"):
        if not file_compito and not testo_manuale:
            st.error("Inserisci un compito inserendo del testo o caricando una foto.")
        else:
            with st.spinner("Analisi del compito e calcolo del voto in corso..."):
                prompt_correzione_sistema = (
                    "Sei un docente di scuola superiore italiana severo, preciso e costruttivo. "
                    "Analizza il compito dello studente confrontandolo con i criteri forniti. "
                    "Restituisci l'analisi strutturata in italiano secondo questo schema:\n"
                    "1. Riassunto del compito analizzato.\n"
                    "2. Analisi degli errori rilevati.\n"
                    "3. Elementi positivi riscontrati.\n"
                    "4. Suggerimenti mirati.\n"
                    "5. VALUTAZIONE FINALE: Voto numerico in decimi (da 2 a 10)."
                )
                
                contenuto_richiesta = []
                
                if file_compito:
                    file_bytes = file_compito.read()
                    part_immagine = types.Part.from_bytes(data=file_bytes, mime_type=file_compito.type)
                    contenuto_richiesta.append(part_immagine)
                
                # CORREZIONE: Aggiunta la virgola mancante tra le stringhe concatenate
                testo_da_inviare = "Compito dello studente:\n" + testo_manuale + "\n\nCriteri/Soluzioni:\n" + griglia_riferimento
                contenuto_richiesta.append(testo_da_inviare)
                
                try:
                    risposta_correzione = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contenuto_richiesta,
                        config={'system_instruction': prompt_correzione_sistema, 'temperature': 0.4}
                    )
                    st.session_state["analisi_correzione"] = risposta_correzione.text
                    st.success("Correzione completata!")
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower() or "exhausted" in str(e).lower():
                        st.warning("⚠️ Linea principale visiva satura. Switch automatico su Gemini 2.5 Pro...")
                        try:
                            risposta_correzione = client.models.generate_content(
                                model='gemini-2.5-pro',
                                contents=contenuto_richiesta,
                                config={'system_instruction': prompt_correzione_sistema, 'temperature': 0.4}
                            )
                            st.session_state["analisi_correzione"] = risposta_correzione.text
                            st.success("Correzione completata usando la linea Pro!")
                        except Exception as e2:
                            st.warning("⚠️ Linea Pro carica. Tentativo finale su linea Flash-8B...")
                            try:
                                risposta_correzione = client.models.generate_content(
                                    model='gemini-2.5-flash-8b',
                                    contents=contenuto_richiesta,
                                    config={'system_instruction': prompt_correzione_sistema, 'temperature': 0.4}
                                )
                                st.session_state["analisi_correzione"] = risposta_correzione.text
                                st.success("Correzione completata usando la linea Flash-8B!")
                            except Exception as final_err:
                                st.error(f"❌ Linee saturate: {final_err}")
                    else:
                        st.error(f"⚠️ Errore durante la correzione: {e}")
                        
    if "analisi_correzione" in st.session_state:
        st.subheader("📊 Scheda di Valutazione del Docente")
        testo_analysis = st.session_state["analisi_correzione"]
        
        # CORREZIONE: Inseriti gli a capo corretti (<br>) al posto dello svuotamento stringa
        analisi_html = testo_analysis.replace('\n', '<br>')
        
        st.markdown("<div class='foglio-word'><h3 style='color: #bf1515; border-bottom: 2px solid #bf1515; padding-bottom: 5px;'>📝 RELAZIONE E CORREZIONE DEL COMPITO</h3><br><div style='font-family: \"Times New Roman\", Times, serif; font-size: 16px; color: #000000;'>" + analisi_html + "</div></div>", unsafe_allow_html=True)
