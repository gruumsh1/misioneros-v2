import datetime
import html
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from datetime import timedelta

# ============================================
# CONFIGURACIÓN: una sola columna, sin sidebar
# ============================================
st.set_page_config(
    page_title="Comidas para Misioneros",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================
# ESTILOS: paleta clara, WCAG 2.1, táctil
# ============================================
st.markdown("""
<style>
/* Tipografía base: 17px, interlineado 1.6 (WCAG 1.4) */
html{font-size:17px}
body,.stMarkdown,p,li{color:#2B2A28}
p,li{line-height:1.6}
h1{font-size:1.7rem;font-weight:800}
h2,h3{font-size:1.25rem;font-weight:700;margin-bottom:.4rem}
.muted{color:#6B6862;font-size:.95rem;line-height:1.5}

/* Ocultar sidebar y pie de Streamlit */
[data-testid="stSidebar"]{display:none}
#MainMenu,footer{visibility:hidden}

/* Tarjetas (containers con borde) */
[data-testid="stVerticalBlockBorderWrapper"]{background:#F3F2EE;border-color:#E5E3DD;border-radius:14px}
[data-testid="stVerticalBlockBorderWrapper"] > div{background:#F3F2EE}

/* Botones táctiles: mínimo 48px (WCAG 2.5.5) */
[data-testid="stButton"] button,[data-testid="stForm"] button{
  min-height:48px;font-size:1rem;font-weight:600;border-radius:10px}
[data-testid="stBaseButton-primary"]{background:#E76F51 !important;color:#2B2A28 !important;border:none !important}

/* Pills y control segmentado: objetivos >=44px */
[data-testid="stPills"] button,[data-testid="stSegmentedControl"] button{
  min-height:44px;font-size:1rem;padding:.4rem .95rem;border-radius:999px}

/* Campos de texto grandes y legibles */
[data-testid="stTextInput"] input,[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea{
  min-height:48px;font-size:1rem;border-color:#C9C6BF;border-radius:10px}

/* Foco siempre visible (WCAG 2.4.7) */
:focus-visible{outline:3px solid #2B2A28;outline-offset:2px}

/* Calendario */
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-top:.6rem}
.cal-head{background:#2B2A28;color:#FAFAF8;text-align:center;font-weight:700;
  font-size:.8rem;padding:8px 2px;border-radius:8px;letter-spacing:.03em}
.cal-cell{background:#FFFFFF;border:1.5px solid #E5E3DD;border-radius:10px;padding:6px 4px;min-height:92px}
.cal-cell.ocupado{background:#FBE9E4;border-color:#E76F51}
.cal-cell.hoy{border:3px solid #2B2A28}
.cal-cell.lunes{background:#EEEDE9;border-style:dashed;border-color:#C9C6BF}
.cal-cell.vacio{border:none;background:transparent;min-height:0}
.cal-day{font-size:1.05rem;font-weight:800;color:#2B2A28}
.cal-state{font-size:.68rem;font-weight:700;letter-spacing:.05em;margin-top:2px}
.st-libre{color:#295F38}
.st-ocupado{color:#8A3324}
.st-descanso{color:#6B6862}
.cal-fam{font-size:.72rem;color:#2B2A28;font-weight:600;margin-top:3px;line-height:1.25;word-break:break-word}
.cal-tel{font-size:.68rem;color:#6B6862;word-break:break-word}

/* Lista de registros */
.reg-row{background:#FFFFFF;border:1px solid #E5E3DD;border-radius:10px;padding:.6rem .7rem;margin-bottom:.5rem}
.reg-fecha{font-weight:800;font-size:1rem}
.reg-fam{font-weight:600}
.reg-row a{color:#8A3324;font-weight:700}

/* Leyenda con texto (no solo color, WCAG 1.4.1) */
.legend{display:flex;gap:.9rem;flex-wrap:wrap;margin-top:.7rem;font-size:.85rem;color:#2B2A28}
.chip{display:inline-block;width:14px;height:14px;border-radius:4px;border:1.5px solid #E5E3DD;vertical-align:-2px;margin-right:6px}
.chip-libre{background:#FFFFFF}
.chip-ocup{background:#FBE9E4;border-color:#E76F51}
.chip-desc{background:#EEEDE9;border-style:dashed;border-color:#C9C6BF}

/* Móvil: calendario compacto, detalles quedan en la lista */
@media (max-width:640px){
  .cal-grid{gap:3px}
  .cal-cell{min-height:64px;padding:4px 2px}
  .cal-day{font-size:.95rem}
  .cal-state{font-size:.58rem}
  .cal-fam,.cal-tel{display:none}
  .cal-head{font-size:.62rem;padding:6px 1px}
}
</style>
""", unsafe_allow_html=True)

st.title("Comidas para misioneros")
st.caption("Apizaco y Tlaxco. Elija su compañerismo, vea los días disponibles y anote a su familia. Los lunes son día de descanso de los misioneros.")

# ============================================
# CONEXIÓN A SUPABASE
# ============================================
try:
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"No se pudo conectar a la base de datos: {e}")
    st.stop()

# ============================================
# LEER REGISTROS
# ============================================
try:
    response = supabase.table("comidas_misioneros").select("*").order("fecha", desc=False).execute()
    df_db = pd.DataFrame(response.data)
    if df_db.empty:
        df_db = pd.DataFrame(columns=["id", "companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])
    else:
        for col in ["id", "companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"]:
            if col not in df_db.columns:
                df_db[col] = ""
except Exception as e:
    st.error(f"No se pudieron leer los registros: {e}")
    df_db = pd.DataFrame(columns=["id", "companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])

# ============================================
# LEER MISIONEROS ACTUALES
# ============================================
try:
    response_mis = supabase.table("misioneros_info").select("*").execute()
    df_mis = pd.DataFrame(response_mis.data)
    if df_mis.empty:
        df_mis = pd.DataFrame(columns=["companerismo", "misionero_1", "misionero_2"])
except Exception:
    df_mis = pd.DataFrame(columns=["companerismo", "misionero_1", "misionero_2"])

def obtener_misioneros(zona_corta):
    if df_mis.empty or "companerismo" not in df_mis.columns:
        return ""
    fila = df_mis[df_mis["companerismo"] == zona_corta]
    if fila.empty:
        return ""
    m1 = str(fila.iloc[0].get("misionero_1", "") or "").strip()
    m2 = str(fila.iloc[0].get("misionero_2", "") or "").strip()
    partes = [p for p in [m1, m2] if p]
    return " / ".join(partes)

# ============================================
# CATÁLOGOS Y EQUIVALENCIAS
# ============================================
mapeo_a_corto = {
    "Compañerismo 1": "Apizaco 1",
    "Compañerismo 2": "Apizaco 2",
    "Compañerismo 3": "Apizaco 3",
    "Compañerismo 4 (Tlaxco)": "Tlaxco",
}
COLONIAS = {
    "Compañerismo 1": "",
    "Compañerismo 2": "San José, Tetel, Santa Rosa, Cerrito, Zumpango",
    "Compañerismo 3": "Centro, Xaltocan, Santa Úrsula, San Simón",
    "Compañerismo 4 (Tlaxco)": "Tlaxco y comunidades",
}
MESES_ABREV = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun",
               7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

hoy = datetime.date.today()

# ============================================
# TARJETA 1: SELECCIÓN (rejilla ordenada, sin desplegables)
# ============================================
with st.container(border=True):
    st.markdown("##### 1. Elija su compañerismo")
    zona = st.pills(
        "Compañerismo",
        options=list(mapeo_a_corto.keys()),
        default=list(mapeo_a_corto.keys())[0],
        key="zona_pill",
        label_visibility="collapsed",
    )
    zona_corta = mapeo_a_corto.get(zona, zona)

    info_lineas = []
    if COLONIAS.get(zona):
        info_lineas.append(f"Colonias: {COLONIAS[zona]}")
    mis_txt = obtener_misioneros(zona_corta)
    if mis_txt:
        info_lineas.append(f"Misioneros asignados: {mis_txt}")
    for linea in info_lineas:
        st.markdown(f'<p class="muted">{html.escape(linea)}</p>', unsafe_allow_html=True)

    st.markdown("##### 2. Elija el mes")
    if "mes_sel" not in st.session_state:
        st.session_state.mes_sel = hoy.month

    cols = st.columns(4)
    for idx, m in enumerate(range(1, 13)):
        with cols[idx % 4]:
            seleccionado = (st.session_state.mes_sel == m)
            if st.button(
                MESES_ABREV[m],
                key=f"mes_btn_{m}",
                use_container_width=True,
                type="primary" if seleccionado else "secondary",
                help=meses_nombres[m],
            ):
                st.session_state.mes_sel = m
                st.rerun()
    mes_sel = st.session_state.mes_sel

    anio_sel = st.segmented_control(
        "Año",
        options=[2025, 2026, 2027],
        default=hoy.year if hoy.year in [2025, 2026, 2027] else 2026,
        key="anio_seg",
        label_visibility="collapsed",
    )

if mes_sel is None:
    mes_sel = hoy.month
if anio_sel is None:
    anio_sel = hoy.year if hoy.year in [2025, 2026, 2027] else 2026

# ============================================
# PREPARAR DATOS DEL MES
# ============================================
periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"

if not df_db.empty:
    df_mes = df_db[df_db["companerismo"] == zona_corta].copy()
    if "mes_ano" in df_mes.columns:
        df_mes = df_mes[df_mes["mes_ano"] == periodo_str]
else:
    df_mes = pd.DataFrame(columns=["id", "companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])

registros_por_fecha = {}
if not df_mes.empty:
    for _, row in df_mes.iterrows():
        fecha_str = str(row["fecha"])
        if "T" in fecha_str:
            fecha_str = fecha_str.split("T")[0]
        registros_por_fecha.setdefault(fecha_str, []).append({
            "id": row.get("id"),
            "familia": str(row.get("familia", "")),
            "telefono": str(row.get("telefono", "")),
            "notas": str(row.get("notas", "")) if pd.notna(row.get("notas")) else "",
        })

primer_dia = datetime.date(anio_sel, mes_sel, 1)
if mes_sel == 12:
    ultimo_dia = datetime.date(anio_sel + 1, 1, 1) - timedelta(days=1)
else:
    ultimo_dia = datetime.date(anio_sel, mes_sel + 1, 1) - timedelta(days=1)
dias_mes = (ultimo_dia - primer_dia).days + 1
dia_semana_inicio = primer_dia.weekday()

# ============================================
# TARJETA 2: CALENDARIO
# ============================================
with st.container(border=True):
    st.markdown(f"### {meses_nombres[mes_sel]} {anio_sel} · {zona}")

    dias_cab = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    html_cal = '<div class="cal-grid">'
    for d in dias_cab:
        html_cal += f'<div class="cal-head">{d}</div>'
    for _ in range(dia_semana_inicio):
        html_cal += '<div class="cal-cell vacio"></div>'

    for dia in range(1, dias_mes + 1):
        f_act = datetime.date(anio_sel, mes_sel, dia)
        f_str = str(f_act)
        es_lunes = f_act.weekday() == 0
        es_hoy = f_act == hoy
        regs = registros_por_fecha.get(f_str, [])

        clase = "cal-cell"
        if es_lunes:
            clase += " lunes"
        elif es_hoy:
            clase += " hoy"
        if regs and not es_lunes:
            clase += " ocupado"

        html_cal += f'<div class="{clase}">'
        html_cal += f'<div class="cal-day">{dia}</div>'
        if es_lunes:
            html_cal += '<div class="cal-state st-descanso">DESCANSO</div>'
        elif regs:
            html_cal += '<div class="cal-state st-ocupado">OCUPADO</div>'
            for r in regs:
                html_cal += f'<div class="cal-fam">{html.escape(r["familia"])}</div>'
                html_cal += f'<div class="cal-tel">{html.escape(r["telefono"])}</div>'
        else:
            html_cal += '<div class="cal-state st-libre">LIBRE</div>'
        html_cal += '</div>'

    html_cal += '</div>'
    html_cal += """
    <div class="legend">
      <span><span class="chip chip-libre"></span>Libre: puede anotarse</span>
      <span><span class="chip chip-ocup"></span>Ocupado: ya hay familia</span>
      <span><span class="chip chip-desc"></span>Lunes: descanso</span>
    </div>
    """
    st.markdown(html_cal, unsafe_allow_html=True)

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
              <div class="reg-fecha">{DIAS_SEMANA[f_obj.weekday()]} {f_obj.day} de {meses_nombres[f_obj.month].lower()}</div>
              <div class="reg-fam">{html.escape(str(row['familia']))}</div>
              <a href="tel:{tel_link}">Llamar: {html.escape(tel_raw)}</a>
            """
            if notas:
                bloque += f'<div class="muted">Nota: {html.escape(notas)}</div>'
            bloque += '</div>'
            st.markdown(bloque, unsafe_allow_html=True)

# ============================================
# TARJETA 5: ADMINISTRACIÓN (solo encargados)
# ============================================
with st.container(border=True):
    with st.expander("Administración (solo encargados)"):
        if 'admin_authenticated' not in st.session_state:
            st.session_state.admin_authenticated = False

        if not st.session_state.admin_authenticated:
            with st.form("login_form"):
                password = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    admin_password = st.secrets.get("admin", {}).get("password", "")
                    if password == admin_password and admin_password:
                        st.session_state.admin_authenticated = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
        else:
            st.success("Sesión de encargado activa.")
            if st.button("Cerrar sesión"):
                st.session_state.admin_authenticated = False
                st.rerun()

            st.markdown("#### Nombres de misioneros")
            for zona_iter in ["Apizaco 1", "Apizaco 2", "Apizaco 3", "Tlaxco"]:
                with st.expander(zona_iter):
                    fila = df_mis[df_mis["companerismo"] == zona_iter] if not df_mis.empty else pd.DataFrame()
                    m1 = str(fila.iloc[0].get("misionero_1", "") or "") if not fila.empty else ""
                    m2 = str(fila.iloc[0].get("misionero_2", "") or "") if not fila.empty else ""
                    with st.form(key=f"form_mis_{zona_iter}"):
                        n1 = st.text_input("Misionero 1", value=m1, key=f"m1_{zona_iter}")
                        n2 = st.text_input("Misionero 2", value=m2, key=f"m2_{zona_iter}")
                        if st.form_submit_button("Guardar nombres", use_container_width=True):
                            try:
                                if fila.empty:
                                    supabase.table("misioneros_info").insert({
                                        "companerismo": zona_iter,
                                        "misionero_1": n1, "misionero_2": n2,
                                    }).execute()
                                else:
                                    supabase.table("misioneros_info").update({
                                        "misionero_1": n1, "misionero_2": n2,
                                        "actualizado_el": datetime.datetime.now().isoformat(),
                                    }).eq("companerismo", zona_iter).execute()
                                st.success("Nombres actualizados.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"No se pudo guardar: {e}")

            st.markdown("#### Respaldo de información")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Descargar todo (CSV)", use_container_width=True):
                    resp = supabase.table("comidas_misioneros").select("*").execute()
                    df_all = pd.DataFrame(resp.data)
                    if not df_all.empty:
                        st.download_button(
                            "Bajar archivo",
                            df_all.to_csv(index=False, encoding='utf-8-sig'),
                            file_name=f"respaldo_{datetime.date.today().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                        )
            with c2:
                if st.button(f"Descargar {meses_nombres[mes_sel]}", use_container_width=True):
                    if not df_mes.empty:
                        st.download_button(
                            "Bajar archivo",
                            df_mes.to_csv(index=False, encoding='utf-8-sig'),
                            file_name=f"respaldo_{periodo_str}.csv",
                            mime="text/csv",
                        )

            st.markdown("#### Corregir o borrar registros del mes")
            if df_mes.empty:
                st.markdown('<p class="muted">No hay registros este mes.</p>', unsafe_allow_html=True)
            else:
                for _, row in df_mes.sort_values("fecha").iterrows():
                    rid = row["id"]
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.markdown(f"**{row['fecha']}** · {html.escape(str(row['familia']))}")
                    if c2.button("Editar", key=f"e_{rid}"):
                        st.session_state[f"editando_{rid}"] = True
                    if c3.button("Borrar", key=f"d_{rid}"):
                        st.session_state[f"eliminando_{rid}"] = True

                for _, row in df_mes.iterrows():
                    rid = row["id"]
                    if st.session_state.get(f"editando_{rid}"):
                        with st.form(key=f"fe_{rid}"):
                            st.markdown(f"**Editando {row['fecha']}**")
                            en = st.text_input("Nombre", value=row["familia"], key=f"en_{rid}")
                            et = st.text_input("Teléfono", value=row["telefono"], key=f"et_{rid}")
                            eo = st.text_area("Nota", value=row["notas"] if pd.notna(row["notas"]) else "", key=f"eo_{rid}")
                            s1, s2 = st.columns(2)
                            guardar = s1.form_submit_button("Guardar cambios")
                            cancelar = s2.form_submit_button("Cancelar")
                            if guardar:
                                supabase.table("comidas_misioneros").update({
                                    "familia": en, "telefono": et, "notas": eo,
                                }).eq("id", rid).execute()
                                st.session_state[f"editando_{rid}"] = False
                                st.rerun()
                            if cancelar:
                                st.session_state[f"editando_{rid}"] = False
                                st.rerun()
                    if st.session_state.get(f"eliminando_{rid}"):
                        st.markdown(f"**¿Borrar el registro del {row['fecha']} de {html.escape(str(row['familia']))}?**")
                        s1, s2 = st.columns(2)
                        if s1.button("Sí, borrar", key=f"sd_{rid}", type="primary"):
                            supabase.table("comidas_misioneros").delete().eq("id", rid).execute()
                            st.session_state[f"eliminando_{rid}"] = False
                            st.rerun()
                        if s2.button("No, conservar", key=f"nd_{rid}"):
                            st.session_state[f"eliminando_{rid}"] = False
                            st.rerun()
