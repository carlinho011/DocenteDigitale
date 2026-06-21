# --- FUNZIONE PER CARICARE IL CSS DA FILE ESTERNO ED EMERGENZA SFONDO ---
def carica_css(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Forza lo sfondo animato via HTML puro se il CSS esterno viene bloccato
    st.markdown("""
        <style>
            @keyframes gradienteDinamico {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            html, body, [data-testid="stAppViewContainer"], .stApp {
                background: linear-gradient(-45deg, #070a12, #14113c, #0a0f1d, #01030a) !important;
                background-size: 400% 400% !important;
                animation: gradienteDinamico 16s ease infinite !important;
                background-image: 
                    linear-gradient(rgba(255, 255, 255, 0.012) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.012) 1px, transparent 1px),
                    radial-gradient(rgba(99, 102, 241, 0.18) 1.2px, transparent 1.2px) !important;
                background-size: 45px 45px, 45px 45px, 22px 22px !important;
                background-position: 0 0, 0 0, 11px 11px !important;
                background-attachment: fixed !important;
            }
            header, [data-testid="stHeader"] {
                display: none !important;
                visibility: hidden !important;
                height: 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)
