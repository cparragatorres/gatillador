from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
import logging
import os

class NotificarMensajeWhatsApp:
    """
    Clase para enviar mensajes por WhatsApp Web utilizando Selenium.

    Métodos:
        iniciar_sesion(): Abre WhatsApp Web y espera a que el usuario inicie sesión.
        enviar_mensaje(numero, mensaje): Envía un mensaje a un número específico.
        enviar_mensajes_en_lote(numeros, mensajes): Envía múltiples mensajes en secuencia.
        cerrar(): Cierra el navegador y limpia los recursos.
    """

    def __init__(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        self.directorio_datos_usuario = os.path.join(base_dir, "chrome-data")

        opciones_chrome = webdriver.ChromeOptions()
        opciones_chrome.add_argument(f"--user-data-dir={self.directorio_datos_usuario}")
        opciones_chrome.add_argument('--disable-notifications')
        opciones_chrome.add_argument('--start-maximized')
        opciones_chrome.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.driver = webdriver.Chrome(options=opciones_chrome)
        self.esperar = WebDriverWait(self.driver, 40)
        self.numeros_fallidos = []
        self.sesion_iniciada = False

    def iniciar_sesion(self):
        """Inicia sesión en WhatsApp Web si aún no se ha hecho."""
        if not self.sesion_iniciada:
            try:
                self.driver.get("https://web.whatsapp.com")
                self.esperar.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                self.sesion_iniciada = True
                logging.info("Sesión de WhatsApp Web iniciada correctamente")
                time.sleep(3)
                return True
            except Exception as e:
                logging.error(f"Error al iniciar sesión en WhatsApp Web: {e}")
                return False
        return True

    def enviar_mensaje(self, numero, mensaje):
        """Envía un mensaje individual usando la URL de WhatsApp Web."""
        try:
            url = f"https://web.whatsapp.com/send?phone={numero}&text={mensaje}"
            self.driver.get(url)
            boton_enviar = self.esperar.until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            time.sleep(3)
            boton_enviar.click()

            self.esperar.until(
                EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check"]'))
            )
            logging.info(f"Mensaje enviado correctamente a {numero}")
            return True
        except Exception as e:
            logging.error(f"Error al enviar mensaje a {numero}: {e}")
            self.numeros_fallidos.append((numero, str(e)))
            return False

    def enviar_mensajes_en_lote(self, numeros, mensajes):
        """Envía múltiples mensajes en secuencia."""
        if not self.iniciar_sesion():
            return False

        for numero, mensaje in zip(numeros, mensajes):
            self.enviar_mensaje(numero, mensaje)

        return True

    def cerrar(self):
        """Cierra el navegador y libera los recursos."""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logging.error(f"Error al cerrar sesión: {e}")
