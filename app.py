import streamlit as st
import os, json

# 1. IMPOSTAZIONI PAGINA E STILE GRAFICO FOGLIO WORD A4
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")
st.markdown("""<style>
    .foglio-word { background-color: #ffffff !important; color: #000000 !important; padding: 50px 60px !important; margin: 20px auto !important; max-width: 800px !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.15) !important; border: 1px solid #d3d3d3 !important; font-family: 'Times New Roman', Times, serif !important; line-height: 1.6 !important; font-size: 16px !important; }
    .tabella-intestazione { width: 100% !important; border-collapse: collapse !important; border-bottom: 2px solid #000000 !important; margin-bottom: 25px !important; font-family: Arial, sans-serif !important; font-size: 14px; }
    .tabella-intestazione td { border: none !important; padding: 6px 0 !important; }
    .salto-pagina { page-break-before: always !important; break-before: page !important; margin-top: 50px !important; border-top: 2px dashed #000000 !important; padding-top: 20px !important; }
    .box-valutazione { border: 2px solid #bf1515 !important; background-color: #fff8f8 !important; padding: 15px 20px !important; margin-bottom: 20px !important; border-radius: 4px !important; }
</style>""", unsafe_allow_html=True)

if "GEMINI_KEY" not in st.secrets:
    st.error("⚠️ Inserisci 'GEMINI_KEY' nei Secrets di Streamlit."); st.stop()

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error(f"Errore SDK Google: {e}"); st.stop()

UTENTI = json.loads(st.secrets["UTENTI_ABILITATI"]) if "UTENTI_ABILITATI" in st.secrets else {"admin@educorrect.it": "AdminPass2026"}
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state: st.session_state["utente_connesso"] = ""

if not st.session_state["autenticato"]:
    st.title("🔒 Area Riservata Docenti - EduCorrect")
    em = st.text_input("Email:")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if em in UTENTI and pw == UTENTI[em]:
            st.session_state["autenticato"], st.session_state["utente_connesso"] = True, em; st.rerun()
        else: st.error("❌ Credenziali errate.")
    st.stop()

st.sidebar.title("🛠️ Menu EduCorrect")
st.sidebar.write(f"👤 Utente: **{st.session_state['utente_connesso']}**")
modalita = st.sidebar.radio("Scegli l'operazione:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

st.sidebar.markdown("---")
if st.sidebar.button("Disconnetti / Esci"):
    st.session_state["autenticato"] = False
    if "testo_verifica" in st.session_state: del st.session_state["testo_verifica"]
    if "analisi_correzione" in st.session_state: del st.session_state["analisi_correzione"]
    st.rerun()

# --- SEZIONE 1: GENERATORE DI VERIFICHE ---
if modalita == "🚀 Genera Nuova Verifica":
    st.header("Generatore di Compiti in Classe")
    col1, col2, col3 = st.columns(3)
    with col1: argomento = st.text_input("Argomento:", placeholder="Es. I vulcani...")
    with col2: stile = st.selectbox("Tipo:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3: diff = st.selectbox("Difficoltà:", ["facile", "media", "difficile"])
    num = st.slider("Numero domande:", 1, 20, 5)
    
    if st.button("Genera Testo Verifica"):
        if not argomento: st.error("Scrivi un argomento!")
        else:
            with st.spinner("Generazione con Gemini in corso..."):
                sys_p = "Sei un assistente didattico esperto per le superiori italiane. Genera la verifica e le risposte in italiano. Inserisci obbligatoriamente il tag [SOLUZIONI] subito prima di scrivere le chiavi di correzione."
                user_p = "Crea una verifica superiore di livello " + diff + " su " + argomento + ". Tipo: " + stile + ". Numero quesiti: " + str(num) + "."
                try:
                    risp = client.models.generate_content(model='gemini-2.5-flash', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.6})
                    st.session_state["testo_verifica"] = risp.text; st.success("Verifica generata!")
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower() or "exhausted" in str(e).lower():
                        st.warning("⚠️ Linea principale satura. Switch automatico su Gemini Pro...")
                        try:
                            risp = client.models.generate_content(model='gemini-2.5-pro', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.6})
                            st.session_state["testo_verifica"] = risp.text; st.success("Generata su linea Pro!")
                        except Exception as final_err: st.error("❌ Server saturi: " + str(final_err))
                    else: st.error("⚠️ Errore: " + str(e))

    if "testo_verifica" in st.session_state:
        tg = st.session_state['testo_verifica']
        st.write("### 📄 Esporta Documento")
        fn = "verifica_" + diff + "_" + argomento.lower().replace(' ', '_') + ".pdf"
        btn_js = "<div style='margin-bottom:20px;'><button onclick='scaricaFilePDF()' style='background-color:#2e7d32;color:white;padding:14px 28px;border:none;border-radius:6px;cursor:pointer;font-size:16px;font-weight:bold;box-shadow:0 4px 6px rgba(0,0,0,0.15);'>📥 Scarica Verifica in PDF</button></div><script src='https://cloudflare.com'></script><script>function scaricaFilePDF() { var target = window.parent.document.getElementById('blocco-foglio-word-target'); if (!target) { alert('Attendi il caricamento.'); return; } html2pdf().set({ margin:12, filename:'" + fn + "', image:{type:'jpeg',quality:0.98}, html2canvas:{scale:2,useCORS:true}, jsPDF:{unit:'mm',format:'a4',orientation:'portrait'} }).from(target).save(); }</script>"
        st.components.v1.html(btn_js, height=75)
        c_html = tg.replace('\n', '<br>').replace("[SOLUZIONI]", "<div class='salto-pagina'><h3 style='color:#000000;border-bottom:2px solid #000000;padding-bottom:5px;'>🔑 CHIAVE DI CORREZIONE (DOCENTE)</h3><br>") + "</div>"
        i_html = "<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;'>Istituto Superiore</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: _________________________________</td><td style='text-align:right;'>Classe: ________ Sez. ____</td></tr><tr><td style='padding-top:10px;font-size:16px;font-weight:bold;'>Verifica scritta (" + diff.capitalize() + ")</td><td style='padding-top:10px;text-align:right;font-size:16px;font-weight:bold;'>Oggetto: " + argomento.capitalize() + "</td></tr></table>"
        st.markdown("<div id='blocco-foglio-word-target' class='foglio-word'>" + i_html + c_html + "</div>", unsafe_allow_html=True)

# --- SEZIONE 2: SCANSIONA E CORREGGI ---
elif modalita == "🔍 Scansiona e Correggi":
    st.header("🔍 Correttore Intelligente di Compiti")
    st.write("Inserisci l'elaborato tramite scatto foto, allegato o testo.")
    col_in, col_cr = st.columns(2)
    with col_in:
        foto = st.camera_input("📸 OPZIONE A: Scatta foto ora:")
        file_c = st.file_uploader("📂 OPZIONE B: Carica file o foto galleria:", type=["png", "jpg", "jpeg", "pdf"])
        testo_m = st.text_area("✍️ OPZIONE C: Incolla testo elaborato:", height=100, placeholder="Risposte dello studente...")
    with col_cr: griglia = st.text_area("🔑 Criteri o soluzioni di riferimento:", value=st.session_state.get("testo_verifica", ""), height=260)

    if st.button("🔎 Avvia Correzione Automatica"):
        if not foto and not file_c and not testo_m: st.error("Inserisci un compito per procedere!")
        else:
            with st.spinner("Lettura elaborato e correzione in corso..."):
                sys_c = "Sei un docente superiore italiano. Analizza il compito (testo o immagine) confrontandolo con i criteri. Restituisci l'analisi in italiano. Inserisci all'inizio il tag [VALUTAZIONE_BOX] seguito da: VOTO IN DECIMI (2-10) e NOTA MOTIVAZIONALE breve. Subito dopo scrivi il tag [DETTAGLIO] e inserisci la spiegazione degli errori."
                req = []
                visivo = foto if foto else file_c
                if visivo: req.append(types.Part.from_bytes(data=visivo.read(), mime_type=visivo.type if hasattr(visivo, 'type') else "image/png"))
                req.append("Compito studente:\n" + testo_m + "\n\nCriteri:\n" + griglia)
                try:
                    risp = client.models.generate_content(model='gemini-2.5-flash', contents=req, config={'system_instruction': sys_c, 'temperature': 0.4})
                    st.session_state["analisi_correzione"] = risp.text; st.success("Correzione completata!")
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower() or "exhausted" in str(e).lower():
                        st.warning("⚠️ Quota esaurita. Passaggio a Gemini Pro...")
                        try:
                            risp = client.models.generate_content(model='gemini-2.5-pro', contents=req, config={'system_instruction': sys_c, 'temperature': 0.4})
                            st.session_state["analisi_correzione"] = risp.text; st.success("Corretto con linea Pro!")
                        except Exception as err2: st.error("❌ Server saturi: " + str(err2))
                    else: st.error("⚠️ Errore: " + str(e))
                    
    if "analisi_correzione" in st.session_state:
        st.write("### 📄 Esporta Relazione di Valutazione")
