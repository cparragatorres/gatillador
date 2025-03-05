import logging
import re
import html

def configurar_logs(log_file="logs/whatsapp_message_sender.log", log_to_console=False):
    """
    Configura el sistema de logging para registrar en un archivo y opcionalmente en consola.

    Args:
        log_file (str): Nombre del archivo donde se registrarán los logs.
        log_to_console (bool): Si es True, también muestra los logs en la consola.
    """
    handlers = [logging.FileHandler(log_file)]
    if log_to_console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    logging.info("Sistema de logs configurado correctamente.")

def validar_numero(numero):
    """
    Valida que el número de teléfono esté en formato internacional (+countrycode).

    Args:
        numero (str): Número de teléfono a validar.

    Returns:
        bool: True si el número es válido, False de lo contrario.
    """
    patron = r'^\+\d{1,15}$'
    if not re.match(patron, numero):
        logging.warning(f"Número inválido: {numero}. Formato esperado: +1234567890.")
        return False
    logging.info(f"Número válido: {numero}")
    return True

def formatear_mensaje(encabezado, cuerpo, pie=None):
    """
    Formatea un mensaje con saltos de línea adecuados para WhatsApp.

    Args:
        encabezado (str): Encabezado del mensaje.
        cuerpo (str): Cuerpo principal del mensaje.
        pie (str, opcional): Pie de página del mensaje.

    Returns:
        str: Mensaje formateado con saltos de línea codificados.
    """
    mensaje_formateado = html.unescape(encabezado + "%0A%0A")
    mensaje_formateado += html.unescape(cuerpo + "%0A%0A")

    if pie:
        mensaje_formateado += html.unescape(pie)

    return mensaje_formateado
