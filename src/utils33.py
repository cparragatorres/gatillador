import logging
import re
import html

def setup_logging(log_file="whatsapp_message_sender.log", log_to_console=False):
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
    logging.info("Logging setup completed.")

def validate_phone_number(phone_number):
    """
    Valida que el número de teléfono esté en formato internacional (+countrycode).

    Args:
        phone_number (str): Número de teléfono a validar.

    Returns:
        bool: True si el número es válido, False de lo contrario.
    """
    pattern = r'^\+\d{1,15}$'
    if not re.match(pattern, phone_number):
        logging.warning(f"Invalid phone number format: {phone_number}. Expected format: +1234567890.")
        return False
    logging.info(f"Valid phone number: {phone_number}")
    return True

def format_message(header, body, footer=None):
    """
    Formatea un mensaje en el estilo deseado.

    Args:
        header (str): Encabezado del mensaje.
        body (str): Cuerpo principal del mensaje.
        recommendations (list): Lista de recomendaciones.
        footer (str): Pie de página del mensaje.

    Returns:
        str: Mensaje formateado con saltos de línea codificados.
    """
    formatted_message = html.unescape(header + "%0A%0A")
    formatted_message += html.unescape(body + "%0A%0A")


    if footer:
        formatted_message += html.unescape(footer)

    return formatted_message
