import datetime
import html
import io
import math
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont

# ============================================
# CONFIGURACIÓN: una sola columna, sin sidebar
# ============================================
st.set_page_config(
    page_title="Comidas para Misioneros",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================
# ESTILOS: paleta tipo Iglesia SUD + ajustes móviles
# ============================================
st.markdown("""
<style>
html{font-size:17px}
body,.stMarkdown,p,li{color:#1F2A37}
p,li{line-height:1.6}
h1{font-size:1.7rem;font-weight:800;color:#12395B}
h2,h3{font-size:1.25rem;font-weight:700;margin-bottom:.4rem;color:#12395B}
.muted{color:#55677A;font-size:.95rem;line-height:1.5}

[data-testid="stSidebar"]{display:none}
#MainMenu,footer{visibility:hidden}

[data-testid="stVerticalBlockBorderWrapper"]{background:#F2F6FA;border-color:#D9E1EA;border-radius:14px}
[data-testid="stVerticalBlockBorderWrapper"] > div{background:#F2F6FA}

[data-testid="stButton"] button,[data-testid="stForm"] button{
  min-height:48px;font-size:1rem;font-weight:600;border-radius:10px}
[data-testid="stBaseButton-primary"]{background:#1668C3 !important;color:#FFFFFF !important;border:none !important}

[data-testid="stPills"] button,[data-testid="stSegmentedControl"] button{
  min-height:44px;font-size:1rem;padding:.4rem .95rem;border-radius:999px}

[data-testid="stTextInput"] input,[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea{
  min-height:48px;font-size:1rem;border-color:#B9C2CC;border-radius:10px}

:focus-visible{outline:3px solid #12395B;outline-offset:2px}

/* ---- Calendario de rejilla ---- */
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-top:.6rem}
.cal-head{background:#12395B;color:#FFFFFF;text-align:center;font-weight:700;
  font-size:.8rem;padding:8px 2px;border-radius:8px;letter-spacing:.03em}
.cal-cell{background:#FFFFFF;border:1.5px solid #D9E1EA;border-radius:10px;padding:6px 4px;min-height:78px}
.cal-cell.ocupado{background:#E7F0FA;border-color:#1668C3}
.cal-cell.hoy{border:3px solid #B98A2E}
.cal-cell.lunes{background:#EEF1F4;border-style:dashed;border-color:#B9C2CC}
.cal-cell.vacio{border:none;background:transparent;min-height:0}
.cal-day{font-size:1.05rem;font-weight:800;color:#1F2A37}
.cal-state{font-size:.68rem;font-weight:700;letter-spacing:.05em;margin-top:2px}
.st-libre{color:#2E6B34}
.st-ocupado{color:#0F4C81}
.st-descanso{color:#55677A}
.cal-fam{font-size:.72rem;color:#1F2A37;font-weight:600;margin-top:3px;line-height:1.25;word-break:break-word}
.cal-tel{font-size:.68rem;color:#55677A;word-break:break-word}

/* ---- Agenda vertical (solo celular, vive en la tarjeta 4) ---- */
.solo-movil{display:none}
.agenda-row{background:#FFFFFF;border:1px solid #D9E1EA;border-radius:10px;
  padding:.55rem .6rem;margin-bottom:.45rem;display:flex;gap:.6rem;align-items:flex-start}
.agenda-row.ocupado{background:#E7F0FA;border-color:#1668C3}
.agenda-row.lunes{background:#EEF1F4;border-style:dashed;border-color:#B9C2CC}
.agenda-row.hoy{border:2px solid #B98A2E}
.agenda-dia{font-weight:800;color:#12395B;min-width:3.6rem;line-height:1.3}
.agenda-cuerpo{flex:1;min-width:0}
.agenda-estado{font-size:.78rem;font-weight:700;letter-spacing:.04em}
.agenda-fam{font-weight:700;color:#1F2A37;word-break:break-word}
.agenda-row a{color:#0F4C81;font-weight:700;word-break:break-word}

/* Lista de escritorio */
.reg-row{background:#FFFFFF;border:1px solid #D9E1EA;border-radius:10px;padding:.6rem .7rem;margin-bottom:.5rem}
.reg-fecha{font-weight:800;font-size:1rem;color:#12395B}
.reg-fam{font-weight:600}
.reg-row a{color:#0F4C81;font-weight:700}

/* Leyenda */
.legend{display:flex;gap:.9rem;flex-wrap:wrap;margin-top:.7rem;font-size:.85rem;color:#1F2A37}
.chip{display:inline-block;width:14px;height:14px;border-radius:4px;border:1.5px solid #D9E1EA;vertical-align:-2px;margin-right:6px}
.chip-libre{background:#FFFFFF}
.chip-ocup{background:#E7F0FA;border-color:#1668C3}
.chip-desc{background:#EEF1F4;border-style:dashed;border-color:#B9C2CC}

.t-corto{display:none}

/* ===== Ajustes finos de ancho en celular ===== */
@media (max-width:640px){
  .solo-escritorio{display:block}
  .solo-movil{display:block}
  .block-container,[data-testid="stAppViewBlockContainer"]{
    padding-left:0.35rem !important;padding-right:0.35rem !important}
  [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stVerticalBlockBorderWrapper"] > div{
    padding:0.35rem !important}
  .cal-grid{gap:2px;grid-template-columns:0.55fr repeat(6,1fr)}
  .cal-head{font-size:.55rem;padding:5px 1px;letter-spacing:0}
  .cal-cell{min-height:56px !important;padding:3px 2px}
  .cal-day{font-size:.9rem}
  .cal-state{font-size:.5rem}
  .cal-fam{font-size:.6rem}
  .cal-tel{font-size:.52rem}
  .t-largo{display:none}
  .t-corto{display:inline}
  .cal-cell.lunes .cal-state{font-size:.45rem}
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
# CATÁLOGOS
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
meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_CORTOS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

hoy = datetime.date.today()

# ============================================
# GENERADORES DE IMAGEN Y PDF DEL CALENDARIO
# ============================================
def _fuente(size, bold=False):
    rutas = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for r in rutas:
        try:
            return ImageFont.truetype(r, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size)
    except Exception:
        return ImageFont.load_default()

def _wrap_pix(draw, texto, font, max_w):
    lineas = []
    for parrafo in str(texto).split("\n"):
        act = ""
        for p in parrafo.split(" "):
            prueba = f"{act} {p}".strip()
            if draw.textlength(prueba, font=font) <= max_w or not act:
                act = prueba
            else:
                lineas.append(act)
                act = p
        lineas.append(act)
    return lineas

def _datos_mes(anio, mes, regs_por_fecha):
    p_dia = datetime.date(anio, mes, 1)
    if mes == 12:
        u_dia = datetime.date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        u_dia = datetime.date(anio, mes + 1, 1) - timedelta(days=1)
    n_dias = (u_dia - p_dia).days + 1
    return p_dia, n_dias, p_dia.weekday()

def generar_png_calendario(anio, mes, titulo, regs_por_fecha, fecha_hoy):
    p_dia, n_dias, offset = _datos_mes(anio, mes, regs_por_fecha)
    W = 1080
    pad = 20
    head_h = 95
    dayhead_h = 46
    cell_w = (W - 2 * pad) / 7
    cell_h = 165
    filas = math.ceil((offset + n_dias) / 7)
    H = pad + head_h + dayhead_h + filas * cell_h + 70

    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)

    f_tit = _fuente(36, True)
    f_sub = _fuente(22)
    f_head = _fuente(21, True)
    f_day = _fuente(27, True)
    f_fam = _fuente(17)
    f_tel = _fuente(15)
    f_est = _fuente(15, True)
    f_leg = _fuente(18)

    d.text((pad, pad), titulo, font=f_tit, fill="#12395B")
    d.text((pad, pad + 48), f"Comidas para misioneros · Apizaco y Tlaxco", font=f_sub, fill="#55677A")

    y0 = pad + head_h
    for i, nombre in enumerate(DIAS_CORTOS):
        x = pad + i * cell_w
        d.rectangle([x, y0, x + cell_w - 4, y0 + dayhead_h - 4], fill="#12395B")
        w_txt = d.textlength(nombre, font=f_head)
        d.text((x + (cell_w - 4 - w_txt) / 2, y0 + 10), nombre, font=f_head, fill="#FFFFFF")

    gy = y0 + dayhead_h
    for idx in range(filas * 7):
        dia = idx - offset + 1
        col = idx % 7
        row = idx // 7
        x = pad + col * cell_w
        y = gy + row * cell_h
        if dia < 1 or dia > n_dias:
            continue
        f_act = datetime.date(anio, mes, dia)
        regs = regs_por_fecha.get(str(f_act), [])
        es_lunes = f_act.weekday() == 0
        es_hoy = f_act == fecha_hoy

        if es_lunes:
            fill, border = "#EEF1F4", "#B9C2CC"
        elif regs:
            fill, border = "#E7F0FA", "#1668C3"
        else:
            fill, border = "#FFFFFF", "#D9E1EA"
        d.rectangle([x, y, x + cell_w - 4, y + cell_h - 6], fill=fill, outline=border, width=2)
        if es_hoy:
            d.rectangle([x, y, x + cell_w - 4, y + cell_h - 6], outline="#B98A2E", width=5)

        d.text((x + 8, y + 6), str(dia), font=f_day, fill="#1F2A37")

        yy = y + 42
        if es_lunes:
            d.text((x + 8, yy), "DESCANSO", font=f_est, fill="#55677A")
        elif regs:
            for r in regs:
                for ln in _wrap_pix(d, r["familia"], f_fam, cell_w - 16):
                    d.text((x + 8, yy), ln, font=f_fam, fill="#1F2A37")
                    yy += 21
                for ln in _wrap_pix(d, r["telefono"], f_tel, cell_w - 16):
                    d.text((x + 8, yy), ln, font=f_tel, fill="#55677A")
                    yy += 18
        else:
            d.text((x + 8, yy), "LIBRE", font=f_est, fill="#2E6B34")

    ly = gy + filas * cell_h + 12
    d.rectangle([pad, ly, pad + 22, ly + 22], fill="#FFFFFF", outline="#D9E1EA", width=2)
    d.text((pad + 30, ly + 2), "Libre: puede anotarse", font=f_leg, fill="#1F2A37")
    d.rectangle([pad + 300, ly, pad + 322, ly + 22], fill="#E7F0FA", outline="#1668C3", width=2)
    d.text((pad + 330, ly + 2), "Con familia: día asignado", font=f_leg, fill="#1F2A37")
    d.rectangle([pad + 660, ly, pad + 682, ly + 22], fill="#EEF1F4", outline="#B9C2CC", width=2)
    d.text((pad + 690, ly + 2), "Lunes: descanso", font=f_leg, fill="#1F2A37")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def generar_pdf_calendario(anio, mes, titulo, regs_por_fecha, fecha_hoy):
    from fpdf import FPDF
    p_dia, n_dias, offset = _datos_mes(anio, mes, regs_por_fecha)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(18, 57, 91)
    pdf.cell(0, 8, titulo)
    pdf.ln(9)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(85, 103, 122)
    pdf.cell(0, 6, "Comidas para misioneros - Apizaco y Tlaxco")
    pdf.ln(9)

    cw = (210 - 20) / 7
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(18, 57, 91)
    pdf.set_text_color(255, 255, 255)
    for nombre in DIAS_CORTOS:
        pdf.cell(cw, 7, nombre, border=1, align="C", fill=True)
    pdf.ln()

    line_h = 3.8
    pdf.set_text_color(31, 42, 55)
    filas = math.ceil((offset + n_dias) / 7)
    for row in range(filas):
        celdas = []
        max_lineas = 1
        pdf.set_font("Helvetica", "", 7.5)
        for col in range(7):
            dia = row * 7 + col - offset + 1
            if dia < 1 or dia > n_dias:
                celdas.append(None)
                continue
            f_act = datetime.date(anio, mes, dia)
            regs = regs_por_fecha.get(str(f_act), [])
            es_lunes = f_act.weekday() == 0
            es_hoy = f_act == fecha_hoy
            lineas = [str(dia)]
            if es_lunes:
                lineas.append("DESCANSO")
                estado = "lunes"
            elif regs:
                estado = "ocupado"
                for r in regs:
                    txt = f'{r["familia"]} {r["telefono"]}'
                    act = ""
                    for p in txt.split(" "):
                        prueba = f"{act} {p}".strip()
                        if pdf.get_string_width(prueba) <= cw - 3 or not act:
                            act = prueba
                        else:
                            lineas.append(act)
                            act = p
                    lineas.append(act)
            else:
                lineas.append("LIBRE")
                estado = "libre"
            max_lineas = max(max_lineas, len(lineas))
            celdas.append((lineas, estado, es_hoy))
        row_h = max(14, max_lineas * line_h + 3)
        y0 = pdf.get_y()
        for col in range(7):
            info = celdas[col]
            if info is None:
                continue
            lineas, estado, es_hoy = info
            x = 10 + col * cw
            if estado == "ocupado":
                pdf.set_fill_color(231, 240, 250); pdf.set_draw_color(22, 104, 195)
            elif estado == "lunes":
                pdf.set_fill_color(238, 241, 244); pdf.set_draw_color(185, 194, 204)
            else:
                pdf.set_fill_color(255, 255, 255); pdf.set_draw_color(217, 225, 234)
            pdf.set_line_width(0.8 if es_hoy else 0.2)
            if es_hoy:
                pdf.set_draw_color(185, 138, 46)
            pdf.rect(x, y0, cw, row_h, style="DF")
            pdf.set_line_width(0.2)
            yy = y0 + 1.5
            pdf.set_xy(x + 1, yy)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(31, 42, 55)
            pdf.cell(cw - 2, line_h, lineas[0])
            yy += line_h
            pdf.set_font("Helvetica", "", 7.5)
            for ln in lineas[1:]:
                pdf.set_xy(x + 1, yy)
                pdf.cell(cw - 2, line_h, ln)
                yy += line_h
        pdf.set_y(y0 + row_h)

    pdf.ln(4)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(31, 42, 55)
    pdf.cell(0, 6, "Libre: puede anotarse   |   Con familia: dia asignado   |   Lunes: descanso")
    return pdf.output()

# ============================================
# TARJETA 1: SELECCIÓN (sin desplegables)
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

    st.markdown("##### 2. Mes que está viendo")
    if "view_ym" not in st.session_state:
        st.session_state.view_ym = (hoy.year, hoy.month)

    def shift_month(ym, delta):
        y, m = ym
        m += delta
        if m < 1:
            y, m = y - 1, 12
        elif m > 12:
            y, m = y + 1, 1
        nuevo = (y, m)
        if nuevo < (2025, 1):
            nuevo = (2025, 1)
        if nuevo > (2027, 12):
            nuevo = (2027, 12)
        return nuevo

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("Anterior", use_container_width=True, key="mes_prev"):
            st.session_state.view_ym = shift_month(st.session_state.view_ym, -1)
            st.rerun()
    with c2:
        y_view, m_view = st.session_state.view_ym
        st.markdown(
            f"<p style='text-align:center;font-weight:800;font-size:1.15rem;margin:0;padding:.55rem 0;color:#12395B'>{meses_nombres[m_view]} {y_view}</p>",
            unsafe_allow_html=True,
        )
    with c3:
        if st.button("Siguiente", use_container_width=True, key="mes_next"):
            st.session_state.view_ym = shift_month(st.session_state.view_ym, 1)
            st.rerun()

    if st.session_state.view_ym != (hoy.year, hoy.month):
        if st.button("Ir al mes actual", use_container_width=True, key="go_today"):
            st.session_state.view_ym = (hoy.year, hoy.month)
            st.rerun()

    mes_sel = st.session_state.view_ym[1]
    anio_sel = st.session_state.view_ym[0]

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
# TARJETA 2: CALENDARIO + DESCARGAS
# ============================================
with st.container(border=True):
    st.markdown(f"### {meses_nombres[mes_sel]} {anio_sel} · {zona}")

    html_cal = '<div class="solo-escritorio"><div class="cal-grid">'
    for d in DIAS_CORTOS:
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
            html_cal += '<div class="cal-state st-descanso"><span class="t-largo">DESCANSO</span><span class="t-corto">DES</span></div>'
        elif regs:
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
      <span><span class="chip chip-ocup"></span>Con familia: día asignado</span>
      <span><span class="chip chip-desc"></span>Lunes: descanso</span>
    </div>
    </div>
    """
    st.markdown(html_cal, unsafe_allow_html=True)

    # ---- Botones de descarga del calendario ----
    titulo_cal = f"{meses_nombres[mes_sel]} {anio_sel} - {zona}"
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        try:
            png_bytes = generar_png_calendario(anio_sel, mes_sel, titulo_cal, registros_por_fecha, hoy)
            st.download_button(
                "Descargar imagen (PNG)",
                data=png_bytes,
                file_name=f"calendario_{periodo_str}_{zona_corta.replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True,
            )
        except Exception:
            st.caption("No se pudo generar la imagen en este momento.")
    with col_d2:
        try:
            pdf_bytes = generar_pdf_calendario(anio_sel, mes_sel, titulo_cal, registros_por_fecha, hoy)
            st.download_button(
                "Descargar PDF",
                data=pdf_bytes,
                file_name=f"calendario_{periodo_str}_{zona_corta.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_pdf",
            )
        except Exception:
            st.caption("No se pudo generar el PDF en este momento.")

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
        and datetime.date(anio_sel, mes_sel, d) >= hoy
    ]

    if ultimo_dia < hoy:
        st.info("Está viendo un mes pasado. Solo consulta; los registros nuevos se hacen en el mes actual o en meses futuros.")
    elif not fechas_disponibles:
        st.warning("No quedan días disponibles este mes. Revise el siguiente mes.")
    else:
        with st.form("form_registro", clear_on_submit=True):
            st.markdown("**Día disponible** (toque el campo para abrir el calendario)")
            min_fechar = max(datetime.date(anio_sel, mes_sel, 1), hoy)
            f_fecha = st.date_input(
                "Día",
                min_value=min_fechar,
                max_value=datetime.date(anio_sel, mes_sel, dias_mes),
                value=fechas_disponibles[0] if fechas_disponibles else min_fechar,
                label_visibility="collapsed",
            )
            f_nombre = st.text_input("Nombre de la familia o persona")
            f_tel = st.text_input("Teléfono de WhatsApp")
            f_notas = st.text_area("Nota opcional (hora acordada, restricciones)")

            enviado = st.form_submit_button("Guardar mi registro", type="primary", use_container_width=True)

            if enviado:
                if not f_nombre.strip() or not f_tel.strip():
                    st.error("Escriba al menos su nombre y su teléfono.")
                elif f_fecha < hoy:
                    st.error("No puede anotarse en una fecha pasada.")
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
# TARJETA 4: LISTA / AGENDA (después del registro)
# ============================================
with st.container(border=True):
    st.markdown(f"### Familias anotadas en {meses_nombres[mes_sel]}")
    if df_mes.empty:
        st.markdown('<p class="muted">Aún no hay familias anotadas este mes en este compañerismo.</p>', unsafe_allow_html=True)

    # ---- Agenda día por día (solo celular) ----
    html_agenda = '<div class="solo-movil">'
    for dia in range(1, dias_mes + 1):
        f_act = datetime.date(anio_sel, mes_sel, dia)
        f_str = str(f_act)
        es_lunes = f_act.weekday() == 0
        es_hoy = f_act == hoy
        regs = registros_por_fecha.get(f_str, [])

        clase = "agenda-row"
        if es_lunes:
            clase += " lunes"
        elif es_hoy:
            clase += " hoy"
        if regs and not es_lunes:
            clase += " ocupado"

        html_agenda += f'<div class="{clase}">'
        html_agenda += f'<div class="agenda-dia">{DIAS_CORTOS[f_act.weekday()]} {dia}</div>'
        html_agenda += '<div class="agenda-cuerpo">'
        if es_lunes:
            html_agenda += '<div class="agenda-estado st-descanso">DESCANSO</div>'
        elif regs:
            for r in regs:
                tel_clean = "".join(ch for ch in r["telefono"] if ch.isdigit() or ch == "+")
                html_agenda += f'<div class="agenda-fam">{html.escape(r["familia"])}</div>'
                html_agenda += f'<a href="tel:{tel_clean}">Llamar: {html.escape(r["telefono"])}</a>'
                if r["notas"]:
                    html_agenda += f'<div class="muted">{html.escape(r["notas"])}</div>'
        else:
            html_agenda += '<div class="agenda-estado st-libre">LIBRE</div>'
        html_agenda += '</div></div>'
    html_agenda += '</div>'
    st.markdown(html_agenda, unsafe_allow_html=True)

    # ---- Lista detallada (solo escritorio / tablet) ----
    if not df_mes.empty:
        html_lista = '<div class="solo-escritorio">'
        for _, row in df_mes.sort_values("fecha").iterrows():
            f_obj = datetime.date.fromisoformat(str(row["fecha"])[:10])
            tel_raw = str(row["telefono"])
            tel_link = "".join(ch for ch in tel_raw if ch.isdigit() or ch == "+")
            notas = str(row["notas"]) if pd.notna(row["notas"]) else ""
            html_lista += f"""
            <div class="reg-row">
              <div class="reg-fecha">{DIAS_SEMANA[f_obj.weekday()]} {f_obj.day} de {meses_nombres[f_obj.month].lower()}</div>
              <div class="reg-fam">{html.escape(str(row['familia']))}</div>
              <a href="tel:{tel_link}">Llamar: {html.escape(tel_raw)}</a>
            """
            if notas:
                html_lista += f'<div class="muted">Nota: {html.escape(notas)}</div>'
            html_lista += '</div>'
        html_lista += '</div>'
        st.markdown(html_lista, unsafe_allow_html=True)

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
