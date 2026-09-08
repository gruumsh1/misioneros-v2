import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from datetime import timedelta

st.set_page_config(page_title="Comidas Misioneros - Apizaco y Tlaxco", layout="wide")
st.title("️ Calendario de Comidas para Misioneros")

# Conexión a Supabase
try:
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
    st.sidebar.success("✅ Conectado a Supabase")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.stop()

# Leer datos
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
# CALENDARIO VISUAL
# ============================================
st.sidebar.header(" Calendario")

# Obtener mes y año actual
hoy = datetime.date.today()
mes_actual = st.sidebar.selectbox(
    "Mes",
    options=list(range(1, 13)),
    format_func=lambda x: datetime.date(2026, x, 1).strftime("%B"),
    index=hoy.month - 1
)

anio_actual = st.sidebar.selectbox("Año", options=[2026, 2027], index=0 if hoy.year == 2026 else 1)

# Crear calendario
def crear_calendario(mes, anio, df_registros):
    """Crea una visualización de calendario con los días ocupados"""
    # Primer día del mes
    primer_dia = datetime.date(anio, mes, 1)
    
    # Último día del mes
    if mes == 12:
        ultimo_dia = datetime.date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = datetime.date(anio, mes + 1, 1) - timedelta(days=1)
    
    # Días del mes
    dias_mes = (ultimo_dia - primer_dia).days + 1
    
    # Crear DataFrame con todos los días del mes
    todos_los_dias = [primer_dia + timedelta(days=i) for i in range(dias_mes)]
    
    # Obtener registros del mes
    periodo_str = f"{anio}-{str(mes).zfill(2)}"
    registros_mes = df_registros[df_registros["mes_ano"] == periodo_str] if not df_registros.empty else pd.DataFrame()
    
    # Crear diccionario de fechas ocupadas
    fechas_ocupadas = {}
    if not registros_mes.empty:
        for _, row in registros_mes.iterrows():
            fecha_str = row["fecha"]
            if fecha_str in fechas_ocupadas:
                fechas_ocupadas[fecha_str].append(row["familia"])
            else:
                fechas_ocupadas[fecha_str] = [row["familia"]]
    
    # Mostrar calendario
    st.subheader(f"📆 {primer_dia.strftime('%B %Y').capitalize()}")
    
    # Días de la semana
    dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**")
    
    # Ajustar para que el lunes sea el primer día
    dia_semana_inicio = (primer_dia.weekday())  # 0 = lunes
    
    # Crear filas del calendario
    dia_actual = 1
    for semana in range(6):  # Máximo 6 semanas
        cols = st.columns(7)
        for dia_col in range(7):
            if semana == 0 and dia_col < dia_semana_inicio:
                # Celdas vacías antes del primer día
                cols[dia_col].markdown("")
            elif dia_actual > dias_mes:
                # Fin del mes
                cols[dia_col].markdown("")
            else:
                # Día del mes
                fecha_completa = datetime.date(anio, mes, dia_actual)
                fecha_str = str(fecha_completa)
                
                if fecha_str in fechas_ocupadas:
                    # Día ocupado
                    familias = fechas_ocupadas[fecha_str]
                    cols[dia_col].markdown(f" **{dia_actual}**")
                    cols[dia_col].caption(f"{', '.join(familias[:2])}")  # Mostrar hasta 2 familias
                else:
                    # Día disponible
                    cols[dia_col].markdown(f"🟢 **{dia_actual}**")
                
                dia_actual += 1
        
        if dia_actual > dias_mes:
            break

# ============================================
# FILTROS DE VISUALIZACIÓN
# ============================================
st.sidebar.header(" Filtros")

zona = st.sidebar.selectbox(
    "Compañerismo:",
    ["Apizaco 1 (Hno. Ulises / Galaviz)", "Apizaco 2 (Hno. Jorge Álvarez)", "Apizaco 3 (Hno. Jorge Luis Pérez)", "Tlaxco"],
)

# Mostrar calendario
crear_calendario(mes_actual, anio_actual, df_db[df_db["companerismo"] == zona] if not df_db.empty else df_db)

st.divider()

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs(["📋 Ver Registros del Mes", "✍️ Apuntarse a una fecha"])

with tab1:
    st.subheader(f"Registros de {datetime.date(anio_actual, mes_actual, 1).strftime('%B %Y').capitalize()}")
    periodo_str = f"{anio_actual}-{str(mes_actual).zfill(2)}"
    
    if not df_db.empty:
        df_filtrado = df_db[
            (df_db["companerismo"] == zona) & 
            (df_db["mes_ano"] == periodo_str)
        ]
    else:
        df_filtrado = pd.DataFrame(columns=["companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])
    
    if df_filtrado.empty:
        st.info(f"Aún no hay familias registradas para {datetime.date(anio_actual, mes_actual, 1).strftime('%B %Y')} en este compañerismo.")
    else:
        # Ordenar por fecha
        df_filtrado = df_filtrado.sort_values("fecha")
        st.dataframe(
            df_filtrado[["fecha", "familia", "telefono", "notas"]],
            use_container_width=True
        )

with tab2:
    st.subheader("Regístrate para darles de comer")
    
    with st.form("form_registro_mes", clear_on_submit=True):
        # Mostrar fechas disponibles
        st.write("**Fechas disponibles este mes:**")
        periodo_str = f"{anio_actual}-{str(mes_actual).zfill(2)}"
        
        if not df_db.empty:
            registros_mes = df_db[df_db["mes_ano"] == periodo_str]
            fechas_ocupadas = registros_mes["fecha"].tolist() if not registros_mes.empty else []
        else:
            fechas_ocupadas = []
        
        # Crear lista de fechas disponibles
        primer_dia = datetime.date(anio_actual, mes_actual, 1)
        if mes_actual == 12:
            ultimo_dia = datetime.date(anio_actual + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = datetime.date(anio_actual, mes_actual + 1, 1) - timedelta(days=1)
        
        fechas_disponibles = [
            (primer_dia + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((ultimo_dia - primer_dia).days + 1)
            if (primer_dia + timedelta(days=i)).strftime("%Y-%m-%d") not in fechas_ocupadas
        ]
        
        if not fechas_disponibles:
            st.warning("No hay fechas disponibles este mes.")
        
        f_fecha = st.selectbox("Selecciona una fecha disponible", fechas_disponibles if fechas_disponibles else [])
        f_nombre = st.text_input("Nombre de la Familia / Persona")
        f_tel = st.text_input("Número de Teléfono (WhatsApp)")
        f_notas = st.text_area("Notas adicionales (ej. hora acordada, restricciones)")
        
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            if f_nombre and f_tel and f_fecha:
                fecha_obj = datetime.datetime.strptime(f_fecha, "%Y-%m-%d").date()
                
                nuevo_registro = {
                    "companerismo": zona,
                    "mes_ano": periodo_str,
                    "fecha": f_fecha,
                    "familia": f_nombre,
                    "telefono": f_tel,
                    "notas": f_notas,
                }
                
                try:
                    supabase.table("comidas_misioneros").insert(nuevo_registro).execute()
                    st.success(f"✅ ¡Gracias {f_nombre}! Tu registro para el {fecha_obj.strftime('%d/%m/%Y')} se ha guardado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")
            else:
                st.error("❌ Por favor completa todos los campos requeridos.")
