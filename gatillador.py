# %%
import pandas as pd
import sys
import os

# Agregar la ruta de la carpeta src al path de Python
src_path = os.path.join(os.getcwd(), "src")
if src_path not in sys.path:
    sys.path.append(src_path)
    
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
from utils33 import setup_logging, format_message, validate_phone_number
from sender9a import EnhancedWhatsAppMessageSender
from openpyxl import load_workbook

# Configurar el sistema de logging para el notebook
setup_logging(log_file="whatsapp_message_sender.log", log_to_console=True)


# %%
def corregir_excel(nombre_archivo):
    """
    Carga un archivo Excel con OpenPyxl y lo guarda nuevamente
    para corregir el problema del warning de estilos.
    """
    try:
        wb = load_workbook(nombre_archivo)
        nombre_corregido = nombre_archivo.replace(".xlsx", "_fixed.xlsx")
        wb.save(nombre_corregido)
        print(f"Archivo corregido guardado como: {nombre_corregido}")
        return nombre_corregido
    except Exception as e:
        print(f"Error al corregir el archivo {nombre_archivo}: {str(e)}")
        return None

# %%
# Ruta base del proyecto
base_path = os.getcwd()

# Nombres de los archivos originales
archivo1 = os.path.join(base_path, "directorio.xlsx")
archivo2 = os.path.join(base_path, "data.xlsx")

# Leemos el archivo Excel
try:
    df_directorio = pd.read_excel(archivo1, dtype=str)
    print("Datos cargados exitosamente.\n")
    # Leer los archivos corregidos
    df1 = pd.read_excel(archivo1, dtype=str)
    print(df_directorio.head())
except FileNotFoundError:
    print(f"El archivo no se encuentra en la ruta: {archivo1}")
except Exception as e:
    print(f"Error al leer el archivo Excel: {str(e)}")
    
# Leemos el archivo Excel
try:
    df_data_estaciones = pd.read_excel(archivo2, dtype=str)
    print("Datos cargados exitosamente.\n")
    # Leer los archivos corregidos
    df2 = pd.read_excel(archivo2, dtype=str)
    print(df_data_estaciones.head())
except FileNotFoundError:
    print(f"El archivo no se encuentra en la ruta: {archivo2}")
except Exception as e:
    print(f"Error al leer el archivo Excel: {str(e)}")

# %%
def normalizar_columnas(df):
    """
    Normaliza los nombres de las columnas y sus valores:
    - Convierte todas las columnas a minúsculas
    - Elimina espacios antes y después del nombre de las columnas
    - Asegura que la columna 'estacion' esté en minúsculas en la cabecera
    - Mantiene los valores de 'estacion' en mayúsculas
    """
    df.columns = df.columns.str.strip().str.lower()  # Normaliza los nombres de las columnas
    df = df.rename(columns={"estación": "estacion"})  # Asegurar que 'Estación' se llame 'estacion'

    # Mantener los valores de la columna 'estacion' en mayúsculas
    if "estacion" in df.columns:
        df["estacion"] = df["estacion"].str.strip().str.upper()  # Convertir valores a mayúsculas

    return df

df1 = normalizar_columnas(df1)
df2 = normalizar_columnas(df2)

# Mostrar las columnas para verificar
print("Columnas de df1:", df1.columns)
print("Columnas de df2:", df2.columns)

# %%
# Unir los dos DataFrames en un solo tablero usando 'Estacion' como clave
df_unido = pd.merge(df1, df2, on="estacion", how="inner")

# Mostrar las primeras filas del DataFrame unido
print("DataFrame unido:")
print(df_unido)


# %%
# Convertir la columna 'promedio de cloro (mg/l)' a float y redondear a 2 decimales
# df_unido["promedio de cloro (mg/l)"] = df_unido["promedio de cloro (mg/l)"].astype(float).round(2)

# Reemplazar valores vacios con NaN
df_unido["promedio de cloro (mg/l)"] = df_unido["promedio de cloro (mg/l)"].replace("", pd.NA)

# Convertir la columna 'promedio de cloro (mg/l)' a float
df_unido["promedio de cloro (mg/l)"] = pd.to_numeric(df_unido["promedio de cloro (mg/l)"], errors="coerce")

# Cambiar el estado a 'Inadecuado' SOLO si el estado actual es 'Activo' y el promedio de cloro es menor a 0.5
df_unido.loc[
    ((df_unido["estado"] == "Activo") & (df_unido["promedio de cloro (mg/l)"] < 0.5)),
    "estado"
] = "Inadecuado"

# Aplicar la conversión con redondeo dinámico
df_unido["promedio de cloro (mg/l)"] = df_unido["promedio de cloro (mg/l)"].apply(
    lambda x: "0" if x == 0 else str(round(x, 6)).rstrip("0").rstrip(".") if pd.notna(x) else ""
)

# Mostrar DataFrame
print("DataFrame con estado corregido:")
print(df_unido)


# %%
# Guardamos el DataFrame filtrado en un archivo Excel
df_unido.to_excel("data_filtrada.xlsx", index=False)

# %%
def filtrar_estaciones_inadecuadas_inactivas(df):
    """
    Devuelve un DataFrame con solo las filas 
    donde Estado sea 'Inadecuado' o 'Inactivo'.
    """
    
    # Limpiar y normalizar la columna 'estado'
    df["estado"] = df["estado"].fillna("").str.strip().str.lower()
        
    # Lista de estados a filtrar (normalizados en minúsculas)
    estados_filtrados = ["inadecuado", "inactivo"]
    
    # Filtrar las filas donde 'estado' sea "mal" o "inactivo"
    df_filtrado = df[df["estado"].isin(estados_filtrados)].copy()
    
    return df_filtrado

# Aplicamos la función de filtrado
df_filtrado = filtrar_estaciones_inadecuadas_inactivas(df_unido)

# Mostramos el resultado
print("Estaciones filtradas (Mal / Inactivo):\n")
print(df_filtrado)


# %%
def generar_mensaje_alerta(telefono, estado, estacion, ultima_fecha_registrada, hora_inferior, hora_superior, nivel_cloro):
    """
    Genera el mensaje de alerta según el estado y la hora de corte.
    """
    header = "Previo cordial saludo,"
    footer = "Este es un mensaje de prueba, por favor no responder."
    
    if estado == "inadecuado":
        body = (
            f"Se comunica que hoy {ultima_fecha_registrada}, la estación {estacion} registra un nivel de cloro inadecuado, "
            f"con un promedio de {nivel_cloro} mg/L (menor a 0,5 mg/L) entre las {hora_inferior} y {hora_superior} horas."
        )
        # recommendations = ["Revisar el sistema de dosificación de cloro", "Enviar equipo técnico a la estación"]
    elif estado == "inactivo":
        body = (
            f"Se comunica que hoy {ultima_fecha_registrada}, la estación {estacion} se encuentra en estado {estado}, "
            f"entre las {hora_inferior} y {hora_superior} horas."
        )
        # recommendations = ["Activar el monitoreo remoto", "Contactar al equipo de mantenimiento"]
    else:
        return None

    return format_message(header, body, footer)

# Generar mensajes
mensajes_de_prueba = []
for idx, row in df_filtrado.iterrows():
    msg = generar_mensaje_alerta(
        telefono=row["telefono"],
        estado=row["estado"],
        estacion=row["estacion"],
        ultima_fecha_registrada=row["última fecha registrada"],
        hora_inferior=row["hora inferior"],
        hora_superior=row["hora superior"],
        nivel_cloro=row["promedio de cloro (mg/l)"]
    )
    mensajes_de_prueba.append((row["telefono"], msg))

# Imprimir mensajes generados
for tel, texto in mensajes_de_prueba:
    print(f"Teléfono: {tel}")
    print(f"Mensaje: {texto}")
    print("------")


# %%
# Validar números de teléfono antes de enviar mensajes
telefonos_validos = []
mensajes_validos = []

for tel, msg in mensajes_de_prueba:
    if validate_phone_number(tel):
        telefonos_validos.append(tel)
        mensajes_validos.append(msg)

print(f"Números válidos: {len(telefonos_validos)}")
print(f"Números inválidos: {len(mensajes_de_prueba) - len(telefonos_validos)}")


# %%
# Inicializar el enviador de mensajes
sender = EnhancedWhatsAppMessageSender()

try:
    # Enviar todos los mensajes en lote
    sender.send_batch_messages(telefonos_validos, mensajes_validos)
    
    # Mostrar números fallidos si los hay
    if sender.failed_numbers:
        print("\nNúmeros que fallaron:")
        for tel, error in sender.failed_numbers:
            print(f"{tel}: {error}")
            # guardar en una variable la lista de mensajes que fallaron y luego volver a enviar los mensajes 
            

finally:
    # Limpiar la sesión
    sender.cleanup()
    


