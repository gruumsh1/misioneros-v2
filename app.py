# ============================================
# TARJETA 3: REGISTRO (primero la acción)
# ============================================
with st.container(border=True):
    st.markdown("### Anotar a mi familia")

    fechas_ocupadas = set(registros_por_fecha.keys())
    fechas_disponibles = [
        datetime.date(anio_sel, mes_sel, d)
        for d in range(1, dias_mes + 1)
        if datetime.date(anio_sel, mes_sel, d).weekday() != 0
        and str(datetime.date(anio_sel, mes_sel, d)) not in fechas_ocupadas
    ]

    if not fechas_disponibles:
        st.warning("No quedan días disponibles este mes. Revise el siguiente mes.")
    else:
        with st.form("form_registro", clear_on_submit=True):
            st.markdown("**Día disponible** (toque el campo para abrir el calendario)")
            f_fecha = st.date_input(
                "Día",
                min_value=datetime.date(anio_sel, mes_sel, 1),
                max_value=datetime.date(anio_sel, mes_sel, dias_mes),
                value=fechas_disponibles[0],
                label_visibility="collapsed",
            )
            f_nombre = st.text_input("Nombre de la familia o persona")
            f_tel = st.text_input("Teléfono de WhatsApp")
            f_notas = st.text_area("Nota opcional (hora acordada, restricciones)")

            enviado = st.form_submit_button("Guardar mi registro", type="primary", use_container_width=True)

            if enviado:
                if not f_nombre.strip() or not f_tel.strip():
                    st.error("Escriba al menos su nombre y su teléfono.")
                elif f_fecha.weekday() == 0:
                    st.error("Los lunes son día de descanso. Elija otro día.")
                elif str(f_fecha) in fechas_ocupadas:
                    st.error("Ese día ya está ocupado. Elija otro día libre.")
                else:
                    try:
                        supabase.table("comidas_misioneros").insert({
                            "companerismo": zona_corta,
                            "mes_ano": periodo_str,
                            "fecha": str(f_fecha),
                            "familia": f_nombre.strip(),
                            "telefono": f_tel.strip(),
                            "notas": f_notas.strip(),
                        }).execute()
                        st.success(f"Listo. Su familia quedó anotada el {f_fecha.strftime('%d/%m/%Y')}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo guardar: {e}")

# ============================================
# TARJETA 4: LISTA DEL MES (después, como consulta)
# ============================================
with st.container(border=True):
    st.markdown(f"### Familias anotadas en {meses_nombres[mes_sel]}")
    if df_mes.empty:
        st.markdown('<p class="muted">Aún no hay familias anotadas este mes en este compañerismo.</p>', unsafe_allow_html=True)
    else:
        for _, row in df_mes.sort_values("fecha").iterrows():
            f_obj = datetime.date.fromisoformat(str(row["fecha"])[:10])
            tel_raw = str(row["telefono"])
            tel_link = "".join(ch for ch in tel_raw if ch.isdigit() or ch == "+")
            notas = str(row["notas"]) if pd.notna(row["notas"]) else ""
            bloque = f"""
            <div class="reg-row">
              <div class="reg-fecha">{f_obj.strftime('%A %d').capitalize()} de {meses_nombres[f_obj.month].lower()}</div>
              <div class="reg-fam">{html.escape(str(row['familia']))}</div>
              <a href="tel:{tel_link}">Llamar: {html.escape(tel_raw)}</a>
            """
            if notas:
                bloque += f'<div class="muted">Nota: {html.escape(notas)}</div>'
            bloque += '</div>'
            st.markdown(bloque, unsafe_allow_html=True)
