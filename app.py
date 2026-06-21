import streamlit as st, os, json, re
import correttore

st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")
st.markdown("""<style>
    .foglio-word { background-color: #ffffff !important; color: #000000 !important; padding: 50px 60px !important; margin: 20px auto !important; max-width: 800px !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.15) !important; border: 1px solid #d3d3d3 !important; font-family: 'Times New Roman', Times, serif !important; line-height: 1.6 !important; font-size: 16px !important; }
    .tabella-intestazione { width: 100% !important; border-collapse: collapse !important; border-bottom: 2px solid #000000 !important; margin-bottom: 25px !important; font-family: Arial, sans-serif !important; font-size: 14px; }
    .tabella-intestazione td { border: none !important; padding: 6px 0 !important; }
    .box-valutazione { border: 2px solid #bf1515 !important; background-color: #fff8f8 !important; padding: 15px 20px !important; margin-bottom: 20px !important; border-radius: 4px !important; font-family: Arial, sans-serif !important; }
</style>""", unsafe_allow_html=True)

if "GEMINI_KEY" not in st.secrets: 
    st.error("⚠️ Inserisci 'GEMINI_KEY' nei Secrets.")
    st.stop()

try:
    from google import genai; from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e: 
    st.error(f"Errore SDK: {e}")
    st.stop()

UTENTI = json.loads(st.secrets["UTENTI_ABILITATI"]) if "UTENTI_ABILITATI" in st.secrets else {"admin@educorrect.it": "AdminPass2026"}
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state: st.session_state["utente_connesso"] = ""

# --- SCHERMATA LOGIN ---
if not st.session_state["autenticato"]:
    st.title("🔒 Area Riservata Docenti - EduCorrect")
    em, pw = st.text_input("Email:"), st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if em in UTENTI and pw == UTENTI[em]: 
            st.session_state["autenticato"], st.session_state["utente_connesso"] = True, em
            st.rerun()
        else: 
            st.error("❌ Credenziali errate.")
    st.stop()

# --- BARRA LATERALE ---
st.sidebar.title("🛠️ Menu EduCorrect")
st.sidebar.write(f"👤 Utente: **{st.session_state['utente_connesso']}**")

# Funzione per pulire la sessione ai cambi di stato
def reset_modalita():
    if "testo_verifica" in st.session_state: del st.session_state["testo_verifica"]
    if "analisi_correzione" in st.session_state: del st.session_state["analisi_correzione"]

modalita = st.sidebar.radio(
    "Scegli l'operazione:", 
    ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"],
    on_change=reset_modalita
)
st.sidebar.markdown("---")

if st.sidebar.button("Disconnetti / Esci"):
    st.session_state["autenticato"] = False
    reset_modalita()
    st.rerun()
    st.stop()

# --- APPLICAZIONE PRINCIPALE ---
if modalita == "🚀 Genera Nuova Verifica":
    st.header("Generatore di Compiti in Classe")
    col1, col2, col3 = st.columns(3)
    with col1: argomento = st.text_input("Argomento:", placeholder="Es. Equazioni...")
    with col2: stile = st.selectbox("Tipo:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3: diff = st.selectbox("Difficoltà:", ["facile", "media", "difficile"])
    num = st.slider("Numero domande:", 1, 20, 5)
    
    if st.button("Genera Testo Verifica"):
        if not argomento: 
            st.error("Scrivi un argomento!")
        else:
            with st.spinner("Generazione in corso..."):
                sys_p = "Sei un assistente didattico esperto per le superiori italiane. Genera direttamente i quesiti e le risposte in italiano. NON includere introduzioni come 'Ecco una verifica...', e non inserire intestazioni per nome, cognome, classe, data o istituto. IMPORTANTE MATEMATICA: NON usare codice LaTeX con $ o $$. Scrivi le formule e i simboli usando i caratteri Unicode estesi o entità matematiche leggibili in HTML. Inserisci il tag [SOLUZIONI] subito prima delle chiavi di correzione."
                user_p = f"Crea una verifica superiore di livello {diff} su {argomento}. Tipo: {stile}. Numero quesiti: {num}."
                risposta_ver = None
                try:
                    risp = client.models.generate_content(model='gemini-2.5-pro', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.6})
                    risposta_ver = risp.text
                except Exception:
                    st.warning("⚠️ Linea Pro satura. Switch automatico su Gemini Flash...")
                    try:
                        risp = client.models.generate_content(model='gemini-2.5-flash', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.6})
                        risposta_ver = risp.text
                    except Exception as e_ver: 
                        st.error(f"❌ Errore server: {e_ver}")
                if risposta_ver: 
                    st.session_state["testo_verifica"] = risposta_ver
                    st.success("Verifica generata!")

    if "testo_verifica" in st.session_state:
        tg = st.session_state['testo_verifica']
        
        # 1. Pulizia introduzioni dell'AI
        tg_pulito = re.sub(r'(?i)^[^1A-Za-z]*(Ecco|Questo|Di seguito|Verifica).*?(\n|\r)+', '', tg)
        
        # 2. Rimozione diciture personali duplicate
        tg_pulito = re.sub(r'(?i)(Nome|Cognome|Alunno|Classe|Data|Istituto|Materia|Scuola|Corso|Docente|Professore|Tempo).*?(\[.*?\]|__+)', '', tg_pulito)
        tg_pulito = re.sub(r'(?i)^.*Verifica di.*$', '', tg_pulito, flags=re.MULTILINE)
        tg_pulito = re.sub(r'^-+$', '', tg_pulito, flags=re.MULTILINE)
        tg_pulito = tg_pulito.strip()
        
        # 3. Conversione Markdown Bold in HTML
        tg_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', tg_pulito)
        tg_html = re.sub(r'\*(.*?)\*', r'<b>\1</b>', tg_html)
        
        # 4. Separazione netta di Domande e Soluzioni tramite indici di lista
        html_domande = ""
        html_soluzioni = ""
        
        if "[SOLUZIONI]" in tg_html:
            parti = tg_html.split("[SOLUZIONI]")
            html_domande = parti[0].replace('\n', '<br>')
            html_soluzioni = parti[1].replace('\n', '<br>')
        else:
            html_domande = tg_html.replace('\n', '<br>')
            html_soluzioni = "Nessuna chiave di correzione fornita dal modello."
        
        # 5. Layout tabella intestazione ministeriale
        i_html = f"<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;'>Istituto Superiori</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: ___________________________</td><td style='text-align:right;'>Classe: ____ Sez. __</td></tr><tr><td style='padding-top:10px;font-size:16px;font-weight:bold;'>Verifica scritta ({diff.capitalize()})</td><td style='padding-top:10px;text-align:right;font-size:16px;font-weight:bold;'>Oggetto: {argomento.capitalize()}</td></tr></table>"
        
        # Renderizza l'interfaccia passando separatamente domande e soluzioni
        correttore.renderizza_documento_stampa(
            titolo=f"Verifica Scritta ({diff.capitalize()})", 
            argomento=argomento.capitalize(), 
            intestazione_html=i_html, 
            domande_html=html_domande, 
            soluzioni_html=html_soluzioni
        )

elif modalita == "🔍 Scansiona e Correggi":
    correttore.mostra_interfaccia_correzione(client, types)
