import streamlit as st
import os
import base64
from openai import OpenAI

# 1. IMPOSTAZIONI DELLA PAGINA WEB
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")

# Configurazione del client OpenAI
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Inserisci la tua OpenAI API Key:", type="password")

client = OpenAI(api_key=api_key) if api_key else None

# Titolo principale della grafica in italiano
st.title("📝 EduCorrect: Crea e Correggi Verifiche con l'IA")
st.write("Semplifica il tuo lavoro di docente. Genera compiti e correggi le foto delle verifiche in pochi secondi.")

if not api_key:
    st.warning("⚠️ Per far funzionare l'applicazione, inserisci la tua OpenAI API Key nella barra a sinistra.")

# 2. CREAZIONE DELLE SCHEDE (TABS) IN ITALIANO
tab1, tab2 = st.tabs(["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

# ==========================================
# SCHEDA 1: GRAFICA PER CREARE LA VERIFICA
# ==========================================
with tab1:
    st.header("Generatore di Compiti in Classe")
    
    col1, col2 = st.columns(2)
    with col1:
        argomento = st.text_input("Inserisci l'argomento della verifica:", placeholder="Es. I vulcani, La prima guerra mondiale...")
    with col2:
        # AGGIUNTA L'OPZIONE 'DOMANDE MISTE'
        stile_domande = st.selectbox("Tipo di domande:", ["Domande miste (Vero/Falso, Crocette, Aperte)", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    
    numero_domande = st.slider("Numero di domande totali:", min_value=1, max_value=20, value=5)
    
    if st.button("Genera Testo Verifica"):
        if not client:
            st.error("Inserisci prima la tua API Key.")
        elif not argomento:
            st.error("Scrivi un argomento prima di generare!")
        else:
            with st.spinner("L'intelligenza artificiale sta scrivendo il compito in italiano..."):
                try:
                    # Istruzioni forzate in italiano per l'IA
                    prompt_sistema = (
                        "Sei un assistente didattico per professori italiani. "
                        "Devi generare la verifica e le risposte ESATTAMENTE E SOLO IN LINGUA ITALIANA. "
                        "Usa il sistema di valutazione scolastico italiano."
                    )
                    
                    # Logica per gestire le domande miste
                    if stile_domande == "Domande miste (Vero/Falso, Crocette, Aperte)":
                        dettaglio_stile = "strutturata con un mix bilanciato di domande a scelta multipla, quesiti Vero o Falso e domande a risposta aperta."
                    else:
                        dettaglio_stile = f"composta esclusivamente da domande di tipo: {stile_domande}."

                    prompt_utente = (
                        f"Crea una verifica scolastica per le scuole superiori basata su queste indicazioni:\n"
                        f"- Argomento principale: {argomento}\n"
                        f"- Struttura del test: {dettaglio_stile}\n"
                        f"- Numero totale di quesiti: {numero_domande}\n\n"
                        f"Fornisci il testo della verifica pronto da copiare e stampare. "
                        f"In fondo al testo, crea una sezione ben separata chiamata 'CORRETTORE E SOLUZIONI' "
                        f"contenente le risposte esatte per il professore."
                    )
                    
                    risposta = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": prompt_utente}
                        ]
                    )
                    testo_generato = risposta.choices.message.content
                    
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
    
    soluzioni_prof = st.text_area("Incolla qui le soluzioni corrette della verifica (o i criteri di valutazione):")
    foto_caricata = st.file_uploader("Scegli o trascina la foto della verifica (.jpg, .jpeg, .png):", type=["jpg", "jpeg", "png"])
    
    if foto_caricata is not None:
        st.image(foto_caricata, caption="Anteprima del compito dello studente", width=400)
        
    if st.button("Scansiona e Correggi Compito"):
        if not client:
            st.error("Inserisci prima la tua API Key.")
        elif not soluzioni_prof or not foto_caricata:
            st.error("Devi inserire sia le soluzioni sia la foto del compito!")
        else:
            with st.spinner("L'IA sta leggendo la calligrafia e correggendo il compito..."):
                try:
                    bytes_data = foto_caricata.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    
                    # Istruzioni di correzione forzate in italiano con voti italiani
                    prompt_sistema = (
                        "Sei un professore italiano e ti esprimi rigorosamente in lingua italiana. "
                        "Analizza l'immagine della verifica dello studente, decifra la sua scrittura a mano "
                        "e confrontala con le soluzioni fornite. Valuta il compito usando i voti da 1 a 10 "
                        "(puoi usare anche i mezzi voti come 6+, 7.5, 8- se necessario). "
                        "Restituisci la risposta scritta bene in italiano con questa precisa struttura:\n\n"
                        "### 📊 VALUTAZIONE FINALE\n"
                        "**Voto proposto:** [Inserisci voto]\n\n"
                        "### ✅ RISPOSTE CORRETTE\n"
                        "[Elenca cosa ha fatto bene]\n\n"
                        "### ❌ ERRORI RISCONTRATI\n"
                        "[Spiega cosa ha sbagliato e perché]\n\n"
                        "### 💬 NOTA DEL DOCENTE\n"
                        "[Un breve commento in italiano per spiegare lo studente come migliorare]"
                    )
                    
                    risposta = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"Ecco il correttore ufficiale con le soluzioni: {soluzioni_prof}"},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        temperature=0.2
                    )
                    
                    st.success("Correzione Completata!")
                    st.markdown(risposta.choices.message.content)
                except Exception as e:
                    st.error(f"Errore durante la scansione: {str(e)}")
