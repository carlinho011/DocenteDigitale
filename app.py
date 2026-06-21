import streamlit as st, os, json, re, time
import correttore

st.set_page_config(
    page_title="EduCorrect - AI per Professori", 
    page_icon="📝", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNZIONE PER CARICARE IL CSS DA FILE ESTERNO ---
def carica_css(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ File {nome_file} non trovato. Grafica di default applicata.")

# Caricamento del file grafico esterno stile.css
carica_css("stile.css")

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
    st.markdown("<div style='max-width: 500px; margin: 80px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1e293b !important; font-family:sans-serif;'>🔒 Area Riservata Docenti</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b !important; font-family:sans-serif; margin-bottom: 25px;'>Benvenuto su EduCorrect. Inserisci le tue credenziali per accedere.</p>", unsafe_allow_html=True)
    em = st.text_input("Email:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi al Registro", use_container_width=True):
        if em in UTENTI and pw == UTENTI[em]: 
            st.session_state["autenticato"], st.session_state["utente_connesso"] = True, em
            st.rerun()
        else: 
            st.error("❌ Credenziali errate.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- BARRA LATERALE ---
st.sidebar.markdown("<h2 style='text-align: center; color: #fbbf24 !important; font-family:sans-serif;'>📝 EduCorrect AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align: center; color: #94a3b8 !important; font-size: 13px;'>👤 {st.session_state['utente_connesso']}</p>", unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

def reset_modalita():
    if "testo_verifica" in st.session_state: del st.session_state["testo_verifica"]
    if "analisi_correzione" in st.session_state: del st.session_state["analisi_correzione"]

modalita = st.sidebar.radio(
    "FUNZIONALITÀ PLANCIA:", 
    ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"],
    on_change=reset_modalita
)
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)

if st.sidebar.button("🚪 Disconnetti ed Esci", use_container_width=True):
    st.session_state["autenticato"] = False
    reset_modalita()
    st.rerun()
    st.stop()

# --- APPLICAZIONE PRINCIPALE ---
if modalita == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore Integrato di Verifiche")
    st.markdown("<p style='color: #94a3b8 !important;'>Configura i parametri ministeriali per strutturare il compito in classe.</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='background-color: rgba(255,255,255,0.02); padding: 25px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 25px;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: argomento = st.text_input("Argomento Didattico:", placeholder="Es. Sigmund Freud, Equazioni di secondo grado...")
    with col2: stile = st.selectbox("Tipologia Quesiti:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3: diff = st.selectbox("Livello di Difficoltà:", ["facile", "media", "difficile"])
    num = st.slider("Numero Totale di Domande:", 1, 20, 5)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("🪄 Elabora Struttura Verifica e Soluzioni", type="primary"):
        if not argomento: 
            st.error("Inserisci un argomento didattico prima di procedere!")
        else:
            with st.spinner("L'intelligenza artificiale sta elaborando e ordinando la verifica..."):
                sys_p = (
                    "Sei un assistente didattico esperto per le superiori italiane. Genera direttamente i quesiti e le risposte in italiano. "
                    "NON includere introduzioni discorsive (es. 'Ecco una verifica...'), e non inserire intestazioni per nome, cognome, classe, data o istituto. "
                    "REGLA ORDINE DOMANDE MISTE: Se il tipo richiesto è 'Domande miste', ordina e raggruppa i quesiti in modo logico per tipologia. "
                    "Ad esempio metti prima tutte le domande a Scelta Multipla, poi tutte le domande Vero/Falso, e infine le Risposte Aperte. "
                    "Mantieni una numerazione progressiva e continua da 1 a N per tutto il foglio senza azzerare il conteggio tra le sottosezioni. "
                    "IMPORTANTE MATEMATICA: NON usare codice LaTeX con $ o $$. Scrivi le formule e i simboli usando i caratteri Unicode estesi o entità matematiche HTML. "
                    "Inserisci il tag [SOLUZIONI] subito prima delle chiavi di correzione."
                )
                user_p = f"Crea una verifica superiore di livello {diff} su {argomento}. Tipo: {stile}. Numero quesiti totali: {num}."
                risposta_ver = None
                
                modelli_tentativi = ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash']
                
                for idx, modello in enumerate(modelli_tentativi):
                    successo = False
                    for tentativo in range(3):
                        try:
                            risp = client.models.generate_content(model=modello, contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.5})
                            risposta_ver = risp.text
                            successo = True
                            break
                        except Exception as e:
                            stringa_errore = str(e)
                            if "503" in stringa_errore or "UNAVAILABLE" in stringa_errore:
                                time.sleep(2 + tentativo * 2)
                            else:
                                break
                    if successo: break
                    elif idx < len(modelli_tentativi) - 1:
                        st.warning(f"⚠️ Modello {modello} temporaneamente saturo. Reindirizzamento della richiesta...")

                if r_text := risposta_ver: 
                    st.session_state["testo_verifica"] = r_text
                    st.success("Verifica e soluzioni generate con successo!")

    if "testo_verifica" in st.session_state:
        tg = st.session_state['testo_verifica']
        
        tg_pulito = re.sub(r'(?i)^[^1A-Za-z]*(Ecco|Questo|Di seguito|Verifica).*?(\n|\r)+', '', tg)
        tg_pulito = re.sub(r'(?i)(Nome|Cognome|Alunno|Classe|Data|Istituto|Materia|Scuola|Corso|Docente|Professore|Tempo).*?(\[.*?\]|__+)', '', tg_pulito)
        tg_pulito = re.sub(r'(?i)^.*Verifica di.*$', '', tg_pulito, flags=re.MULTILINE)
        tg_pulito = re.sub(r'^-+$', '', tg_pulito, flags=re.MULTILINE)
        tg_pulito = tg_pulito.strip()
        
        testo_puro_domande = ""
        testo_puro_soluzioni = ""
        
        if "[SOLUZIONI]" in tg_pulito:
            parti_pure = tg_pulito.split("[SOLUZIONI]")
            testo_puro_domande = parti_pure[0].strip()
            testo_puro_soluzioni = parti_pure[1].strip()
        else:
            testo_puro_domande = tg_pulito.strip()
            testo_puro_soluzioni = "Nessuna chiave di correzione fornita."

        tg_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', tg_pulito)
        tg_html = re.sub(r'\*(.*?)\*', r'<b>\1</b>', tg_html)
        
        html_domande = ""
        if "[SOLUZIONI]" in tg_html:
            parti = tg_html.split("[SOLUZIONI]")
            html_domande = parti[0].replace('\n', '<br>')
        else:
            html_domande = tg_html.replace('\n', '<br>')
        
        i_html = f"<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;font-size:15px;'>Istituto Statale di Istruzione Superiore</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: _________________________________________</td><td style='text-align:right;'>Classe: ________ Sez. ____</td></tr><tr><td style='padding-top:15px;font-size:16px;font-weight:bold;'>Verifica Scritta Valutativa ({diff.capitalize()})</td><td style='padding-top:15px;text-align:right;font-size:16px;font-weight:bold;'>Materia/Oggetto: {argomento.capitalize()}</td></tr></table>"
        
        correttore.renderizza_documento_stampa(
            argomento=argomento.capitalize(), 
            diffic=diff.capitalize(),
            intestazione_html=i_html, 
            domande_html=html_domande, 
            testo_domande=testo_puro_domande,
            testo_soluzioni=testo_puro_soluzioni
        )

elif modalita == "🔍 Scansiona e Correggi":
    correttore.mostra_interfaccia_correzione(client, types)
