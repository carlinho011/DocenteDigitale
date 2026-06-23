import streamlit as st
import io
import google.generativeai as genai
from reportlab.pdfgen import canvas

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Generatore Verifica", page_icon="📝")
genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNZIONE PDF ---
def genera_pdf(titolo, testo):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595, 842))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, titolo)
    c.setFont("Helvetica", 11)
    
    y = 770
    for linea in testo.split('\n'):
        if y < 50: # Nuova pagina se il testo è lungo
            c.showPage()
            c.setFont("Helvetica", 11)
            y = 800
        c.drawString(50, y, linea)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACCIA ---
st.title("📝 Generatore di Verifiche")
materia = st.text_input("Materia")
argomento = st.text_input("Argomento")
n_domande = st.slider("Numero di domande", 1, 10, 5)

if st.button("Genera Verifica"):
    with st.spinner("Creazione in corso..."):
        prompt = f"Crea una verifica di {materia} su {argomento} composta da {n_domande} domande. Includi anche le risposte corrette alla fine."
        risposta = model.generate_content(prompt).text
        st.session_state["verifica"] = risposta

if "verifica" in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state["verifica"])
    st.download_button(
        label="📥 Scarica PDF",
        data=genera_pdf("Verifica di " + argomento, st.session_state["verifica"]),
        file_name="verifica.pdf"
    )
