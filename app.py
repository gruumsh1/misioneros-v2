import datetime
import pandas as pd
import streamlit as st
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.set_page_config(page_title="Comidas Misioneros - Apizaco y Tlaxco", layout="wide")
st.title("🍽️ Calendario de Comidas para Misioneros")

# ============================================
# CONFIGURACIÓN DIRECTA (sin secrets.toml)
# ============================================
SPREADSHEET_ID = "1DEg_PWnzuzXeAL9r6GfHjphX_8we9rsDPgdQS5RT6Q0"
SHEET_NAME = "Hoja 1"  # Cambia esto si tu hoja tiene otro nombre

# Credenciales del service account (PEGA AQUÍ EL CONTENIDO DE TU JSON NUEVO)
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "calendario-misioneros",
    "private_key_id": "22c91ea8109bdf8a85c1e19ce357d267291a41d4",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggsjAgEAAoIBAQD0BGA/TYRJDeBy\nn1ChJqIO0H1av7ePdR8iPXIUckakDM+JBJ2nR1D+UTsSKtCEauV2S8ahYLuG5C+Fh\nnavGHGasMB73QRtl7PP/jAU8x/FEtUeBdyc2UkKXZmW0wdL1bqqAhtgcvaGNYzZj+\n/noe8fDNgYfLCDTm5o9BOy3X2/NfhHBTxxthV6SL7t/ZG4MS31v81E0OVFXH2O1HE\n/n0WEbTz2eYn+fyghUJIXVRh9G4GvLK//kHRL0dbjKMnPzue9QEqtR872eaJ1b6Te\n/n2htpff0DK5FBeKYD7Z0zJMdw9300KhlwSA0CEHpoL2GnkofS1LNVx7inR830JUpF\n/n0Wi75gf/AgMBAAECggEAM4M7386dc7ccX8ZORJ9Xtk6PwSRYJApvlVEQhVEssc67\n/nV0qxYmGG/ewFEEnpaHK1ZXL55u6Ma33aKDGr3bckbI1GP2DJ9818cJE+vPX7KMVL\n/n4HJZXUC8tU4WuGWPnfOR2G61hPkYXAlIXzDCjjgJQuMWCWoLulrwq//4qgyXV7oV1\n/nMmu55vhuA20txrqtA1P3Mcqqkep5HDoGzoFtxzALJ6Mos2tCGTSa0lLpSaqGXu5a\n/nWksUu/07TrAzkvG7eAtPlc4E16jzNnbseLgj2RK/E0CZmsfd1nAzHyurSBB75e0D\n/nULQIB4p0gZ103qBB/EEPXuMD4ZcVHX1hV3M4ooAxCQKBgQDs8thDrfOQV/eAXBtN\n/n3uKJwyfQaDoFfkeV3vXT989ypYT/0h5Ia8e14WiCXh8CdKQWBSScmB3wh5Zg19Ae\n/nlfqLzX1bT2zpLTc69E6AQq3iZIP/mg5r4135Npf+Wn5oa+rlx8Mir69UIB93JL8R\n/n050Hrvas64Fs6qQkJVZCy7sewtQKBgQDoTlLAG9JOYk85IecmbvhfeH5DQFkLE820\n/nmdul9GXYtlTcx5cE138DMw92dAywpqrAjex84BYNnylWi1F9epMhy/ztB61Mf0qU\n/nBUBwJAabsA6V1+8c1vCsp575YqjMFQjEx02XlkZ04aaZGrRPbHxZa/ujMbLCDCh\n/ndv59yqMqYwKBgASR61nLyRnjgh+7pwspcVUW3n22HOf3JIppCo5UCTw81QPaGZtr\n/n+L4ZStq41gBGH60NFYfTp0AsXUog33K3kc2AeQa50W/t3l1Tw2/VseTb62/SmNSb\n/n3gQgeW3+cNGyvyVaZPkWStltAzZZFxx06FeFmFxdbpGzNNTfo5REN3jBAoGBaMVc\n/nNpVl0kUP1462Pp1oGlckyxoTBOjCh18113AdInnFitFgswheHBYiZB30Dm2mxYHC\n/nP9NUgsA32ceno0DSk0M0wDZBvC3eCp/xEbmuWyWeeiye6hD5Oqw5H5qDfcKwUhZyT\n/nkha2q1Xmes3pI+HuHax4vH0a1M0DBsNJD10pvJchAa0GAfgwR/6ZagMYnYUhwhhSs\n/nkPS4wxAapEpBk8reJcnHdxSkNI/JnTRF4vhDBYLX8XvEokTnb9YF2EPG+5LZbes78\n/nJILHhk/F0G//FwH3UZ7LRTHYnwfwQKybBUtdS0lkQ84X0VPHkLvmcm+vtinTvGpH\n/nKEPSp0fXbZjlznWFkcD1EV8=\n-----END PRIVATE KEY-----\n",
    "client_email": "streamlit-bot@calendario-misioneros.iam.gserviceaccount.com",
    "client_id": "117212862484663181550",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-bot%40calendario-misioneros.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# ============================================
# AUTENTICACIÓN DIRECTA
# ============================================
try:
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=credentials)
    st.sidebar.success("✅ Conexión directa establecida")
except Exception as e:
    st.error(f"❌ Error de autenticación: {e}")
    st.stop()

# ============================================
# FUNCIONES PARA LEER/ESCRIBIR
# ============================================
def read_sheet():
    """Lee todos los datos de la hoja"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_NAME
        ).execute()
        values = result.get("values", [])
        if not values:
            return pd.DataFrame(columns=["Compañerismo", "Mes-Año", "Fecha", "Familia / Hermano", "Teléfono", "Notas"])
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except Exception as e:
        st.error(f"Error al leer: {e}")
        return pd.DataFrame()

def write_sheet(df):
    """Escribe todos los datos en la hoja"""
    try:
        values = [df.columns.tolist()] + df.values.tolist()
        body = {"values": values}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_NAME,
            valueInputOption="RAW",
            body=body
        ).execute()
        return True
    except Exception as e:
        st.error(f"Error al escribir: {e}")
        return False

# ============================================
# CARGAR DATOS
# ============================================
expected_columns = ["Compañerismo", "Mes-Año", "Fecha", "Familia / Hermano", "Teléfono", "Notas"]

try:
    df_db = read_sheet()
    if df_db.empty or not all(col in df_db.columns for col in expected_columns):
        df_db = pd.DataFrame(columns=expected_columns)
    else:
        df_db = df_db[expected_columns]
    st.sidebar.success(f"✅ {len(df_db)} registros cargados")
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    df_db = pd.DataFrame(columns=expected_columns)

# ============================================
# FILTROS
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
tab1, tab2 = st.tabs(["📅 Ver Calendario del Mes", "️ Apuntarse a una fecha"])

with tab1:
    st.subheader(f"Registros de {meses_nombres[mes_sel]} {anio_sel}")
    periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"
    
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
        st.dataframe(df_filtrado[["Fecha", "Familia / Hermano", "Teléfono", "Notas"]], use_container_width=True)

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
            if not f_nombre or not f_tel:
                st.error("❌ Por favor completa al menos tu nombre y teléfono.")
            elif f_fecha.month != mes_sel or f_fecha.year != anio_sel:
                st.warning(f"⚠️ La fecha seleccionada no corresponde a {meses_nombres[mes_sel]} {anio_sel}.")
            else:
                nuevo_registro = pd.DataFrame([{
                    "Compañerismo": zona,
                    "Mes-Año": periodo_str,
                    "Fecha": str(f_fecha),
                    "Familia / Hermano": f_nombre,
                    "Teléfono": f_tel,
                    "Notas": f_notas,
                }])
                
                df_db_clean = df_db.dropna(how="all")
                df_updated = pd.concat([df_db_clean, nuevo_registro], ignore_index=True)
                
                if write_sheet(df_updated):
                    st.success(f"✅ ¡Gracias {f_nombre}! Tu registro para el {f_fecha} se ha guardado.")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar en Google Sheets.")
