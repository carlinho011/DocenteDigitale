import streamlit as st
import os
import base64
from openai import OpenAI

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# Configurazione del client OpenAI
# Legge la chiave inserita nei segreti del sito o in una casella di testo
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    # Se non trova la chiave nel sistema, mostra un campo sulla barra laterale del sito
    api_key = st.sidebar.text_input("Inserisci la tua OpenAI API Key:", type="password")

client = OpenAI(api_key=api_key) if api_key else None

# Titolo principale della grafica
st.title("📝 EduCorrect: Crea e Correggi Verifiche con l'IA")
st.write("Semplifica il tuo lavoro di docente. Genera compiti e correggi le foto delle verifiche in pochi secondi.")

if not api_key:
    st.warning("⚠️ Per far funzionare l'applicazione, inserisci la tua OpenAI API Key nella barra a sinistra.")

# 2. CREAZIONE DELLE SCHEDE (TABS) NELLA GRAFICA
tab1, tab2 = st.tabs(["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

# ==========================================
# SCHEDA 1: GRAFICA PER CREARE LA VERIFICA
# ==========================================
with tab1:
    st.header("Generatore di Compiti in Classe")
    
    # Elementi grafici di input
    col1, col2 = st.columns(2)
    with col1:
        argomento = st.text_input("Inserisci l'argomento della verifica:", placeholder="Es. I vulcani, La prima guerra mondiale...")
    with col2:
        stile_domande = st.selectbox("Tipo di domande:", ["Risposte aperte", "Scelta multipla", "Vero o Falso"])
    
    numero_domande = st.slider("Numero di domande:", min_value=1, max_value=20, value=5)
    
    # Bottone per attivare l'IA
    if st.button("Genera Testo Verifica"):
        if not client:
            st.error("Inserisci prima la tua API Key.")
        elif not argomento:
            st.error("Scrivi un argomento prima di generare!")
        else:
            with st.spinner("L'intelligenza artificiale sta scrivendo il compito..."):
                try:
                    prompt_sistema = "Sei un assistente didattico per professori. Crea una verifica scolastica chiara e adatta alle superiori."
                    prompt_utente = f"Crea una verifica su: {argomento}. Tipo: {stile_domande}. Domande: {numero_domande}. Includi in fondo le soluzioni."
                    
                    risposta = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": prompt_utente}
                        ]
                    )
                    testo_generato = risposta.choices.message.content
                    
                    # Mostra il risultato dentro un box di testo nella grafica
                    st.success("Verifica Generata con Successo!")
                    st.text_area("Copia il testo qui sotto:", value=testo_generato, height=400)
                except Exception as e:
                    st.error(f"Errore: {str(e)}")

# ==========================================
# SCHEDA 2: GRAFICA PER SCANSIONARE LA FOTO
# ==========================================
with tab2:
    st.header("Scanner e Correttore Automatico")
    st.write("Carica la foto o la scansione del foglio scritto a mano dallo studente.")
    
    # Elementi grafici di input
    soluzioni_prof = st.text_area("Incolla qui le soluzioni corrette della verifica (o i criteri di valutazione):")
    foto_caricata = st.file_uploader("Scegli o trascina la foto della verifica (.jpg, .jpeg, .png):", type=["jpg", "jpeg", "png"])
    
    # Se il prof carica una foto, la mostra a schermo nella grafica
    if foto_caricata is not None:
        st.image(foto_caricata, caption="Anteprima del compito dello studente", width=400)
        
    # Bottone per attivare la correzione visiva
    if st.button("Scansiona e Correggi Compito"):
        if not client:
            st.error("Inserisci prima la tua API Key.")
        elif not soluzioni_prof or not foto_caricata:
            st.error("Devi inserire sia le soluzioni sia la foto del compito!")
        else:
            with st.spinner("L'IA sta leggendo la calligrafia e correggendo il compito..."):
                try:
                    # Convertiamo la foto caricata in base64 per l'IA
                    bytes_data = foto_caricata.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    
                    prompt_sistema = (
                        "Sei un professore digitale. Leggi la scrittura sullo studente nella foto, "
                        "confrontala con le soluzioni e restituisci: VOTO FINALE (1-10), ERRORI TROVATI e CONSIGLIO."
                    )
                    
                    risposta = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"Soluzioni: {soluzioni_prof}"},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        temperature=0.2
                    )
                    
                    # Mostra l'esito della correzione nella grafica
                    st.success("Correzione Completata!")
                    st.markdown(risposta.choices.message.content)
                except Exception as e:
                    st.error(f"Errore durante la scansione: {str(e)}")
