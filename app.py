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
# REGLAS AUTOMÁTICAS DE APERTURA DE MES
# ============================================
UMBRAL_DIAS_LIBRES = 3      # con este número de días libres o menos, se avisa del mes siguiente
MESES_ADELANTE_MAX = 3      # cuántos meses avanza la búsqueda automática de lugar

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

/* ---- Agenda vertical (solo celular) ---- */
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
# LEER REGISTROS DE COMIDAS
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
# LEER INFORMACIÓN DE MISIONEROS Y COLONIAS (CON RESPALDO)
# ============================================
COLONIAS_DEFAULT = {
    "Apizaco I": "Santa Ursula, San Dionisio",
    "Apizaco II": "Centro",
    "Apizaco III": "Atexcatzingo, San jose tetel",
    "Apizaco Central": "Centro",
    "Tlaxco": "Tlaxco",
}

try:
    response_mis = supabase.table("misioneros_info").select("*").execute()
    df_mis = pd.DataFrame(response_mis.data)
    if df_mis.empty:
        df_mis = pd.DataFrame([
            {"companerismo": "Apizaco I", "misionero_1": "E. Montesinos", "misionero_2": "McAvoy", "colonia": COLONIAS_DEFAULT["Apizaco I"]},
            {"companerismo": "Apizaco II", "misionero_1": "E. Souto", "misionero_2": "Christensen y Day", "colonia": COLONIAS_DEFAULT["Apizaco II"]},
            {"companerismo": "Apizaco III", "misionero_1": "E. Menjivar", "misionero_2": "Reck", "colonia": COLONIAS_DEFAULT["Apizaco III"]},
            {"companerismo": "Apizaco Central", "misionero_1": "H. Howard", "misionero_2": "H. Muir", "colonia": COLONIAS_DEFAULT["Apizaco Central"]},
            {"companerismo": "Tlaxco", "misionero_1": "E. Perez", "misionero_2": "Lyman", "colonia": COLONIAS_DEFAULT["Tlaxco"]},
        ])
except Exception:
    df_mis = pd.DataFrame([
        {"companerismo": k, "misionero_1": "", "misionero_2": "", "colonia": v}
        for k, v in COLONIAS_DEFAULT.items()
    ])

mapeo_a_corto = {
    "Apizaco I": "Apizaco I",
    "Apizaco II": "Apizaco II",
    "Apizaco III": "Apizaco III",
    "Apizaco Central": "Apizaco Central",
    "Tlaxco": "Tlaxco",
}

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

def obtener_colonias(zona_corta):
    if df_mis.empty or "companerismo" not in df_mis.columns:
        return COLONIAS_DEFAULT.get(zona_corta, "")
    fila = df_mis[df_mis["companerismo"] == zona_corta]
    if fila.empty:
        return COLONIAS_DEFAULT.get(zona_corta, "")
    col = str(fila.iloc[0].get("colonia", "") or "").strip()
    return col if col else COLONIAS_DEFAULT.get(zona_corta, "")

meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_CORTOS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

hoy = datetime.date.today()

# ============================================
# HELPERS DE FECHAS Y DISPONIBILIDAD
# ============================================
def ultimo_dia_de(anio, mes):
    if mes == 12:
        return datetime.date(anio + 1, 1, 1) - timedelta(days=1)
    return datetime.date(anio, mes + 1, 1) - timedelta(days=1)

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

ocupadas_por_zona = {}
if not df_db.empty:
    for _, r in df_db.iterrows():
        fs = str(r["fecha"])[:10]
        ocupadas_por_zona.setdefault(str(r["companerismo"]), set()).add(fs)

def dias_libres_restantes(zona_corta, anio, mes):
    u = ultimo_dia_de(anio, mes)
    ocup = ocupadas_por_zona.get(zona_corta, set())
    libres = 0
    d = max(datetime.date(anio, mes, 1), hoy)
    while d <= u:
        if d.weekday() != 0 and str(d) not in ocup:
            libres += 1
        d += timedelta(days=1)
    return libres

def al_cambiar_zona():
    st.session_state["vista_manual"] = False
    st.session_state["view_ym"] = (hoy.year, hoy.month)

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
    n_dias = (ultimo_dia_de(anio, mes) - p_dia).days + 1
    return p_dia, n_dias, p_dia.weekday()

def generar_png_calendario(anio, mes, titulo, regs_por_fecha, fecha_hoy):
    p_dia, n_dias, offset = _datos_mes(anio, mes, regs_por_fecha)
    W = 1080
    pad = 20
    head_h = 95
    dayhead_h = 46
    cell_w = (W - 2 * pad) / 7

    tmp = Image.new("RGB", (10, 10))
    dtmp = ImageDraw.Draw(tmp)

    f_tit = _fuente(36, True)
    f_sub = _fuente(22)
    f_head = _fuente(21, True)
    f_day = _fuente(27, True)
    f_fam = _fuente(17)
    f_tel = _fuente(15)
    f_nota = _fuente(14)
    f_est = _fuente(15, True)
    f_leg = _fuente(18)

    def celdas_lineas(dia):
        f_act = datetime.date(anio, mes, dia)
        regs = regs_por_fecha.get(str(f_act), [])
        es_lunes = f_act.weekday() == 0
        es_hoy = f_act == fecha_hoy
        lineas = [(str(dia), f_day, "#1F2A37", 34)]
        if es_lunes:
            lineas.append(("DESCANSO", f_est, "#55677A", 22))
            estado = "lunes"
        elif regs:
            estado = "ocupado"
            for r in regs:
                for ln in _wrap_pix(dtmp, r["familia"], f_fam, cell_w - 16):
                    lineas.append((ln, f_fam, "#1F2A37", 21))
                for ln in _wrap_pix(dtmp, r["telefono"], f_tel, cell_w - 16):
                    lineas.append((ln, f_tel, "#55677A", 18))
                notas = str(r.get("notas", "") or "").strip()
                if notas:
                    for ln in _wrap_pix(dtmp, f"Nota: {notas}", f_nota, cell_w - 16):
                        lineas.append((ln, f_nota, "#55677A", 17))
        else:
            lineas.append(("LIBRE", f_est, "#2E6B34", 22))
            estado = "libre"
        return lineas, estado, es_hoy

    filas = math.ceil((offset + n_dias) / 7)
    filas_datos = []
    for row in range(filas):
        celdas = []
        alto_row = 120
        for col in range(7):
            dia = row * 7 + col - offset + 1
            if dia < 1 or dia > n_dias:
                celdas.append(None)
                continue
            lineas, estado, es_hoy = celdas_lineas(dia)
            alto = sum(a for _, _, _, a in lineas) + 16
            alto_row = max(alto_row, alto)
            celdas.append((lineas, estado, es_hoy))
        filas_datos.append((celdas, alto_row))

    H = pad + head_h + dayhead_h + sum(a for _, a in filas_datos) + 70
    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((pad, pad), titulo, font=f_tit, fill="#12395B")
    d.text((pad, pad + 48), "Comidas para misioneros - Apizaco y Tlaxco", font=f_sub, fill="#55677A")

    y0 = pad + head_h
    for i, nombre in enumerate(DIAS_CORTOS):
        x = pad + i * cell_w
        d.rectangle([x, y0, x + cell_w - 4, y0 + dayhead_h - 4], fill="#12395B")
        w_txt = d.textlength(nombre, font=f_head)
        d.text((x + (cell_w - 4 - w_txt) / 2, y0 + 10), nombre, font=f_head, fill="#FFFFFF")

    y = y0 + dayhead_h
    for celdas, alto_row in filas_datos:
        for col in range(7):
            info = celdas[col]
            if info is None:
                continue
            lineas, estado, es_hoy = info
            x = pad + col * cell_w
            if estado == "lunes":
                fill, border = "#EEF1F4", "#B9C2CC"
            elif estado == "ocupado":
                fill, border = "#E7F0FA", "#1668C3"
            else:
                fill, border = "#FFFFFF", "#D9E1EA"
            d.rectangle([x, y, x + cell_w - 4, y + alto_row - 6], fill=fill, outline=border, width=2)
            if es_hoy:
                d.rectangle([x, y, x + cell_w - 4, y + alto_row - 6], outline="#B98A2E", width=5)
            yy = y + 6
            for texto, font, color, alto in lineas:
                d.text((x + 8, yy), texto, font=font, fill=color)
                yy += alto
        y += alto_row

    ly = y + 12
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

    def agregar_wrap(lineas, texto):
        act = ""
        for p in str(texto).split(" "):
            prueba = f"{act} {p}".strip()
            if pdf.get_string_width(prueba) <= cw - 3 or not act:
                act = prueba
            else:
                lineas.append(act)
                act = p
        lineas.append(act)

    for row in range(filas):
        y0 = pdf.get_y()
        if y0 > 240:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(18, 57, 91)
            pdf.set_text_color(255, 255, 255)
            for nombre in DIAS_CORTOS:
                pdf.cell(cw, 7, nombre, border=1, align="C", fill=True)
            pdf.ln()
            pdf.set_text_color(31, 42, 55)
            y0 = pdf.get_y()

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
                    agregar_wrap(lineas, f'{r["familia"]} {r["telefono"]}')
                    notas = str(r.get("notas", "") or "").strip()
                    if notas:
                        agregar_wrap(lineas, f'Nota: {notas}')
            else:
                lineas.append("LIBRE")
                estado = "libre"
            max_lineas = max(max_lineas, len(lineas))
            celdas.append((lineas, estado, es_hoy))
        row_h = max(14, max_lineas * line_h + 3)
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
    pdf.cell(0, 6, "Libre: puede anotarse    |    Con familia: dia asignado    |    Lunes: descanso")
    return pdf.output()

# ============================================
# PANEL DE ADMINISTRACIÓN DE COLONIAS Y MISIONEROS
# ============================================
with st.expander("⚙️ Panel de Administración (Modificar Colonias y Misioneros)"):
    st.markdown("Actualiza la información de los compañerismos, misioneros y colonias directamente aquí:")
    
    df_editable = df_mis.copy()
    
    df_resultado = st.data_editor(
        df_editable,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "companerismo": st.column_config.TextColumn("Compañerismo", disabled=True),
            "misionero_1": st.column_config.TextColumn("Misionero 1"),
            "misionero_2": st.column_config.TextColumn("Misionero 2"),
            "colonia": st.column_config.TextColumn("Colonias / Sectores"),
            "actualizado_el": None
        },
        hide_index=True,
        key="editor_misioneros"
    )
    
    if st.button("Guardar cambios de administración", type="primary"):
        try:
            for _, row in df_resultado.iterrows():
                data_update = {
                    "misionero_1": row.get("misionero_1", ""),
                    "misionero_2": row.get("misionero_2", ""),
                    "colonia": row.get("colonia", "")
                }
                if "id" in row and pd.notna(row["id"]):
                    supabase.table("misioneros_info").update(data_update).eq("id", int(row["id"])).execute()
                else:
                    supabase.table("misioneros_info").update(data_update).eq("companerismo", row["companerismo"]).execute()

            st.success("¡Información actualizada correctamente! Recargando...")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar los cambios: {e}")

# ============================================
# TARJETA 1: SELECCIÓN
# ============================================
with st.container(border=True):
    st.markdown("##### 1. Elija su compañerismo")
    zona = st.pills(
        "Compañerismo",
        options=list(mapeo_a_corto.keys()),
        default=list(mapeo_a_corto.keys())[0],
        key="zona_pill",
        label_visibility="collapsed",
        on_change=al_cambiar_zona,
    )
    zona_corta = mapeo_a_corto.get(zona, zona)

    info_lineas = []
    colonias_txt = obtener_colonias(zona_corta)
    if colonias_txt:
        info_lineas.append(f"Colonias: {colonias_txt}")
    mis_txt = obtener_misioneros(zona_corta)
    if mis_txt:
        info_lineas.append(f"Misioneros asignados: {mis_txt}")
    for linea in info_lineas:
        st.markdown(f'<p class="muted">{html.escape(linea)}</p>', unsafe_allow_html=True)

    if "vista_manual" not in st.session_state:
        st.session_state.vista_manual = False
    if "view_ym" not in st.session_state:
        st.session_state.view_ym = (hoy.year, hoy.month)

    salto_info = None
    if not st.session_state.vista_manual:
        candidato = (hoy.year, hoy.month)
        for _ in range(MESES_ADELANTE_MAX):
            if dias_libres_restantes(zona_corta, candidato[0], candidato[1]) > 0:
                break
            sig = shift_month(candidato, 1)
            if sig == candidato:
                break
            candidato = sig
        if candidato != (hoy.year, hoy.month):
            st.session_state.view_ym = candidato
            salto_info = candidato

    st.markdown("##### 2. Mes que está viendo")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("Anterior", use_container_width=True, key="mes_prev"):
            st.session_state.view_ym = shift_month(st.session_state.view_ym, -1)
            st.session_state.vista_manual = True
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
            st.session_state.vista_manual = True
            st.rerun()

    if st.session_state.view_ym != (hoy.year, hoy.month):
        if st.button("Ir al mes actual", use_container_width=True, key="go_today"):
            st.session_state.view_ym = (hoy.year, hoy.month)
            st.session_state.vista_manual = True
            st.rerun()

    if salto_info:
        st.info(
            f"Como {meses_nombres[hoy.month]} {hoy.year} ya no tiene días libres, "
            f"le mostramos {meses_nombres[salto_info[1]]} {salto_info[0]} para que pueda anotarse. "
            f"Si solo quiere consultar {meses_nombres[hoy.month]}, use Anterior o Ir al mes actual."
        )
    elif st.session_state.view_ym == (hoy.year, hoy.month):
        libres_hoy = dias_libres_restantes(zona_corta, hoy.year, hoy.month)
        if 0 < libres_hoy <= UMBRAL_DIAS_LIBRES:
            sig = shift_month((hoy.year, hoy.month), 1)
            st.warning(
                f"Quedan {libres_hoy} día(s) libre(s) en {meses_nombres[hoy.month]}. "
                f"El mes siguiente ya está abierto para anotarse."
            )
            if st.button(f"Ver {meses_nombres[sig[1]]} {sig[0]}", use_container_width=True, key="ver_sig"):
                st.session_state.view_ym = sig
                st.session_state.vista_manual = True
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
ultimo_dia = ultimo_dia_de(anio_sel, mes_sel)
dias_mes = (ultimo_dia - primer_dia).days + 1
dia_semana_inicio = primer_dia.weekday()

# ============================================
# TARJETA 2: CALENDARIO + DESCARGAS (¡AHORA VISIBLE DE NUEVO!)
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
# TARJETA 3: REGISTRO Y MODIFICACIÓN
# ============================================
with st.container(border=True):
    tab_reg, tab_mod = st.tabs(["✍️ Anotar a mi familia", "✏️ Modificar o Cancelar mi registro"])

    # --- PESTAÑA 1: NUEVO REGISTRO ---
    with tab_reg:
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

    # --- PESTAÑA 2: MODIFICAR O CANCELAR REGISTRO ---
    with tab_mod:
        st.markdown("¿Te equivocaste en un dato o necesitas cambiar de fecha? Busca tu registro ingresando el **teléfono** con el que te registraste:")
        
        busqueda_tel = st.text_input("Introduce tu teléfono de registro", key="input_busqueda_tel")
        
        if busqueda_tel.strip():
            matches = []
            if not df_mes.empty:
                for _, r in df_mes.iterrows():
                    if busqueda_tel.strip() in str(r.get("telefono", "")):
                        matches.append(r)
            
            if not matches:
                st.warning("No se encontró ningún registro en este mes con ese número de teléfono.")
            else:
                st.success(f"¡Se encontró {len(matches)} registro(s) con este número!")
                for reg in matches:
                    reg_id = reg["id"]
                    f_actual = datetime.date.fromisoformat(str(reg["fecha"])[:10])
                    
                    with st.form(f"form_edit_{reg_id}"):
                        st.markdown(f"**Fecha actual:** {f_actual.strftime('%d/%m/%Y')}")
                        
                        nuevo_nombre = st.text_input("Nombre de la familia", value=str(reg["familia"]), key=f"nombre_{reg_id}")
                        nuevo_tel = st.text_input("Teléfono de WhatsApp", value=str(reg["telefono"]), key=f"tel_{reg_id}")
                        nueva_nota = st.text_area("Nota opcional", value=str(reg["notas"] if pd.notna(reg["notas"]) else ""), key=f"nota_{reg_id}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            guardar_cambios = st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True)
                        with col_btn2:
                            eliminar_reg = st.form_submit_button("🗑️ Cancelar Registro", use_container_width=True)
                        
                        if guardar_cambios:
                            try:
                                supabase.table("comidas_misioneros").update({
                                    "familia": nuevo_nombre.strip(),
                                    "telefono": nuevo_tel.strip(),
                                    "notas": nueva_nota.strip()
                                }).eq("id", reg_id).execute()
                                st.success("¡Registro actualizado con éxito!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al actualizar: {e}")
                                
                        if eliminar_reg:
                            try:
                                supabase.table("comidas_misioneros").delete().eq("id", reg_id).execute()
                                st.warning("El registro ha sido eliminado del calendario.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al eliminar: {e}")

# ============================================
# TARJETA 4: LISTA / AGENDA (Móvil y Escritorio)
# ============================================
with st.container(border=True):
    st.markdown(f"### Familias anotadas en {meses_nombres[mes_sel]}")
    if df_mes.empty:
        st.markdown('<p class="muted">Aún no hay familias anotadas este mes en este compañerismo.</p>', unsafe_allow_html=True)

    # Vista móvil resumida
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
        html_agenda += f'<div class="agenda-dia">{dia} {DIAS_CORTOS[f_act.weekday()]}</div>'
        html_agenda += '<div class="agenda-cuerpo">'
        if es_lunes:
            html_agenda += '<div class="agenda-estado" style="color:#55677A;">DESCANSO</div>'
        elif regs:
            for r in regs:
                tel_clean = r["telefono"].replace(" ", "").replace("-", "")
                html_agenda += f'<div class="agenda-fam">🍽️ {html.escape(r["familia"])}</div>'
                html_agenda += f'<div><a href="https://wa.me/{tel_clean}" target="_blank">📱 {html.escape(r["telefono"])}</a></div>'
                if r["notas"]:
                    html_agenda += f'<div style="font-size:0.8rem; color:#55677A;">Nota: {html.escape(r["notas"])}</div>'
        else:
            html_agenda += '<div class="agenda-estado" style="color:#2E6B34;">LIBRE</div>'
        html_agenda += '</div></div>'
    html_agenda += '</div>'
    st.markdown(html_agenda, unsafe_allow_html=True)

    # Vista escritorio detallada
    st.markdown('<div class="solo-escritorio" style="margin-top:1rem;">', unsafe_allow_html=True)
    if not df_mes.empty:
        for _, row in df_mes.iterrows():
            f_dt = datetime.date.fromisoformat(str(row["fecha"])[:10])
            f_fmt = f_dt.strftime("%d/%m/%Y")
            dia_sem = DIAS_SEMANA[f_dt.weekday()]
            tel_clean = str(row["telefono"]).replace(" ", "").replace("-", "")
            
            nota_html = f" · <em>Nota: {html.escape(str(row['notas']))}</em>" if row.get("notas") else ""
            st.markdown(
                f"""
                <div class="reg-row">
                    <span class="reg-fecha">{f_fmt} ({dia_sem})</span><br>
                    <span class="reg-fam">🍽️ {html.escape(str(row['familia']))}</span> · 
                    <a href="https://wa.me/{tel_clean}" target="_blank">📱 {html.escape(str(row['telefono']))}</a>
                    {nota_html}
                </div>
                """,
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)
