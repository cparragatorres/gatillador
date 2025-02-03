from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging
from urllib.parse import quote

class EnhancedWhatsAppMessageSender:
    def __init__(self):
        # Configuración del navegador
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 40)
        self.failed_numbers = []
        self.is_logged_in = False

    def initialize_session(self):
        """Inicializa la sesión de WhatsApp Web una sola vez."""
        if not self.is_logged_in:
            try:
                self.driver.get("https://web.whatsapp.com")
                # Esperar a que el usuario escanee el QR y se cargue WhatsApp
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                self.is_logged_in = True
                logging.info("WhatsApp Web session initialized successfully")
                time.sleep(3)  # Dar tiempo adicional para que todo cargue
                return True
            except Exception as e:
                logging.error(f"Failed to initialize WhatsApp Web session: {e}")
                return False
        return True

    from utils33 import format_message

    #class EnhancedWhatsAppMessageSender:
        # ...
    def send_message(self, phone_number, message):
            """
            Envía un mensaje usando URL directa con el nuevo formato.
            """
            try:
                url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
                self.driver.get(url)
                send_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                )
                time.sleep(2)
                send_button.click()
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check"]'))
                )
                logging.info(f"Message sent successfully to {phone_number}")
                return True
            except Exception as e:
                logging.error(f"Failed to send message to {phone_number}: {e}")
                self.failed_numbers.append((phone_number, str(e)))
                return False   


    def send_batch_messages(self, phone_numbers, messages):
        """Envía mensajes en lote."""
        if not self.initialize_session():
            return False
        
        for phone, message in zip(phone_numbers, messages):
            self.send_message(phone, message)
        
        return True

    def cleanup(self):
        """Limpia los recursos."""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")