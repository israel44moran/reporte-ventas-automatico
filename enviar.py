"""
Envío del reporte por correo electrónico vía SMTP.
Funciona con Gmail (con contraseña de aplicación), Outlook, Yahoo y
cualquier servidor SMTP estándar.
"""

import smtplib
from email.message import EmailMessage
from pathlib import Path
import mimetypes


def enviar_reporte(
    pdf_path,
    destinatarios,
    asunto,
    cuerpo,
    smtp_host,
    smtp_port,
    smtp_user,
    smtp_password,
    remitente=None,
    usar_tls=True,
):
    """
    Envía un PDF como adjunto.

    Parámetros
    ----------
    pdf_path : str | Path
        Ruta al PDF a adjuntar.
    destinatarios : list[str]
        Lista de correos de destino.
    asunto : str
        Asunto del correo.
    cuerpo : str
        Cuerpo del mensaje en texto plano.
    smtp_host, smtp_port : str, int
        Servidor SMTP. Ejemplo Gmail: 'smtp.gmail.com', 587.
    smtp_user, smtp_password : str
        Credenciales (en Gmail debe ser una contraseña de aplicación).
    remitente : str
        Dirección visible. Si es None se usa smtp_user.
    usar_tls : bool
        True para STARTTLS (587), False para SSL (465) o sin cifrado.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"No se encontró el PDF: {pdf_path}")

    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = remitente or smtp_user
    msg['To'] = ", ".join(destinatarios)
    msg.set_content(cuerpo)

    # Adjuntar PDF
    mime_type, _ = mimetypes.guess_type(pdf_path.name)
    if mime_type is None:
        mime_type = "application/pdf"
    main_type, sub_type = mime_type.split("/", 1)

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype=main_type,
            subtype=sub_type,
            filename=pdf_path.name,
        )

    # Conexión SMTP
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            if usar_tls:
                server.starttls()
                server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    return True
