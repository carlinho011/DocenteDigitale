import streamlit as st
import os
import io
from google import genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="EduCorrect AI", page_icon="📝")

# --- CSS E LOGIN ---
# (Inserisci qui il caricamento stile.css e la logica di login precedente)
# [OMESSO PER BREVITÀ, USA QUELLO DEL MESSAGGIO PRECEDENTE]

def genera_pdf_verifica(dati):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Correzione Verifica: {dati['nome']} - {dati['classe']}")
    c.setFont("Helvetica", 12)
    # Logica icone: c.drawString(50, 750, "✅ Domanda 1: Corretta")
    c.save()
    buffer.seek(0)
    return buffer

def genera_griglia_voti(dati):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(50, 800, "Griglia di Valutazione")
    # Qui inseriresti la tabella con i punteggi per tipo
    c.save()
    buffer.seek(0)
    return buffer

# --- LOGICA CORREZIONE ---
if funzione == "🔍 Correggi":
    st.title("🔍 Centro Correzione")
    
    # 1. Input: Foto o PDF
    scelta = st.radio("Come vuoi inserire il compito?", ["Carica File", "Scatta Foto"])
    file = st.camera_input("Scatta") if scelta == "Scatta Foto" else st.file_uploader("Carica PDF/Foto", type=["jpg", "png", "pdf"])

    if file and st.button("Analizza e Correggi"):
        with st.spinner("L'IA sta analizzando il compito..."):
            try:
                # 2. Analisi IA
                client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                # Conversione immagine in formato leggibile da Gemini
                img_bytes = file.getvalue()
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        {"mime_type": "image/jpeg", "data": img_bytes},
                        "Estrai Nome, Data, Classe. Correggi ogni domanda mettendo ✅ per corrette e ❌ per errate. Calcola voto 1/10 e scrivi un commento per l'alunno."
                    ]
                )
                
                # Simulazione estrazione dati (In produzione, parserizza il JSON di risposta)
                dati = {"nome": "Studente", "classe": "3A", "voto": 8, "commento": "Bravo!"}
                
                # 3. Generazione PDF
                st.success("Correzione completata!")
                st.download_button("Scarica Verifica Corretta (PDF)", genera_pdf_verifica(dati), "verifica.pdf")
                st.download_button("Scarica Griglia Voti (PDF)", genera_griglia_voti(dati), "griglia.pdf")
                
            except Exception as e:
                st.error(f"Errore durante l'analisi: {e}")
