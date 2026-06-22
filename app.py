import streamlit as st
from google import genai

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="wide")

# --- INIZIALIZZAZIONE SESSIONE ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state: st.session_state["nome_docente"] = ""
if "risposta_ia" not in st.session_state: st.session_state["risposta_ia"] = ""

# --- LOGICA DI LOGIN ---
if not st.session_state["autenticato"]:
    st.markdown("<div style='max-width: 400px; margin: 80px auto; padding: 40px; background: #f8fafc; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.title("🔒 Accesso Docente")
    nome = st.text_input("Inserisci il tuo Nome:")
    pw = st.text_input("Password:", type="password")
    
    if st.button("Accedi"):
        if pw == "MATTEI" and nome.strip() != "":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else:
            st.error("❌ Credenziali errate o nome mancante.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- BARRA LATERALE ---
st.sidebar.markdown(f"## 👤 Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])
if st.sidebar.button("🚪 Disconnetti"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- INTERFACCIA PRINCIPALE ---
if funzione == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore di Verifiche")
    
    with st.form("form_gen"):
        col1, col2 = st.columns(2)
        materia = col1.text_input("Materia:", placeholder="Es. Storia")
        argomento = col2.text_input("Argomento:", placeholder="Es. Rivoluzione Francese")
        tipologia = st.selectbox("Tipologia:", ["Vero/Falso", "Scelta multipla", "Risposte aperte", "Miste"])
        diff = st.select_slider("Difficoltà:", ["Facile", "Media", "Difficile"])
        num = st.number_input("Numero domande:", 1, 20, 5)
        submitted = st.form_submit_button("Genera Verifica")

    if submitted:
        if "GEMINI_KEY" not in st.secrets:
            st.error("⚠️ Errore: GEMINI_KEY non trovata nei Secrets di Streamlit.")
        else:
            try:
                with st.spinner("Generazione in corso..."):
                    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                    prompt = f"Crea una verifica di {materia} su {argomento}. Tipo: {tipologia}, Difficoltà: {diff}, Numero domande: {num}. Inserisci [SOLUZIONI] alla fine."
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                    st.session_state["risposta_ia"] = response.text
            except Exception as e:
                st.error(f"Errore durante la generazione: {e}")

    if st.session_state["risposta_ia"]:
        st.markdown("---")
        st.markdown(st.session_state["risposta_ia"])

elif funzione == "🔍 Scansiona e Correggi":
    st.title("🔍 Centro Correzione")
    st.info("Funzionalità in sviluppo.")
