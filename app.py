import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client

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
    st.error(f" Error de conexión: {e}")
    st.stop()

# ============================================
# LEER DATOS DE SUPABASE
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
# FILTROS DE VISUALIZACIÓN
# ============================================
st.sidebar.header("Filtros de Visualización")

zona = st.sidebar.selectbox(
    "Selecciona el Compañerismo:",
    [
        "Apizaco 1 (Hno. Ulises / Galaviz)",
        "Apizaco 2 (Hno. Jorge Álvarez)",
        "Apizaco 3 (Hno. Jorge Luis Pérez)",
        "Tlaxco",
    ],
)

meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

col_m, col_a = st.sidebar.columns(2)
with col_m:
    mes_sel = st.selectbox(
        "Mes",
        options=list(meses_nombres.keys()),
        format_func=lambda x: meses_nombres[x],
        index=8
    )
with col_a:
    anio_sel = st.selectbox("Año", options=[2026, 2027], index=0)

st.header(f"Agenda para: {zona} — {meses_nombres[mes_sel]} {anio_sel}")

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs(["📅 Ver Calendario del Mes", "✍️ Apuntarse a una fecha"])

with tab1:
    st.subheader(f"Registros de {meses_nombres[mes_sel]} {anio_sel}")
    periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"
    
    if not df_db.empty:
        df_filtrado = df_db[
            (df_db["companerismo"] == zona) & 
            (df_db["mes_ano"] == periodo_str)
        ]
    else:
        df_filtrado = pd.DataFrame(columns=["companerismo", "mes_ano", "fecha", "familia", "telefono", "notas"])
    
    if df_filtrado.empty:
        st.info(f"Aún no hay familias registradas para {meses_nombres[mes_sel]} {anio_sel} en este compañerismo.")
    else:
        st.dataframe(
            df_filtrado[["fecha", "familia", "telefono", "notas"]],
            use_container_width=True
        )

with tab2:
    st.subheader("Regístrate para darles de comer")
    
    with st.form("form_registro_mes", clear_on_submit=True):
        f_fecha = st.date_input(
            "Fecha de la comida",
            datetime.date(anio_sel, mes_sel, 1)
        )
        f_nombre = st.text_input("Nombre de la Familia / Persona")
        f_tel = st.text_input("Número de Teléfono (WhatsApp)")
        f_notas = st.text_area("Notas adicionales (ej. hora acordada, restricciones)")
        
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            if f_nombre and f_tel:
                if f_fecha.month == mes_sel and f_fecha.year == anio_sel:
                    periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"
                    
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
                        st.success(f"✅ ¡Gracias {f_nombre}! Tu registro para el {f_fecha} se ha guardado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {e}")
                else:
                    st.warning(f"⚠️ La fecha seleccionada no corresponde a {meses_nombres[mes_sel]} {anio_sel}.")
            else:
                st.error(" Por favor completa al menos tu nombre y teléfono.")
