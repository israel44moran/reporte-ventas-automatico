"""
Orquestador: genera el reporte de la semana pasada y lo envía por correo.
Ejecuta este script una sola vez (o desde el programador).
"""

from datetime import datetime
import sys
import traceback

from reporte import generar_reporte_semanal
from enviar import enviar_reporte

try:
    import config
except ImportError:
    print("ERROR: no existe 'config.py'.")
    print("Copia 'config.example.py' a 'config.py' y rellena tus datos.")
    sys.exit(1)


def ejecutar():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando reporte semanal")

    # 1. Generar PDF
    try:
        pdf = generar_reporte_semanal(
            archivo_excel=config.ARCHIVO_VENTAS,
            salida=config.PDF_SALIDA,
            semana_offset=-1,   # semana pasada
        )
        print(f"  [OK] PDF generado: {pdf}")
    except Exception as e:
        print(f"  [ERROR] No se pudo generar el PDF: {e}")
        traceback.print_exc()
        return False

    # 2. Enviar correo
    try:
        enviar_reporte(
            pdf_path=pdf,
            destinatarios=config.DESTINATARIOS,
            asunto=config.ASUNTO,
            cuerpo=config.CUERPO,
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            smtp_user=config.SMTP_USER,
            smtp_password=config.SMTP_PASSWORD,
            remitente=config.REMITENTE,
            usar_tls=config.USAR_TLS,
        )
        print(f"  [OK] Correo enviado a: {', '.join(config.DESTINATARIOS)}")
        return True
    except Exception as e:
        print(f"  [ERROR] Fallo el envio del correo: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    exito = ejecutar()
    sys.exit(0 if exito else 1)
