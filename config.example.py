"""
Plantilla de configuración. Copia este archivo a 'config.py' y rellena
con tus datos reales. 'config.py' está en el .gitignore — nunca subas
tus credenciales al repositorio.
"""

# ============================================================
# ARCHIVO DE DATOS
# ============================================================
ARCHIVO_VENTAS = "ventas.xlsx"      # Excel o CSV con las ventas
PDF_SALIDA     = "reporte_semanal.pdf"

# ============================================================
# CORREO — SMTP
# ============================================================
# Gmail: smtp.gmail.com / 587 (STARTTLS) — usar contraseña de aplicación
# Outlook: smtp-mail.outlook.com / 587
# Yahoo: smtp.mail.yahoo.com / 587
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SMTP_USER     = "tu_correo@gmail.com"
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"   # contraseña de aplicación de 16 caracteres
USAR_TLS      = True

REMITENTE     = "Reporte Automatico <tu_correo@gmail.com>"
DESTINATARIOS = [
    "dueno_negocio@ejemplo.com",
    "contador@ejemplo.com",
]

ASUNTO  = "Reporte semanal de ventas"
CUERPO  = (
    "Hola,\n\n"
    "Adjunto encontraras el reporte de ventas de la semana pasada, "
    "generado automaticamente.\n\n"
    "Incluye:\n"
    "  - Indicadores principales (ventas, transacciones, ticket promedio)\n"
    "  - Comparativa contra la semana anterior\n"
    "  - Grafica diaria\n"
    "  - Top 10 productos\n"
    "  - Distribucion por categoria\n\n"
    "Saludos,\n"
    "Sistema de reportes automaticos"
)

# ============================================================
# PROGRAMACION
# ============================================================
DIA_ENVIO  = "monday"   # monday, tuesday, ...
HORA_ENVIO = "08:00"    # formato 24h
