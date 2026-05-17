"""
Generador del reporte semanal en PDF.
Lee un Excel de ventas, calcula KPIs, genera gráficas con matplotlib y
arma un PDF con ReportLab.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

# ============================================================
# PALETA — coherente con el resto del portafolio
# ============================================================
INK    = HexColor("#0E1218")
CREAM  = HexColor("#F2EDE3")
COOL   = HexColor("#9AA3B5")
MUTED  = HexColor("#5A6478")
BORDER = HexColor("#2A3140")
AMBER  = HexColor("#D4A574")
SURFACE = HexColor("#171C24")

# Para matplotlib (necesita strings)
COLOR_AMBER = "#D4A574"
COLOR_CREAM = "#F2EDE3"
COLOR_INK   = "#0E1218"
COLOR_COOL  = "#9AA3B5"
COLOR_BORD  = "#2A3140"

DIAS_ES = {
    'Monday': 'Lun', 'Tuesday': 'Mar', 'Wednesday': 'Mie',
    'Thursday': 'Jue', 'Friday': 'Vie', 'Saturday': 'Sab', 'Sunday': 'Dom'
}
MESES_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
            'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


# ============================================================
# CARGA DE DATOS
# ============================================================
def cargar_datos(archivo):
    if archivo.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(archivo)
    else:
        df = pd.read_csv(archivo)

    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])

    if 'total' not in df.columns and 'precio_unitario' in df.columns and 'cantidad' in df.columns:
        df['total'] = df['precio_unitario'] * df['cantidad']
    if 'cantidad' not in df.columns:
        df['cantidad'] = 1
    if 'id_venta' not in df.columns:
        df['id_venta'] = range(1, len(df) + 1)

    return df


def filtrar_semana(df, semana_offset=0):
    """
    semana_offset = 0 -> semana en curso
    semana_offset = -1 -> semana pasada (la más común para el reporte de los lunes)
    """
    hoy = datetime.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=semana_offset)
    fin_semana = inicio_semana + timedelta(days=6)
    mask = (df['fecha'].dt.date >= inicio_semana) & (df['fecha'].dt.date <= fin_semana)
    return df[mask], inicio_semana, fin_semana


# ============================================================
# GRÁFICAS
# ============================================================
def grafica_diaria(df_semana, ruta):
    plt.figure(figsize=(7, 2.6), facecolor=COLOR_INK)
    ax = plt.gca()
    ax.set_facecolor(COLOR_INK)

    ventas_dia = df_semana.groupby(df_semana['fecha'].dt.date)['total'].sum()
    fechas = sorted(ventas_dia.index)
    valores = [ventas_dia.get(f, 0) for f in fechas]
    etiquetas = [DIAS_ES.get(pd.Timestamp(f).day_name(), '') + f"\n{f.day}" for f in fechas]

    bars = ax.bar(range(len(fechas)), valores, color=COLOR_AMBER, width=0.55,
                  edgecolor='none')

    for bar, val in zip(bars, valores):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(valores) * 0.02,
                    f"${val:,.0f}", ha='center', va='bottom',
                    color=COLOR_CREAM, fontsize=7, fontfamily='DejaVu Sans')

    ax.set_xticks(range(len(fechas)))
    ax.set_xticklabels(etiquetas, color=COLOR_COOL, fontsize=8)
    ax.tick_params(axis='y', colors=COLOR_COOL, labelsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORD)
    ax.spines['bottom'].set_color(COLOR_BORD)
    ax.yaxis.grid(True, color=COLOR_BORD, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(valores) * 1.18 if max(valores) > 0 else 1)

    plt.tight_layout()
    plt.savefig(ruta, dpi=150, facecolor=COLOR_INK, bbox_inches='tight')
    plt.close()


def grafica_categorias(df_semana, ruta):
    if 'categoria' not in df_semana.columns:
        return False

    cat = df_semana.groupby('categoria')['total'].sum().sort_values(ascending=True)

    plt.figure(figsize=(7, 2.6), facecolor=COLOR_INK)
    ax = plt.gca()
    ax.set_facecolor(COLOR_INK)

    bars = ax.barh(cat.index, cat.values, color=COLOR_AMBER, edgecolor='none', height=0.6)
    for bar, val in zip(bars, cat.values):
        ax.text(bar.get_width() + max(cat.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va='center', ha='left',
                color=COLOR_CREAM, fontsize=8)

    ax.tick_params(axis='y', colors=COLOR_CREAM, labelsize=9)
    ax.tick_params(axis='x', colors=COLOR_COOL, labelsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORD)
    ax.spines['bottom'].set_color(COLOR_BORD)
    ax.xaxis.grid(True, color=COLOR_BORD, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_xlim(0, max(cat.values) * 1.18 if max(cat.values) > 0 else 1)

    plt.tight_layout()
    plt.savefig(ruta, dpi=150, facecolor=COLOR_INK, bbox_inches='tight')
    plt.close()
    return True


# ============================================================
# CONSTRUCCIÓN DEL PDF
# ============================================================
def construir_pdf(df_semana, inicio, fin, ruta_pdf, comparativa=None):
    doc = SimpleDocTemplate(
        ruta_pdf, pagesize=LETTER,
        leftMargin=1.6 * cm, rightMargin=1.6 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm
    )

    elementos = []

    # ---- Estilos ----
    estilo_eyebrow = ParagraphStyle(
        'eyebrow', fontName='Helvetica-Bold', fontSize=8,
        textColor=AMBER, alignment=TA_LEFT, leading=10,
        spaceAfter=4
    )
    estilo_titulo = ParagraphStyle(
        'titulo', fontName='Helvetica', fontSize=24,
        textColor=CREAM, alignment=TA_LEFT, leading=28,
        spaceAfter=4
    )
    estilo_deck = ParagraphStyle(
        'deck', fontName='Helvetica', fontSize=10,
        textColor=COOL, alignment=TA_LEFT, leading=14,
        spaceAfter=14
    )
    estilo_section = ParagraphStyle(
        'section', fontName='Helvetica-Bold', fontSize=8,
        textColor=AMBER, alignment=TA_LEFT, leading=10,
        spaceBefore=14, spaceAfter=6
    )
    estilo_section_title = ParagraphStyle(
        'sectionTitle', fontName='Helvetica', fontSize=14,
        textColor=CREAM, alignment=TA_LEFT, leading=18,
        spaceAfter=8
    )
    estilo_footer = ParagraphStyle(
        'footer', fontName='Helvetica', fontSize=7,
        textColor=MUTED, alignment=TA_CENTER, leading=9
    )

    # ---- Encabezado ----
    fmt_fecha = lambda d: f"{d.day:02d} {MESES_ES[d.month-1]} {d.year}"
    elementos.append(Paragraph("— REPORTE SEMANAL DE VENTAS", estilo_eyebrow))
    elementos.append(Paragraph(f"Resumen del {fmt_fecha(inicio)} al {fmt_fecha(fin)}", estilo_titulo))
    elementos.append(Paragraph(
        f"Generado automáticamente el {fmt_fecha(datetime.now())} a las {datetime.now().strftime('%H:%M')} hrs.",
        estilo_deck
    ))

    # ---- KPIs ----
    if len(df_semana) == 0:
        elementos.append(Paragraph("Sin operaciones registradas en este periodo.", estilo_deck))
        doc.build(elementos)
        return

    total = df_semana['total'].sum()
    transacciones = df_semana['id_venta'].nunique()
    ticket_prom = total / transacciones if transacciones else 0
    unidades = int(df_semana['cantidad'].sum())

    # Variación contra semana anterior
    delta_txt = "—"
    if comparativa is not None and len(comparativa) > 0:
        total_prev = comparativa['total'].sum()
        if total_prev > 0:
            delta = (total - total_prev) / total_prev * 100
            signo = "+" if delta >= 0 else ""
            delta_txt = f"{signo}{delta:.1f}% vs semana anterior"

    kpi_data = [
        [
            Paragraph("VENTAS TOTALES", ParagraphStyle('k1', fontName='Helvetica-Bold', fontSize=7, textColor=MUTED, leading=9)),
            Paragraph("TRANSACCIONES", ParagraphStyle('k2', fontName='Helvetica-Bold', fontSize=7, textColor=MUTED, leading=9)),
            Paragraph("TICKET PROMEDIO", ParagraphStyle('k3', fontName='Helvetica-Bold', fontSize=7, textColor=MUTED, leading=9)),
            Paragraph("UNIDADES", ParagraphStyle('k4', fontName='Helvetica-Bold', fontSize=7, textColor=MUTED, leading=9)),
        ],
        [
            Paragraph(f"${total:,.0f}", ParagraphStyle('v1', fontName='Helvetica', fontSize=18, textColor=CREAM, leading=22)),
            Paragraph(f"{transacciones:,}", ParagraphStyle('v2', fontName='Helvetica', fontSize=18, textColor=CREAM, leading=22)),
            Paragraph(f"${ticket_prom:,.0f}", ParagraphStyle('v3', fontName='Helvetica', fontSize=18, textColor=CREAM, leading=22)),
            Paragraph(f"{unidades:,}", ParagraphStyle('v4', fontName='Helvetica', fontSize=18, textColor=CREAM, leading=22)),
        ],
        [
            Paragraph(delta_txt, ParagraphStyle('s1', fontName='Helvetica', fontSize=7, textColor=AMBER, leading=9)),
            Paragraph("Tickets emitidos", ParagraphStyle('s2', fontName='Helvetica', fontSize=7, textColor=MUTED, leading=9)),
            Paragraph("Por transacción", ParagraphStyle('s3', fontName='Helvetica', fontSize=7, textColor=MUTED, leading=9)),
            Paragraph("Productos vendidos", ParagraphStyle('s4', fontName='Helvetica', fontSize=7, textColor=MUTED, leading=9)),
        ],
    ]

    tabla_kpi = Table(kpi_data, colWidths=[4.4 * cm] * 4)
    tabla_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), INK),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, BORDER),
        ('LINEBELOW', (0, 2), (-1, 2), 0.5, BORDER),
        ('LINEAFTER', (0, 0), (-2, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(tabla_kpi)

    # ---- Gráfica diaria ----
    elementos.append(Spacer(1, 16))
    elementos.append(Paragraph("— GRAFICA 01 / DIARIO", estilo_section))
    elementos.append(Paragraph("Ventas por día de la semana", estilo_section_title))

    chart_buffer = BytesIO()
    grafica_diaria(df_semana, chart_buffer)
    chart_buffer.seek(0)
    elementos.append(Image(chart_buffer, width=18 * cm, height=6.5 * cm))

    # ---- Top productos ----
    elementos.append(Spacer(1, 16))
    elementos.append(Paragraph("— RANKING / PRODUCTOS", estilo_section))
    elementos.append(Paragraph("Top 10 productos por ingreso", estilo_section_title))

    top = df_semana.groupby('producto').agg(
        ingreso=('total', 'sum'),
        unidades=('cantidad', 'sum')
    ).sort_values('ingreso', ascending=False).head(10).reset_index()

    encabezado = ['#', 'Producto', 'Unidades', 'Ingreso']
    filas = [encabezado]
    for i, r in top.iterrows():
        filas.append([
            f"{i + 1:02d}",
            r['producto'],
            f"{int(r['unidades'])}",
            f"${r['ingreso']:,.0f}"
        ])

    tabla_top = Table(filas, colWidths=[1.2 * cm, 9 * cm, 3 * cm, 4.4 * cm])
    tabla_top.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SURFACE),
        ('TEXTCOLOR', (0, 0), (-1, 0), AMBER),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('TEXTCOLOR', (0, 1), (-1, -1), CREAM),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, -1), INK),
        ('TEXTCOLOR', (0, 1), (0, -1), MUTED),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, BORDER),
        ('LINEBELOW', (0, 1), (-1, -1), 0.25, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    elementos.append(tabla_top)

    # ---- Categorías ----
    if 'categoria' in df_semana.columns:
        elementos.append(Spacer(1, 16))
        elementos.append(Paragraph("— GRAFICA 02 / CATEGORIAS", estilo_section))
        elementos.append(Paragraph("Distribución por categoría", estilo_section_title))

        cat_buffer = BytesIO()
        if grafica_categorias(df_semana, cat_buffer):
            cat_buffer.seek(0)
            elementos.append(Image(cat_buffer, width=18 * cm, height=6.5 * cm))

    # ---- Pie ----
    elementos.append(Spacer(1, 28))
    elementos.append(Paragraph(
        "REPORTE GENERADO AUTOMATICAMENTE   ·   PYTHON / REPORTLAB / MATPLOTLIB",
        estilo_footer
    ))

    # ---- Construcción con fondo oscuro ----
    def fondo(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(INK)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(elementos, onFirstPage=fondo, onLaterPages=fondo)


# ============================================================
# ORQUESTADOR
# ============================================================
def generar_reporte_semanal(archivo_excel="ventas.xlsx",
                             salida="reporte_semanal.pdf",
                             semana_offset=-1):
    """
    Genera el reporte de la semana pasada (semana_offset=-1) por defecto.
    Devuelve la ruta del PDF generado.
    """
    df = cargar_datos(archivo_excel)
    df_semana, inicio, fin = filtrar_semana(df, semana_offset=semana_offset)
    df_prev, _, _ = filtrar_semana(df, semana_offset=semana_offset - 1)

    construir_pdf(df_semana, inicio, fin, salida, comparativa=df_prev)
    return salida


if __name__ == "__main__":
    pdf = generar_reporte_semanal()
    print(f"[OK] Reporte generado: {pdf}")
