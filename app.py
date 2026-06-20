import streamlit as st
import os, json

# 1. IMPOSTAZIONI PAGINA E STILE GRAFICO FOGLIO WORD A4
st.set_page_config(page_title="EduCorrect - AI per Professori", page_icon="📝", layout="wide")
st.markdown("""<style>
    .foglio-word { background-color: #ffffff !important; color: #000000 !important; padding: 50px 60px !important; margin: 20px auto !important; max-width: 800px !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.15) !important; border: 1px solid #d3d3d3 !important; font-family: 'Times New Roman', Times, serif !important; line-height: 1.6 !important; font-size: 16px !important; }
    .tabella-intestazione { width: 100% !important; border-collapse: collapse !important; border-bottom: 2px solid #000000 !important; margin-bottom: 25px !important; font-family: Arial, sans-serif !important; font-size: 14px; }
    .tabella-intestazione td { border: none !important; padding: 6px 0 !important; }
    .salto-pagina { page-break-before: always !important; break-before: page !important; margin-top: 50px !important; border-top: 2px dashed #000000 !important; padding-top: 20px !important; }
    .box-valutazione { border: 2px solid #bf1515 !important; background-color: #fff8f8 !important; padding: 15px 20px !important; margin-bottom: 20px !important; border-radius: 4px !important; font-family: Arial, sans-serif !important; }
</style>""", unsafe_allow_html=True)

if "GEMINI_KEY" not in st.secrets: st.error("⚠️ Inserisci 'GEMINI_KEY' nei Secrets."); st.stop()
try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
except Exception as e: st.error(f"Errore SDK: {e}"); st.stop()

UTENTI = json.loads(st.secrets["UTENTI_ABILITATI"]) if "UTENTI_ABILITATI" in st.secrets else {"admin@educorrect.it": "AdminPass2026"}
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "utente_connesso" not in st.session_state: st.session_state["utente_connesso"] = ""
if "registro_voti" not in st.session_state: st.session_state["registro_voti"] = []

if not st.session_state["autenticato"]:
    st.title("🔒 Area Riservata Docenti - EduCorrect")
    em, pw = st.text_input("Email:"), st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if em in UTENTI and pw == UTENTI[em]: st.session_state["autenticato"], st.session_state["utente_connesso"] = True, em; st.rerun()
        else: st.error("❌ Credenziali errate.")
    st.stop()

st.sidebar.title("🛠️ Menu EduCorrect")
st.sidebar.write(f"👤 Utente: **{st.session_state['utente_connesso']}**")
modalita = st.sidebar.radio("Scegli l'operazione:", ["🚀 Genera Nuova Verifica", "🔍 Scansiona e Correggi"])

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Registro Voti Sessione")
if st.session_state["registro_voti"]:
    for item in st.session_state["registro_voti"]:
        st.sidebar.info(f"📋 {item['studente']} - {item['argomento']} -> **Voto: {item['voto']}**")
    if st.sidebar.button("🗑️ Svuota Registro"): st.session_state["registro_voti"] = []; st.rerun()
else: st.sidebar.write("*Nessun voto registrato.*")

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
    with col1: argomento = st.text_input("Argomento:", placeholder="Es. Equazioni di secondo grado...")
    with col2: stile = st.selectbox("Tipo:", ["Domande miste", "Risposte aperte", "Scelta multipla", "Vero o Falso"])
    with col3: diff = st.selectbox("Difficoltà:", ["facile", "media", "difficile"])
    num = st.slider("Numero domande:", 1, 20, 5)
    
    if st.button("Genera Testo Verifica"):
        if not argomento: st.error("Scrivi un argomento!")
        else:
            with st.spinner("Generazione in corso..."):
                sys_p = "Sei un assistente didattico esperto per le superiori italiane. Genera la verifica e le risposte in italiano. IMPORTANTE MATEMATICA: NON usare codice LaTeX con $ o $$. Scrivi le formule e i simboli usando i caratteri Unicode estesi o entità matematiche leggibili in HTML (es. usare x², √x, ±, ≠, ≤, ≥, ÷, ×, ∫, λ, π, ½, ¼, ∛). Per le frazioni scrivi numeratore/denominatore o usa la linea orizzontale. Inserisci il tag [SOLUZIONI] subito prima delle chiavi di correzione."
                user_p = f"Crea una verifica superiore di livello {diff} su {argomento}. Tipo: {stile}. Numero quesiti: {num}."
                try:
                    risp = client.models.generate_content(model='gemini-2.5-pro', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.6})
                    st.session_state["testo_verifica"] = risp.text; st.success("Verifica generata!")
                except Exception as e:
                    if any(x in str(e).lower() for x in ["429", "quota", "exhausted"]):
                        st.warning("⚠️ Linea Pro satura. Switch su Gemini Flash...")
                        try:
                            risp = client.models.generate_content(model='gemini-2.5-flash', contents=user_p, config={'system_instruction': sys_p, 'temperature': 0.6})
                            st.session_state["testo_verifica"] = risp.text; st.success("Generata su linea Flash!")
                        except Exception as final_err: st.error(f"❌ Server saturi: {final_err}")
                    else: st.error(f"⚠️ Errore generico: {e}")

    if "testo_verifica" in st.session_state:
        tg = st.session_state['testo_verifica']
        fn = f"verifica_{diff}_{argomento.lower().replace(' ', '_')}.pdf"
        btn_js = "<div style='margin-bottom:20px;'><button onclick='scaricaFilePDF()' style='background-color:#2e7d32;color:white;padding:14px 28px;border:none;border-radius:6px;cursor:pointer;font-size:16px;font-weight:bold;box-shadow:0 4px 6px rgba(0,0,0,0.15);'>📥 Scarica PDF</button></div><script src='https://cloudflare.com'></script><script>function scaricaFilePDF() { var target = window.parent.document.getElementById('blocco-foglio-word-target'); if (!target) { alert('Attendi il caricamento.'); return; } html2pdf().set({ margin:12, filename:'" + fn + "', image:{type:'jpeg',quality:0.98}, html2canvas:{scale:2,useCORS:true}, jsPDF:{unit:'mm',format:'a4',orientation:'portrait'} }).from(target).save(); }</script>"
        st.components.v1.html(btn_js, height=75)
        c_html = tg.replace('\n', '<br>').replace("[SOLUZIONI]", "<div class='salto-pagina'><h3 style='color:#000000;border-bottom:2px solid #000000;padding-bottom:5px;'>🔑 CHIAVE DI CORREZIONE</h3><br>") + "</div>"
        i_html = f"<table class='tabella-intestazione'><tr><td style='width:60%;font-weight:bold;'>Istituto Superiori</td><td style='width:40%;text-align:right;font-weight:bold;'>Data: ____/____/________</td></tr><tr><td>Alunno/a: ___________________________</td><td style='text-align:right;'>Classe: ____ Sez. __</td></tr><tr><td style='padding-top:10px;font-size:16px;font-weight:bold;'>Verifica scritta ({diff.capitalize()})</td><td style='padding-top:10px;text-align:right;font-size:16px;font-weight:bold;'>Oggetto: {argomento.capitalize()}</td></tr></table>"
        st.markdown(f"<div id='blocco-foglio-word-target' class='foglio-word'>{i_html}{c_html}</div>", unsafe_allow_html=True)

# --- SEZIONE 2: SCANSIONA E CORREGGI ---
elif modalita == "🔍 Scansiona e Correggi":
    st.header("🔍 Correttore Intelligente di Compiti")
    col_stud, col_arg = st.columns(2)
    with col_stud: nome_alunno = st.text_input("Nome Alunno/a:", placeholder="Es. Mario Rossi")
    with col_arg: arg_compito = st.text_input("Materia o Argomento:", placeholder="Es. Matematica")
    col_in, col_cr = st.columns(2)
    with col_in:
        foto = st.camera_input("📸 OPZIONE A:")
        file_c = st.file_uploader("📂 OPZIONE B:", type=["png", "jpg", "jpeg", "pdf"])
        testo_m = st.text_area("✍️ OPZIONE C:", height=100)
    with col_cr: griglia = st.text_area("🔑 Criteri di riferimento:", value=st.session_state.get("testo_verifica", ""), height=260)

    if st.button("🔎 Avvia Correzione Automatica"):
        if not foto and not file_c and not testo_m: st.error("Inserisci un compito!")
        elif not nome_alunno or not arg_compito: st.error("Compila nome e argomento!")
        else:
            with st.spinner("Correzione in corso..."):
                sys_c = "Sei un docente superiore italiano. Analizza il compito confrontandolo con i criteri. Restituisci l'analisi in italiano. MATEMATICA: Non usare delimitatori LaTeX, esprimi i calcoli e i simboli matematici con caratteri Unicode/HTML leggibili (es. x², √, ±, ≠, ÷). Inserisci all'inizio il tag [VALUTAZIONE_BOX] seguito da: VOTO IN DECIMI e NOTA MOTIVAZIONALE breve. Subito dopo inserisci il corpo dettagliato della correzione."
                contenuto_input = [f"Criteri:\n{griglia}\n\nCompito:\nAlunno: {nome_alunno}\nOggetto: {arg_compito}"]
                if testo_m: contenuto_input.append(testo_m)
                if foto: contenuto_input.append(types.Part.from_bytes(data=foto.getvalue(), mime_type="image/jpeg"))
                if file_c:
                    m_type = "application/pdf" if file_c.name.endswith(".pdf") else "image/jpeg"
                    contenuto_input.append(types.Part.from_bytes(data=file_c.getvalue(), mime_type=m_type))
                
                # LOGICA DI FALLBACK CORRETTA (Senza blocchi asimmetrici o SyntaxError)
                modello_selezionato = 'gemini-2.5-pro'
                try:
                    risp = client.models.generate_content(model=modello_selezionato, contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
