import datetime
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Comidas Misioneros - Apizaco y Tlaxco", layout="wide")
st.title("️ Calendario de Comidas para Misioneros")

# Credenciales hardcodeadas (temporalmente para probar)
# Credenciales hardcodeadas (temporalmente para probar)
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "calendario-misioneros",
    "private_key_id": "22c91ea8109bdf8a85c1e19ce357d267291a41d4",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDXBGA/TYRJDeBy
1ChJqIO0H1av7ePdR8iPXIUckakDM+JBJ2nRlD+UTsSKtCEauV2S8ahYLuG5C+Fh
avGHGasMB73QRtl7PP/jAU8x/FEtUeBdyczUUkXZmWDwd1lbqqAhtgcvaGNYvZj+
oe8fDNgYflCDTm5o9BOy3X2/NfhHBTxxtHV6SL7t/ZG4MS3lv81EOQVFXHH2OlHE
0WEbTz2eYn+fyghUJIXVRh9G4GvlK//kHRLQdbjKMnPzue9QEqtiR872eaI1b6Te
2htpff0DK5FBeKDY7ZQzJMdw9R3QQKhLwSA0CEHp0k2GnkofSlNVx7inR83OJUpF
OWi75gf/AgMBAAECggEAM4M7386dc7ccX8ZORJ9Xtk6PwSRYJApvlVEQHvESsc67
VOqxYmGG/ewFEEnpaHKiZXL55u6Ma33aKDGr3bcbkI1GP2DJ98l8cJE+vPX7KMVl
4HJZXUC8tU4WuGWPhfOR26G1hPkYXAlIXzDCjgjQuMWCWoLu1rwq//4qgyXV7oV1
Mmu55vhuA20txrqtAiP3Mcqqkep5HDoGzoFtxzALJ6Mos2tCGTSaOlLpSaqGXu5a
WKsUu/07TrAzkvG7eAtPlc4E16jzNnbseLgJ2RK/E0CZmsfd1nAzHyu+SBB75eDD
ULQIB4p0gZl03qBB/EEPXuMD4ZcVHXihV3M4ooAxCQKBgQDs8tHDrFQV/eBAXBtN
3uKJwyfQaDoFrkeV3vXT989ypYT/0h5Ia8e14WiCXh8CdKQWBS5cmB3wh5Zg19Ae
lfqLzXlbT2zpLTc69E6AOq3iZIP/mg5r4135Npf+Wn5oa+r1x8Mir69UIB93Jl8R
05OHrvas64fs6qOkJVZCY5ewtQKBgQDoTiLAG9JOYk85IecmbvhfeH5DQFkLE820
mduL9GXYtLTcx5cEl38DMw92dAywpqrAjex84BYNnyWVi1F9epMhy/ztB6iMf0qU
BU8wJAabsA6Vl+8c1vCsp575YqjMFQjExO2XlkZO4aaZ6rRPbHxZa/ujMbLCDCh/
dv59yqMqYwKBgASR6lnLyRNjgh+7pwspcVUW3n22hOf3JIpPco5UCTw81QPaGZtr
+L4ZStq41gBGH6QNFYfTp0AsXUog33K3kc2AeQa50W/t31LTw2/VseTb62/SmNSb
3gQgeW3+cNGywyVaZPkWSltlAzZZFxxQ6FeFmFxdbpGzNNTFo5REN3jBAoGBAMvG
PpVl0kUP1462Pp1oGlckyx0TBQjChl8113AdInnFiiFgswhEHBYiZB30Dm2mxYHC
/P9NUgsA32ceno0DSK0M0wDZBvC3eCP/xEbmUyWeeiye6hDSOqw5HSqFcKwUh2yT
kha2q1Xmes3pI+HHuAx4vHOa1MODBsNJDlQpvJchAoGAfgwR/6ZagMYnYUhhwhSs
kPS4wxApEpBk8reJCnHdxSkNI/JnTRF4vhDBYLX8XvEokTnb9YF2EPG+5LZbeS78
JILHhk/F0G//FwH3UZ7lRTHYnwfwQKybBUtdSQlkQ84X0VPHkLvmcm+vtinTvGpH
KEP5P0fXbZjlznWFkCD1EV8=
-----END PRIVATE KEY-----""",
    "client_email": "streamlit-bot@calendario-misioneros.iam.gserviceaccount.com",
    "client_id": "117212862484663181550",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-bot%40calendario-misioneros.iam.gserviceaccount.com"
}

# Autenticación directa con gspread
try:
    credentials = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)
    
    # Abrir la hoja de cálculo
    spreadsheet_id = "1DEg_PWnzuzXeAL9r6GfHjphX_8we9rsDPgdQS5RT6Q0"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.sheet1
    
    st.sidebar.success("✅ Conectado con gspread")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.stop()

# Columnas esperadas
expected_columns = ["Compañerismo", "Mes-Año", "Fecha", "Familia / Hermano", "Teléfono", "Notas"]

# Leer datos
try:
    data = worksheet.get_all_records()
    df_db = pd.DataFrame(data)
    if df_db.empty or not all(col in df_db.columns for col in expected_columns):
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
                nuevo = [zona, periodo_str, str(f_fecha), f_nombre, f_tel, f_notas]
                try:
                    worksheet.append_row(nuevo)
                    st.success(f"✅ ¡Guardado con éxito para el {f_fecha}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")
            else:
                st.error("❌ Completa nombre, teléfono y verifica la fecha.")
