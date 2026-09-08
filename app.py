import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Comidas Misioneros - Apizaco y Tlaxco", layout="wide")
st.title("🍽️ Calendario de Comidas para Misioneros")

# Conexión a Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success("✅ Conexión establecida")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.stop()

# Columnas esperadas
expected_columns = ["Compañerismo", "Mes-Año", "Fecha", "Familia / Hermano", "Teléfono", "Notas"]

# Leer datos
try:
    df_db = conn.read(ttl=0)
    if df_db is None or df_db.empty or not all(col in df_db.columns for col in expected_columns):
        df_db = pd.DataFrame(columns=expected_columns)
    else:
        df_db = df_db[expected_columns]
    st.sidebar.success(f"✅ {len(df_db)} registros cargados")
except Exception as e:
    st.error(f"❌ Error al leer: {e}")
    df_db = pd.DataFrame(columns=expected_columns)

# Filtros
st.sidebar.header("Filtros de Visualización")
zona = st.sidebar.selectbox("Compañerismo:", ["Apizaco 1 (Hno. Ulises / Galaviz)", "Apizaco 2 (Hno. Jorge Álvarez)", "Apizaco 3 (Hno. Jorge Luis Pérez)", "Tlaxco"])

meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

col_m, col_a = st.sidebar.columns(2)
with col_m:
    mes_sel = st.selectbox("Mes", options=list(meses_nombres.keys()), format_func=lambda x: meses_nombres[x], index=8)
with col_a:
    anio_sel = st.selectbox("Año", options=[2026, 2027], index=0)

st.header(f"Agenda para: {zona} — {meses_nombres[mes_sel]} {anio_sel}")

tab1, tab2 = st.tabs(["📅 Ver Calendario del Mes", "✍️ Apuntarse a una fecha"])

with tab1:
    periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"
    if not df_db.empty and "Compañerismo" in df_db.columns and "Mes-Año" in df_db.columns:
        df_limpio = df_db.dropna(subset=["Compañerismo", "Mes-Año"])
        df_filtrado = df_limpio[(df_limpio["Compañerismo"] == zona) & (df_limpio["Mes-Año"] == periodo_str)]
    else:
        df_filtrado = pd.DataFrame(columns=expected_columns)
    
    if df_filtrado.empty:
        st.info(f"Aún no hay registros para {meses_nombres[mes_sel]} {anio_sel}.")
    else:
        st.dataframe(df_filtrado[["Fecha", "Familia / Hermano", "Teléfono", "Notas"]], use_container_width=True)

with tab2:
    with st.form("form_registro", clear_on_submit=True):
        f_fecha = st.date_input("Fecha", datetime.date(anio_sel, mes_sel, 1))
        f_nombre = st.text_input("Nombre de la Familia / Persona")
        f_tel = st.text_input("Teléfono (WhatsApp)")
        f_notas = st.text_area("Notas")
        
        if st.form_submit_button("Guardar Registro"):
            if f_nombre and f_tel and f_fecha.month == mes_sel and f_fecha.year == anio_sel:
                nuevo = pd.DataFrame([{"Compañerismo": zona, "Mes-Año": periodo_str, "Fecha": str(f_fecha), "Familia / Hermano": f_nombre, "Teléfono": f_tel, "Notas": f_notas}])
                try:
                    df_actualizado = pd.concat([df_db.dropna(how="all"), nuevo], ignore_index=True)
                    conn.update(data=df_actualizado)
                    st.success(f"✅ ¡Guardado con éxito para el {f_fecha}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")
            else:
                st.error("❌ Completa nombre, teléfono y verifica la fecha.")
