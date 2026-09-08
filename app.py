import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from datetime import timedelta
import math

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Comidas Misioneros - Apizaco y Tlaxco",
    layout="wide",
    initial_sidebar_state="auto"
)

# ============================================
# CSS RESPONSIVE Y CALENDARIO
# ============================================
st.markdown("""
<style>
@media (max-width: 768px) {
    .calendario-grid {
        grid-template-columns: repeat(7, 1fr) !important;
        gap: 2px !important;
    }
    .dia-recuadro {
        min-height: 60px !important;
        padding: 3px !important;
    }
    .dia-numero {
        font-size: 12px !important;
    }
    .registro-item {
        font-size: 8px !important;
        padding: 2px !important;
    }
    .registro-familia {
        font-size: 9px !important;
    }
    .registro-tel, .registro-notas {
        font-size: 7px !important;
    }
    .disponible-badge, .descanso-badge {
        font-size: 7px !important;
    }
    .dia-header {
        font-size: 10px !important;
        padding: 6px 2px !important;
    }
    h1 {
        font-size: 1.3rem !important;
    }
    h2 {
        font-size: 1.1rem !important;
    }
}

@media (max-width: 480px) {
    .calendario-grid {
        gap: 1px !important;
    }
    .dia-recuadro {
        min-height: 45px !important;
    }
    .registro-item {
        display: none !important;
    }
    .disponible-badge, .descanso-badge {
        font-size: 6px !important;
    }
}

.calendario-container {
    margin-top: 20px;
    margin-bottom: 20px;
}
.calendario-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 6px;
    margin-top: 10px;
}
.dia-header {
    background: #1f2937;
    color: white;
    padding: 12px 5px;
    text-align: center;
    font-weight: bold;
    border-radius: 6px;
    font-size: 14px;
}
.dia-recuadro {
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 8px;
    min-height: 110px;
    background: #f9fafb;
    position: relative;
}
.dia-recuadro.ocupado {
    background: #fef3c7;
    border-color: #f59e0b;
}
.dia-recuadro.hoy {
    border-color: #3b82f6;
    border-width: 3px;
    background: #dbeafe;
}
.dia-recuadro.lunes {
    background: #f3f4f6;
    border-color: #9ca3af;
    border-style: dashed;
}
.dia-recuadro.dia-vacio {
    background: transparent;
    border: none;
    min-height: 0;
}
.dia-numero {
    font-size: 18px;
    font-weight: bold;
    color: #1f2937;
    margin-bottom: 5px;
}
.registro-item {
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    padding: 4px 6px;
    margin-bottom: 4px;
    font-size: 11px;
}
.registro-familia {
    font-weight: bold;
    color: #1f2937;
    font-size: 12px;
}
.registro-tel {
    color: #6b7280;
    font-size: 10px;
}
.registro-notas {
    color: #9ca3af;
    font-size: 10px;
    font-style: italic;
}
.disponible-badge {
    color: #10b981;
    font-size: 10px;
    margin-top: 4px;
    font-weight: bold;
}
.descanso-badge {
    color: #6b7280;
    font-size: 10px;
    margin-top: 4px;
    font-weight: bold;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Calendario de Comidas para Misioneros")

# ============================================
# CONEXIÓN A SUPABASE
# ============================================
try:
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
    st.sidebar.success("✅ Conectado a Supabase")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.stop()

# ============================================
# LEER DATOS DE SUPABASE
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
    st.sidebar.success(f"✅ {len(df_db)} registros cargados")
except Exception as e:
    st.error(f"❌ Error al leer: {e}")
    df_db = pd.DataFrame(columns=["id", "companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])

# ============================================
# CONFIGURACIÓN DE COMPAÑERISMOS
# ============================================
zonas_disponibles = [
    "Compañerismo 1",
    "Compañerismo 2 (San José, Tetel, Santa Rosa, Cerrito, Zumpango)",
    "Compañerismo 3 (Centro, Xaltocan, Santa Úrsula, San Simón)",
    "Compañerismo 4 (Tlaxco)",
]

# ============================================
# FILTROS EN SIDEBAR
# ============================================
st.sidebar.header("️ Filtros")

zona = st.sidebar.selectbox(
    "Compañerismo:",
    zonas_disponibles,
)

meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

hoy = datetime.date.today()
col_m, col_a = st.sidebar.columns(2)
with col_m:
    mes_sel = st.selectbox(
        "Mes",
        options=list(meses_nombres.keys()),
        format_func=lambda x: meses_nombres[x],
        index=hoy.month - 1
    )
with col_a:
    anio_sel = st.selectbox(
        "Año",
        options=[2025, 2026, 2027],
        index=1 if hoy.year == 2026 else (2 if hoy.year == 2027 else 0)
    )

# ============================================
# PREPARAR DATOS DEL MES SELECCIONADO
# ============================================
periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"

if not df_db.empty:
    df_mes = df_db[df_db["companerismo"] == zona].copy()
    if "mes_ano" in df_mes.columns:
        df_mes = df_mes[df_mes["mes_ano"] == periodo_str]
else:
    df_mes = pd.DataFrame(columns=["id", "companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])

# Crear diccionario de registros por fecha
registros_por_fecha = {}
if not df_mes.empty:
    for _, row in df_mes.iterrows():
        fecha_str = str(row["fecha"])
        if "T" in fecha_str:
            fecha_str = fecha_str.split("T")[0]
        if fecha_str not in registros_por_fecha:
            registros_por_fecha[fecha_str] = []
        registros_por_fecha[fecha_str].append({
            "id": row.get("id"),
            "familia": str(row.get("familia", "")),
            "telefono": str(row.get("telefono", "")),
            "notas": str(row.get("notas", "")) if pd.notna(row.get("notas")) else "",
        })

# ============================================
# CALCULAR DÍAS DEL MES
# ============================================
primer_dia = datetime.date(anio_sel, mes_sel, 1)
if mes_sel == 12:
    ultimo_dia = datetime.date(anio_sel + 1, 1, 1) - timedelta(days=1)
else:
    ultimo_dia = datetime.date(anio_sel, mes_sel + 1, 1) - timedelta(days=1)
dias_mes = (ultimo_dia - primer_dia).days + 1
dia_semana_inicio = primer_dia.weekday()

# ============================================
# CALENDARIO VISUAL
# ============================================
st.header(f"📆 {meses_nombres[mes_sel]} {anio_sel} — {zona}")

dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

html_calendario = '<div class="calendario-container"><div class="calendario-grid">'

for dia in dias_semana:
    html_calendario += f'<div class="dia-header">{dia}</div>'

for i in range(dia_semana_inicio):
    html_calendario += '<div class="dia-recuadro dia-vacio"></div>'

for dia in range(1, dias_mes + 1):
    fecha_actual = datetime.date(anio_sel, mes_sel, dia)
    fecha_str = str(fecha_actual)
    es_lunes = (fecha_actual.weekday() == 0)
    es_hoy = (fecha_actual == hoy)
    tiene_registro = fecha_str in registros_por_fecha
    
    clase = "dia-recuadro"
    if es_lunes:
        clase += " lunes"
    elif es_hoy:
        clase += " hoy"
    if tiene_registro and not es_lunes:
        clase += " ocupado"
    
    html_calendario += f'<div class="{clase}">'
    html_calendario += f'<div class="dia-numero">{dia}</div>'
    
    if es_lunes:
        html_calendario += '<div class="descanso-badge">😴 Descanso</div>'
    elif tiene_registro:
        for reg in registros_por_fecha[fecha_str]:
            familia = reg["familia"]
            telefono = reg["telefono"]
            notas = reg.get("notas", "")
            
            html_calendario += '<div class="registro-item">'
            html_calendario += f'<div class="registro-familia">‍👩‍👧 {familia}</div>'
            html_calendario += f'<div class="registro-tel"> {telefono}</div>'
            if notas:
                html_calendario += f'<div class="registro-notas">📝 {notas}</div>'
            html_calendario += '</div>'
    else:
        html_calendario += '<div class="disponible-badge">✅ Libre</div>'
    
    html_calendario += '</div>'

html_calendario += '</div></div>'
st.markdown(html_calendario, unsafe_allow_html=True)

st.divider()

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs(["📋 Lista de registros", "✍️ Apuntarse a una fecha"])

with tab1:
    st.subheader(f"Registros de {meses_nombres[mes_sel]} {anio_sel}")
    
    if df_mes.empty:
        st.info(f"Aún no hay familias registradas para este mes en {zona}.")
    else:
        df_mostrar = df_mes.sort_values("fecha")[["fecha", "familia", "telefono", "notas"]].copy()
        st.dataframe(df_mostrar, use_container_width=True)
        st.metric("Total de registros este mes", len(df_mostrar))
    
    # ============================================
    # ZONA DE ADMINISTRACIÓN (PROTEGIDA)
    # ============================================
    st.divider()
    st.subheader("🔐 Zona de Administración")
    
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown("**Ingresa la contraseña de administrador:**")
        
        with st.form("login_form"):
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("🔓 Ingresar", use_container_width=True)
            
            if submitted:
                admin_password = st.secrets.get("admin", {}).get("password", "")
                if password == admin_password and admin_password != "":
                    st.session_state.admin_authenticated = True
                    st.success("✅ Acceso concedido")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
    else:
        st.success("✅ Modo administrador activo")
        
        if st.button("🔒 Cerrar sesión", type="secondary"):
            st.session_state.admin_authenticated = False
            st.rerun()
        
        st.divider()
        
        # BACKUP
        st.markdown("### 💾 Backup de Datos")
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            if st.button("📥 Exportar TODO a CSV", use_container_width=True):
                try:
                    response = supabase.table("comidas_misioneros").select("*").order("fecha", desc=False).execute()
                    df_completo = pd.DataFrame(response.data)
                    if not df_completo.empty:
                        csv_data = df_completo.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="⬇️ Descargar CSV completo",
                            data=csv_data,
                            file_name=f"backup_comidas_{datetime.date.today().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.success(f"✅ {len(df_completo)} registros listos")
                except Exception as e:
                    st.error(f" Error: {e}")
        
        with col_b2:
            if st.button(f"📥 Exportar {meses_nombres[mes_sel]} {anio_sel}", use_container_width=True):
                try:
                    if not df_mes.empty:
                        csv_data = df_mes.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label=f"⬇️ Descargar {periodo_str}",
                            data=csv_data,
                            file_name=f"backup_{periodo_str}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.success(f"✅ {len(df_mes)} registros del mes listos")
                    else:
                        st.warning("No hay datos este mes")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        st.divider()
        
        # EDITAR/ELIMINAR
        if df_mes.empty:
            st.info("No hay registros para editar.")
        else:
            df_ordenado = df_mes.sort_values("fecha").reset_index(drop=True)
            
            for idx, row in df_ordenado.iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.write(f"**📅 {row['fecha']}**")
                with col2:
                    st.write(f"👨‍👩👧 {row['familia']}")
                with col3:
                    st.write(f" {row['telefono']}")
                with col4:
                    if st.button("✏️", key=f"edit_{row['id']}", help="Editar"):
                        st.session_state[f"editando_{row['id']}"] = True
                    if st.button("🗑️", key=f"del_{row['id']}", help="Eliminar"):
                        st.session_state[f"eliminando_{row['id']}"] = True
            
            st.divider()
            
            for idx, row in df_ordenado.iterrows():
                registro_id = row['id']
                
                if st.session_state.get(f"editando_{registro_id}"):
                    st.markdown(f"**✏️ Editando: {row['fecha']} - {row['familia']}**")
                    
                    with st.form(key=f"form_edit_{registro_id}"):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            e_nombre = st.text_input("Nombre", value=row['familia'], key=f"e_nom_{registro_id}")
                            e_tel = st.text_input("Teléfono", value=row['telefono'], key=f"e_tel_{registro_id}")
                        with col_e2:
                            e_notas = st.text_area("Notas", value=row['notas'] if pd.notna(row['notas']) else "", key=f"e_not_{registro_id}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            guardar = st.form_submit_button("💾 Guardar", use_container_width=True)
                        with col_btn2:
                            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                        
                        if guardar:
                            try:
                                supabase.table("comidas_misioneros").update({
                                    "familia": e_nombre,
                                    "telefono": e_tel,
                                    "notas": e_notas,
                                }).eq("id", registro_id).execute()
                                st.success("✅ Registro actualizado")
                                st.session_state[f"editando_{registro_id}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                        
                        if cancelar:
                            st.session_state[f"editando_{registro_id}"] = False
                            st.rerun()
                
                if st.session_state.get(f"eliminando_{registro_id}"):
                    st.markdown(f"**🗑️ ¿Eliminar {row['fecha']} - {row['familia']}?**")
                    
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("✅ Sí, eliminar", key=f"confirm_del_{registro_id}", type="primary"):
                            try:
                                supabase.table("comidas_misioneros").delete().eq("id", registro_id).execute()
                                st.success("✅ Registro eliminado")
                                st.session_state[f"eliminando_{registro_id}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                    with col_c2:
                        if st.button("❌ No, cancelar", key=f"cancel_del_{registro_id}"):
                            st.session_state[f"eliminando_{registro_id}"] = False
                            st.rerun()

with tab2:
    st.subheader("Regístrate para darles de comer")
    
    fechas_ocupadas = set(registros_por_fecha.keys())
    fechas_disponibles = []
    for dia in range(1, dias_mes + 1):
        fecha = datetime.date(anio_sel, mes_sel, dia)
        if fecha.weekday() != 0 and str(fecha) not in fechas_ocupadas:
            fechas_disponibles.append(fecha)
    
    st.info("️ **Nota:** Los lunes son día de descanso y no están disponibles.")
    
    if not fechas_disponibles:
        st.warning("⚠️ No hay fechas disponibles este mes.")
    else:
        with st.form("form_registro", clear_on_submit=True):
            st.markdown("**Selecciona una fecha:**")
            
            f_fecha = st.date_input(
                "Fecha de la comida",
                min_value=datetime.date(anio_sel, mes_sel, 1),
                max_value=datetime.date(anio_sel, mes_sel, dias_mes),
                value=fechas_disponibles[0] if fechas_disponibles else datetime.date(anio_sel, mes_sel, 1),
            )
            
            if f_fecha.weekday() == 0:
                st.error(f"❌ {f_fecha.strftime('%d/%m/%Y')} es lunes (día de descanso).")
            elif f_fecha in fechas_disponibles:
                st.success(f"✅ {f_fecha.strftime('%d/%m/%Y')} está disponible")
            else:
                st.error(f"❌ {f_fecha.strftime('%d/%m/%Y')} ya está ocupada.")
            
            f_nombre = st.text_input("Nombre de la Familia / Persona")
            f_tel = st.text_input("Número de Teléfono (WhatsApp)")
            f_notas = st.text_area("Notas adicionales", height=80)
            
            submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True)
            
            if submitted:
                if f_nombre and f_tel:
                    if f_fecha.weekday() != 0 and f_fecha in fechas_disponibles:
                        nuevo_registro = {
                            "companerismo": zona,
                            "mes_ano": periodo_str,
                            "fecha": str(f_fecha),
                            "familia": f_nombre,
                            "telefono": f_tel,
                            "notas": f_notas,
                        }
                        try:
                            supabase.table("comidas_misioneros").insert(nuevo_registro).execute()
                            st.success(f"✅ ¡Gracias {f_nombre}! Registro guardado para el {f_fecha.strftime('%d/%m/%Y')}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f" Error: {e}")
                    elif f_fecha.weekday() == 0:
                        st.error(" Los lunes son día de descanso.")
                    else:
                        st.error(f"❌ La fecha ya está ocupada.")
                else:
                    st.error("❌ Completa nombre y teléfono.")