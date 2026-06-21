import streamlit as st, os, json, re, time

st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")
if "tema_scelto" not in st.session_state: st.session_state["tema_scelto"] = "Total Dark"

# --- FUNZIONE CARICAMENTO CSS COMPRESSA ---
def carica_css(nome_file, tema):
    if os.path.exists(nome_file):
        with open(nome_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style id='css-{time.time()}'>{f.read()}</style>", unsafe_allow_html=True)
        bg = "linear-gradient(-45deg, #020b1e, #0a1931, #0b132b, #001233) !important; background-size: 400% 400% !important; animation: gradienteScuro 20s ease infinite !important; background-image: linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px), radial-gradient(rgba(99, 102, 241, 0.3) 1.5px, transparent 1.5px) !important; background-size: 45px 45px, 45px 45px, 22px 22px !important; background-position: 0 0, 0 0, 11px 11px !important; background-attachment: fixed" if tema == "Total Dark" else "#f8fafc !important; background-image: radial-gradient(#e2e8f0 1.5px, transparent 1.5px) !important; background-size: 20px 20px !important; animation: none"
        st.markdown(f"<style>html, body, [data-testid='stAppViewContainer'], .stApp {{ background: {bg} !important; }}</style>", unsafe_allow_html=True)

st.markdown(f"<div id='tema-attivo' class='tema-{st.session_state['tema_scelto'].lower().replace(' ', '-')}' style='display:none;'></div>", unsafe_allow_html=True)
carica_css("stile.css", st.session_state["tema_scelto"])

if "GEMINI_KEY" not in st.secrets: st.error("⚠️ Inserisci 'GEMINI_KEY' nei Secrets."); st.stop()
try:
    from google import genai; from google.genai import types; import correttore
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e: st.error(f"Errore SDK: {e}"); st.stop()

UTENTI = json.loads(st.secrets["UTENTI_ABILITATI"]) if "UTENTI_ABILITATI" in st.secrets else {"admin@educorrect.it": "AdminPass2026"}
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False

# --- LOCK LOGIN ---
if not st.session_state["autenticato"]:
    st.markdown("<div class='box-login'><h2>🔒 Area Riservata Docenti</h2><p>Inserisci le tue credenziali.</p>", unsafe_allow_html=True)
    em, pw = st.text_input("Email:"), st.text_input("Password:", type="password")
    if st.button("Accedi al Registro", use_container_width=True, type="primary"):
        if em in UTENTI and pw == UTENTI[em]: st.session_state["autenticato"] = True; st.rerun()
        else: st.error("❌ Credenziali errate.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

# --- BARRA LATERALE E SWITCH TEMA ---
st.sidebar.markdown("<h2 style='text-align: center; color: #fbbf24 !important;'>📝 EduCorrect AI</h2>", unsafe_allow_html=True)
scelta_tema = st.sidebar.selectbox("🎨 INTERFACCIA SITO:", ["Total Dark", "Light Mode"], index=0 if st.session_state["tema_scelto"] == "Total Dark" else 1)
if scelta_tema != st.session_state["tema_scelto"]: st.session_state["tema_scelto"] = scelta_tema; st.rerun()

modalita = st.sidebar.radio("FUNZIONALITÀ PLANCIA:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])
if st.sidebar.button("🚪 Esci", use_container_width=True, type="secondary"): st.session_state["autenticato"] = False; st.rerun()

# --- LOGICA APPLICAZIONE ---
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
        if not arg: st.error("Inserisci un argomento!")
        else:
            with st.spinner("Generazione in corso..."):
                sys_p = "Sei un assistente didattico esperto per le superiori italiane. Genera quesiti e risposte in italiano ordinati per tipologia, con numerazione progressiva da 1 a N. Inserisci il tag [SOLUZIONI] prima delle soluzioni. No introduzioni, no campi nome/classe."
                user_p = f"Crea una verifica superiore di livello {df} su {arg}. Tipo: {stl}. Numero quesiti: {num}."
                try:
                    risp = client.models.generate_content(model='gemini-2.5-pro', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.5})
                    st.session_state["testo_verifica"] = risp.text; st.success("Generata con successo!")
                except Exception:
                    try:
                        risp = client.models.generate_content(model='gemini-2.5-flash', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.5})
                        st.session_state["testo_verifica"] = risp.text; st.success("Generata con successo (Flash)!")
                    except Exception as e: st.error(f"Errore server: {e}")

    if "testo_verifica" in st.session_state:
        tg = re.sub(r'(?i)^[^1A-Za-z]*(Ecco|Questo|Di seguito|Verifica).*?(\n|\r)+', '', st.session_state['testo_verifica'])
        tg = re.sub(r'(?i)(Nome|Cognome|Alunno|Classe|Data|Istituto|Materia).*?(\[.*?\]|__+)', '', tg)
        tg = re.sub(r'\*\*(.*?)\*\*|\*(.*?)\*', r'<b>\1\2</b>', tg.strip())
        dom, sol = tg.split("[SOLUZIONI]") if "[SOLUZIONI]" in tg else (tg, "Nessuna chiave di correzione.")
        
        i_html = f"<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;font-size:15px;'>Istituto Superiore</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: _________________________________________</td><td style='text-align:right;'>Classe: ________ Sez. ____</td></tr><tr><td style='padding-top:15px;font-size:16px;font-weight:bold;'>Verifica Scritta ({df.capitalize()})</td><td style='padding-top:15px;text-align:right;font-size:16px;font-weight:bold;'>Oggetto: {arg.capitalize()}</td></tr></table>"
        correttore.renderizza_documento_stampa(arg.capitalize(), df.capitalize(), i_html, dom.replace('\n', '<br>'), dom.strip(), sol.strip())

elif modalita == "🔍 Scansiona e Correggi":
    correttore.mostra_interfaccia_correzione(client, types)
