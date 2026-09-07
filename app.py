import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Comidas Misioneros - Apizaco y Tlaxco",
    layout="wide"
)

st.title("🍽️ Calendario de Comidas para Misioneros")

# ============================================
# CONEXIÓN A GOOGLE SHEETS
# ============================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success("✅ Conexión establecida")
except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    st.stop()

# Columnas esperadas
expected_columns = [
    "Compañerismo",
    "Mes-Año",
    "Fecha",
    "Familia / Hermano",
    "Teléfono",
    "Notas"
]

# ============================================
# LEER DATOS
# ============================================
try:
    df_db = conn.read(ttl=0)
    if df_db is None or df_db.empty or not all(col in df_db.columns for col in expected_columns):
        df_db = pd.DataFrame(columns=expected_columns)
    else:
        df_db = df_db[expected_columns]
    st.sidebar.success(f"✅ {len(df_db)} registros cargados")
except Exception as e:
    st.error(f"❌ Error al leer Google Sheets: {e}")
    df_db = pd.DataFrame(columns=expected_columns)

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
        index=8  # Septiembre por defecto
    )
with col_a:
    anio_sel = st.selectbox("Año", options=[2026, 2027], index=0)

st.header(f"Agenda para: {zona} — {meses_nombres[mes_sel]} {anio_sel}")

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs([" Ver Calendario del Mes", "✍️ Apuntarse a una fecha"])

with tab1:
    st.subheader(f"Registros de {meses_nombres[mes_sel]} {anio_sel}")
    periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"
    
    # Filtrar datos de forma segura
    if not df_db.empty and "Compañerismo" in df_db.columns and "Mes-Año" in df_db.columns:
        df_limpio = df_db.dropna(subset=["Compañerismo", "Mes-Año"])
        df_filtrado = df_limpio[
            (df_limpio["Compañerismo"] == zona) & 
            (df_limpio["Mes-Año"] == periodo_str)
        ]
    else:
        df_filtrado = pd.DataFrame(columns=expected_columns)
    
    if df_filtrado.empty:
        st.info(f"Aún no hay familias registradas para {meses_nombres[mes_sel]} {anio_sel} en este compañerismo.")
    else:
        st.dataframe(
            df_filtrado[["Fecha", "Familia / Hermano", "Teléfono", "Notas"]],
            use_container_width=True
        )
        if st.button("🖨️ Generar vista para imprimir este mes"):
            st.success("¡Vista lista para imprimir este mes sin tachones!")

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
                    nuevo_registro = pd.DataFrame([{
                        "Compañerismo": zona,
                        "Mes-Año": periodo_str,
                        "Fecha": str(f_fecha),
                        "Familia / Hermano": f_nombre,
                        "Teléfono": f_tel,
                        "Notas": f_notas,
                    }])
                    
                    try:
                        # Asegurar limpieza de filas vacías previas
                        df_db_clean = df_db.dropna(how="all")
                        df_updated = pd.concat([df_db_clean, nuevo_registro], ignore_index=True)
                        
                        # Actualizar en Google Sheets
                        conn.update(data=df_updated)
                        st.success(f"✅ ¡Gracias {f_nombre}! Tu registro para el {f_fecha} se ha guardado permanentemente en Google Sheets.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al sincronizar con Google Sheets: {e}")
                else:
                    st.warning(f"⚠️ La fecha seleccionada no corresponde a {meses_nombres[mes_sel]} {anio_sel}.")
            else:
                st.error("❌ Por favor completa al menos tu nombre y teléfono.")
