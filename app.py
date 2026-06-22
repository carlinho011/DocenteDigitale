import streamlit as st
from google import genai

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EduCorrect AI", page_icon="📝", layout="wide")

# --- STATO SESSIONE ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "nome_docente" not in st.session_state: st.session_state["nome_docente"] = ""
if "risposta_ia" not in st.session_state: st.session_state["risposta_ia"] = ""

# --- LOGIN ---
if not st.session_state["autenticato"]:
    st.markdown("<div style='max-width: 400px; margin: 80px auto; padding: 40px; background: #f8fafc; border-radius: 12px;'>", unsafe_allow_html=True)
    st.title("🔒 Accesso")
    nome = st.text_input("Nome Docente:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI" and nome.strip() != "":
            st.session_state.update({"autenticato": True, "nome_docente": nome})
            st.rerun()
        else:
            st.error("Credenziali errate o nome mancante.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- INTERFACCIA PRINCIPALE ---
st.sidebar.markdown(f"## 👤 Prof. {st.session_state['nome_docente']}")
funzione = st.sidebar.radio("Navigazione:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])
if st.sidebar.button("🚪 Disconnetti"):
    st.session_state.clear()
    st.rerun()

# --- LOGICA GENERAZIONE (VELOCE) ---
if funzione == "🚀 Genera Nuova Verifica":
    st.title("🚀 Generatore Rapido")
    
    with st.form("form_gen"):
        col1, col2 = st.columns(2)
        materia = col1.text_input("Materia:")
        argomento = col2.text_input("Argomento:")
        tipologia = st.selectbox("Tipologia:", ["Vero/Falso", "Scelta multipla", "Risposte aperte", "Miste"])
        diff = st.select_slider("Difficoltà:", ["Facile", "Media", "Difficile"])
        num = st.number_input("Numero domande:", 1, 20, 5)
        submitted = st.form_submit_button("Genera Istantaneamente")

    if submitted:
        client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
        prompt = f"Crea una verifica di {materia} su {argomento}. Tipo: {tipologia}, Difficoltà: {diff}, Numero domande: {num}. Inserisci [SOLUZIONI] alla fine."
        
        st.session_state["risposta_ia"] = ""
        placeholder = st.empty()
        
        # Stream per velocità massima
        stream = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        for chunk in stream:
            st.session_state["risposta_ia"] += chunk.text
            placeholder.markdown(st.session_state["risposta_ia"])

elif funzione == "🔍 Scansiona e Correggi":
    st.title("🔍 Centro Correzione")
    st.info("Funzionalità in fase di ottimizzazione.")

# --- MANTENIMENTO RISULTATO ---
if st.session_state["risposta_ia"]:
    st.markdown("---")
    st.markdown(st.session_state["risposta_ia"])
