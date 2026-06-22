import streamlit as st

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="wide")

# --- GESTIONE AUTH ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state: st.session_state["nome_docente"] = ""

if not st.session_state["autenticato"]:
    st.markdown("<div style='max-width: 400px; margin: 80px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.title("🔒 Accesso Docente")
    nome = st.text_input("Inserisci il tuo Nome:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome.strip() != "":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else:
            st.error("❌ Password errata o nome mancante.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- BARRA LATERALE ---
st.sidebar.markdown(f"## 👤 Prof. {st.session_state['nome_docente']}")
st.sidebar.divider()
funzione = st.sidebar.radio("Seleziona la modalità:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])
if st.sidebar.button("🚪 Disconnetti"):
    st.session_state["autenticato"] = False
    st.rerun()

# --- LOGICA GENERAZIONE ---
if funzione == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore di Verifiche")
    
    with st.form("form_verifica"):
        col1, col2 = st.columns(2)
        with col1:
            materia = st.text_input("Materia:")
            argomento = st.text_input("Argomento:")
        with col2:
            tipologia = st.selectbox("Tipologia Quesiti:", ["Vero/Falso", "Scelta multipla", "Risposte aperte", "Miste"])
            difficolta = st.select_slider("Difficoltà:", options=["Facile", "Media", "Difficile"])
        
        num_domande = st.number_input("Numero di domande:", min_value=1, max_value=20, value=5)
        submitted = st.form_submit_button("Genera Verifica")

    if submitted:
        if materia and argomento:
            st.success(f"Sto generando una verifica di {materia} su {argomento} ({tipologia}, {difficolta})...")
            # Qui inserirai la logica di chiamata all'API Gemini
        else:
            st.error("Per favore, compila tutti i campi obbligatori.")

elif funzione == "🔍 Scansiona e Correggi":
    st.title("🔍 Centro Correzione")
    st.write("Carica qui i compiti da correggere.")
