import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from datetime import timedelta

st.set_page_config(page_title="Comidas Misioneros - Apizaco y Tlaxco", layout="wide")
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
# LEER DATOS
# ============================================
try:
    response = supabase.table("comidas_misioneros").select("*").execute()
    df_db = pd.DataFrame(response.data)
    if df_db.empty:
        df_db = pd.DataFrame(columns=["companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])
    st.sidebar.success(f"✅ {len(df_db)} registros cargados")
except Exception as e:
    st.error(f"❌ Error al leer: {e}")
    df_db = pd.DataFrame(columns=["companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])

# ============================================
# FILTROS
# ============================================
st.sidebar.header("🎛️ Filtros")
zona = st.sidebar.selectbox(
    "Compañerismo:",
    ["Apizaco 1 (Hno. Ulises / Galaviz)", "Apizaco 2 (Hno. Jorge Álvarez)", "Apizaco 3 (Hno. Jorge Luis Pérez)", "Tlaxco"],
)

meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

hoy = datetime.date.today()
col_m, col_a = st.sidebar.columns(2)
with col_m:
    mes_sel = st.selectbox("Mes", options=list(meses_nombres.keys()), format_func=lambda x: meses_nombres[x], index=hoy.month - 1)
with col_a:
    anio_sel = st.selectbox("Año", options=[2025, 2026, 2027], index=1 if hoy.year == 2026 else (2 if hoy.year == 2027 else 0))

# ============================================
# CALENDARIO VISUAL TIPO RECUADROS
# ============================================
st.header(f"📆 {meses_nombres[mes_sel]} {anio_sel} — {zona}")

# Preparar datos del mes
periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"
if not df_db.empty:
    df_mes = df_db[df_db["companerismo"] == zona]
    df_mes = df_mes[df_mes["mes_ano"] == periodo_str] if "mes_ano" in df_mes.columns else pd.DataFrame()
else:
    df_mes = pd.DataFrame()

# Crear diccionario de registros por fecha
registros_por_fecha = {}
if not df_mes.empty:
    for _, row in df_mes.iterrows():
        fecha_str = str(row["fecha"])
        if fecha_str not in registros_por_fecha:
            registros_por_fecha[fecha_str] = []
        registros_por_fecha[fecha_str].append({
            "familia": row.get("familia", ""),
            "telefono": row.get("telefono", ""),
            "notas": row.get("notas", ""),
        })

# Calcular días del mes
primer_dia = datetime.date(anio_sel, mes_sel, 1)
if mes_sel == 12:
    ultimo_dia = datetime.date(anio_sel + 1, 1, 1) - timedelta(days=1)
else:
    ultimo_dia = datetime.date(anio_sel, mes_sel + 1, 1) - timedelta(days=1)
dias_mes = (ultimo_dia - primer_dia).days + 1

# Día de la semana del primer día (0=Lunes, 6=Domingo)
dia_semana_inicio = primer_dia.weekday()

# CSS para el calendario
calendario_css = """
<style>
.calendario-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 10px;
}
.dia-header {
    background: #2c3e50;
    color: white;
    padding: 10px 5px;
    text-align: center;
    font-weight: bold;
    border-radius: 6px;
    font-size: 14px;
}
.dia-recuadro {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 8px;
    min-height: 100px;
    background: #f8f9fa;
    position: relative;
}
.dia-recuadro.ocupado {
    background: #fff3cd;
    border-color: #ffc107;
}
.dia-recuadro.hoy {
    border-color: #007bff;
    border-width: 3px;
    background: #e7f1ff;
}
.dia-numero {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 5px;
}
.dia-vacio {
    background: transparent;
    border: none;
}
.registro-item {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 4px 6px;
    margin-bottom: 4px;
    font-size: 11px;
}
.registro-familia {
    font-weight: bold;
    color: #2c3e50;
}
.registro-tel {
    color: #666;
    font-size: 10px;
}
.registro-notas {
    color: #888;
    font-size: 10px;
    font-style: italic;
}
.disponible-badge {
    color: #28a745;
    font-size: 10px;
    margin-top: 4px;
}
</style>
"""

st.markdown(calendario_css, unsafe_allow_html=True)

# Construir HTML del calendario
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

html_calendario = '<div class="calendario-grid">'

# Headers de días de la semana
for dia in dias_semana:
    html_calendario += f'<div class="dia-header">{dia}</div>'

# Celdas vacías antes del primer día
for i in range(dia_semana_inicio):
    html_calendario += '<div class="dia-recuadro dia-vacio"></div>'

# Días del mes
for dia in range(1, dias_mes + 1):
    fecha_actual = datetime.date(anio_sel, mes_sel, dia)
    fecha_str = str(fecha_actual)
    
    es_hoy = (fecha_actual == hoy)
    tiene_registro = fecha_str in registros_por_fecha
    
    clase = "dia-recuadro"
    if es_hoy:
        clase += " hoy"
    if tiene_registro:
        clase += " ocupado"
    
    html_calendario += f'<div class="{clase}">'
    html_calendario += f'<div class="dia-numero">{dia}</div>'
    
    if tiene_registro:
        for reg in registros_por_fecha[fecha_str]:
            familia = reg["familia"]
            telefono = reg["telefono"]
            notas = reg.get("notas", "")
            
            html_calendario += '<div class="registro-item">'
            html_calendario += f'<div class="registro-familia">👨👩‍👧 {familia}</div>'
            html_calendario += f'<div class="registro-tel">📞 {telefono}</div>'
            if notas:
                html_calendario += f'<div class="registro-notas">📝 {notas}</div>'
            html_calendario += '</div>'
    else:
        html_calendario += '<div class="disponible-badge">✅ Disponible</div>'
    
    html_calendario += '</div>'

html_calendario += '</div>'

st.markdown(html_calendario, unsafe_allow_html=True)

st.divider()

# ============================================
# TABS: Lista y Registro
# ============================================
tab1, tab2 = st.tabs(["📋 Lista de registros", "✍️ Apuntarse a una fecha"])

with tab1:
    st.subheader(f"Registros de {meses_nombres[mes_sel]} {anio_sel}")
    
    if df_mes.empty:
        st.info(f"Aún no hay familias registradas para este mes.")
    else:
        df_mostrar = df_mes.sort_values("fecha")[["fecha", "familia", "telefono", "notas"]]
        st.dataframe(df_mostrar, use_container_width=True)

with tab2:
    st.subheader("Regístrate para darles de comer")
    
    # Fechas disponibles
    fechas_ocupadas = set(registros_por_fecha.keys())
    fechas_disponibles = []
    for dia in range(1, dias_mes + 1):
        fecha = datetime.date(anio_sel, mes_sel, dia)
        if str(fecha) not in fechas_ocupadas:
            fechas_disponibles.append(fecha)
    
    if not fechas_disponibles:
        st.warning("⚠️ No hay fechas disponibles este mes.")
    else:
        with st.form("form_registro", clear_on_submit=True):
            f_fecha = st.selectbox(
                "Selecciona una fecha disponible",
                options=fechas_disponibles,
                format_func=lambda x: f"{x.strftime('%d/%m/%Y')} ({['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'][x.weekday()]})"
            )
            f_nombre = st.text_input("Nombre de la Familia / Persona")
            f_tel = st.text_input("Número de Teléfono (WhatsApp)")
            f_notas = st.text_area("Notas adicionales (ej. hora acordada, restricciones)")
            
            submitted = st.form_submit_button(" Guardar Registro")
            
            if submitted:
                if f_nombre and f_tel:
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
                        st.error(f"❌ Error al guardar: {e}")
                else:
                    st.error("❌ Por favor completa nombre y teléfono.")
