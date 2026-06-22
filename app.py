import streamlit as st
import os
import io
from google import genai
from google.genai import types
from reportlab.pdfgen import canvas

st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# --- CSS ---
if os.path.exists("stile.css"):
    with open("stile.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- LOGIN ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if not st.session_state["autenticato"]:
    st.title("Area Riservata 💜")
    pw = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if pw == "MATTEI":
            st.session_state.update({"autenticato": True, "nome_docente": "Docente"})
            st.rerun()
    st.stop()

# --- FUNZIONE CHIAMATA API SICURA ---
def chiama_gemini(prompt, file_part=None):
    client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
    models = ["gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model in models:
        try:
            contents = [file_part, prompt] if file_part else [prompt]
            return client.models.generate_content(model=model, contents=contents)
        except Exception as e:
            if "429" in str(e): continue # Prova il modello successivo
            raise e
    return None

# --- APP ---
st.sidebar.title("EduCorrect AI")
funzione = st.sidebar.radio("Menu", ["🚀 Genera Verifica", "🔍 Correggi"])

if funzione == "🚀 Genera Verifica":
    st.title("🚀 Genera Verifica")
    materia = st.text_input("Materia")
    argomento = st.text_input("Argomento")
    if st.button("Genera"):
        try:
            res = chiama_gemini(f"Crea verifica di {materia} su {argomento}")
            st.markdown(res.text)
        except Exception as e:
            st.error(f"Errore: {e}")

elif funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    file = st.file_uploader("Carica", type=["jpg", "png", "pdf"])
    if file and st.button("Analizza"):
        try:
            mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
            file_part = types.Part.from_bytes(data=file.getvalue(), mime_type=mime)
            res = chiama_gemini("Correggi questo compito e dai un voto 1/10.", file_part)
            st.success("Analisi completata!")
            st.write(res.text)
        except Exception as e:
            st.error("Quota esaurita su tutti i modelli. Riprova più tardi.")
