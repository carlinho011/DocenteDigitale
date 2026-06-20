elif modalita == "🔍 Scansiona e Correggi":
    st.header("🔍 Correttore Intelligente di Compiti")
    col_in, col_cr = st.columns(2)
    with col_in:
        foto = st.camera_input("📸 OPZIONE A:")
        file_c = st.file_uploader("📂 OPZIONE B:", type=["png", "jpg", "jpeg", "pdf"])
        testo_m = st.text_area("✍️ OPZIONE C:", height=100, placeholder="Risposte studente...")
    with col_cr: griglia = st.text_area("🔑 Criteri di riferimento:", value=st.session_state.get("testo_verifica", ""), height=260)

    if st.button("🔎 Avvia Correzione Automatica"):
        if not foto and not file_c and not testo_m: st.error("Inserisci un compito!")
        else:
            with st.spinner("Correzione in corso..."):
                sys_c = "Sei un docente superiore italiano. Analizza il compito confrontandolo con i criteri. Restituisci l'analisi in italiano. MATEMATICA: Non usare delimitatori LaTeX, esprimi i calcoli e i simboli matematici con caratteri Unicode/HTML leggibili (es. x², √, ±, ≠, ÷). Inserisci all'inizio il tag [VALUTAZIONE_BOX] seguito da: VOTO IN DECIMI e NOTA MOTIVAZIONALE breve. Subito dopo inserisci il corpo dettagliato della correzione."
                contenuto_input = [f"Criteri:\n{griglia}\n\nCompito studente:"]
                if testo_m: contenuto_input.append(testo_m)
                if foto: contenuto_input.append(foto)
                if file_c: contenuto_input.append(file_c)
                
                try:
                    risp = client.models.generate_content(model='gemini-2.5-pro', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                    st.session_state["analisi_correzione"] = risp.text; st.success("Correzione completata con Pro!")
                except Exception as e:
                    if any(x in str(e).lower() for x in ["429", "quota", "exhausted"]):
                        st.warning("⚠️ Linea Pro satura. Switch su Gemini Flash...")
                        try:
                            risp = client.models.generate_content(model='gemini-2.5-flash', contents=contenuto_input, config={'system_instruction': sys_c, 'temperature': 0.3})
                            st.session_state["analisi_correzione"] = risp.text; st.success("Correzione completata con Flash!")
                        except Exception as final_err: st.error(f"❌ Server saturi: {final_err}")
                    else: st.error(f"⚠️ Errore: {e}")

    # INTEGRATO E INDENTATO ALL'INTERNO DI ELIF: Non uscirà più dai box
    if "analisi_correzione" in st.session_state:
        cx = st.session_state["analisi_correzione"]
        if "[VALUTAZIONE_BOX]" in cx:
            pt = cx.split("[VALUTAZIONE_BOX]")
            t_ut = pt[1] if len(pt) > 1 else cx
            pg = t_ut.split("\n\n")
            p_p = pg[0] if len(pg) > 0 else ""
            c_est = "\n\n".join(pg[1:]) if len(pg) > 1 else ""
            st.markdown(f"<div class='box-valutazione'><h3>📊 Valutazione Docente</h3>{p_p.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
            if c_est: st.markdown(f"<div class='foglio-word'><h3>🔍 Analisi di Correzione</h3><br>{c_est.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='foglio-word'>{cx.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
