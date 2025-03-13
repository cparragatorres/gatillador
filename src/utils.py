import logging
import re
import html
import pandas as pd
import unicodedata

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

def cargar_excel(ruta):
    """
    Carga un archivo Excel con pandas y maneja errores de manera eficiente.

    Args:
        ruta (str): Ruta del archivo Excel.

    Returns:
        pd.DataFrame: DataFrame con los datos si se carga correctamente, None si hay error.
    """
    try:
        df = pd.read_excel(ruta, dtype=str)
        print(f"Datos cargados exitosamente: {ruta}")
        return df
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta}")
    except Exception as e:
        print(f"Error al leer el archivo {ruta}: {str(e)}")
    return None



def normalizar_nombres_columnas(df):
    """
    Normaliza los nombres de las columnas:
    - Convierte a minúsculas.
    - Elimina espacios al inicio y al final.
    - Reemplaza tildes por letras sin acento.
    - Reemplaza caracteres especiales por un guion bajo.
    """
    def limpiar(texto):
        texto = texto.strip().lower()  # Convertir a minúsculas y quitar espacios
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')  # Quitar tildes
        texto = re.sub(r'[^a-z0-9_]', '_', texto)  # Reemplazar caracteres especiales por "_"
        return texto

    df.columns = [limpiar(col) for col in df.columns]
    return df

from datetime import datetime
from src.utils import formatear_mensaje

def generar_mensaje_alerta(
    telefono,
    representante_estacion,
    cami_nombre,
    cami_sede,
    estado,
    estacion,
    ultima_fecha,
    hora_inferior,
    hora_superior,
    nivel_cloro,
    localidad=None,
    departamento=None
    ):

    """
    Genera el mensaje de alerta según el estado y la hora de corte.

    Args:
        telefono (str): Número de teléfono al que se enviará el mensaje.
        estado (str): Estado de la estación (inadecuado, inactivo, etc.).
        estacion (str): Nombre de la estación.
        ultima_fecha (str): Fecha del último registro.
        hora_inferior (str): Hora de inicio del monitoreo.
        hora_superior (str): Hora de fin del monitoreo.
        nivel_cloro (str): Nivel de cloro detectado.
        localidad (str, opcional): Localidad de la estación.
        departamento (str, opcional): Departamento de la estación.

    Returns:
        str: Mensaje formateado listo para ser enviado por WhatsApp.s
    """

    # Si no se proporciona una fecha, usar la actual
    if not ultima_fecha:
        ultima_fecha = datetime.now().strftime("%d/%m/%Y")

    # Ubicación opcional en el mensaje
    ubicacion = f" ubicada en *{localidad}* - *{departamento}*," if localidad and departamento else ""

    # Generar mensaje según el estado
    if estado == "inadecuado":
        header = "🚨¡ALERTA: NIVEL BAJO DE CLORO!🚨"
        body = (
            f"Buen dia Dr. {representante_estacion}, soy {cami_nombre} de CAMI YAKU {cami_sede} 😊"
            "%0A%0A"
            f"Hoy, {ultima_fecha} se ha detectado un *nivel de cloro* promedio de *{nivel_cloro}* mg/L "
            f"indicando que está por debajo del mínimo requerido (0.5 mg/L) en la estación *{estacion}*{ubicacion} "
            f"entre las *{hora_inferior}* y *{hora_superior}* horas."
            "%0A%0A"
            "⚠️ *Importante:* Es necesario corregir el nivel de cloro para garantizar que el agua sea segura para el consumo."
        )
        footer = "✅ Acción inmediata: *Realizar* el proceso de cloración ahora, responder las acciones que tomarán y *reportar por este medio* cuando se esté corregido."

    elif estado == "inactivo":
        header = "🚨*¡ALERTA: INACTIVIDAD DE ESTACIÓN!* 🚨"
        body = (
            f"Buen dia Dr. {representante_estacion}, soy {cami_nombre} de CAMI YAKU {cami_sede} 😊"
            "%0A%0A"
            f"Hoy, {ultima_fecha} la estación *{estacion}*{ubicacion} se detectó *inactiva* "
            f"entre las *{hora_inferior}* y *{hora_superior}* horas, estando fuera de su horario de operación programada.\n\n"
            "%0A%0A"
            "⚠️ *Importante:* Es necesario activar la estación y cuidar del nivel de cloro para garantizar que el agua sea segura para el consumo."
        )
        footer = "✅ Acción inmediata: *Realizar* la activación de la estación e indicar el nivel de cloro y *reportar por este medio* cuando se esté corregido."

    else:
        return None  # Si el estado no es relevante, no genera mensaje

    return formatear_mensaje(header, body, footer)
