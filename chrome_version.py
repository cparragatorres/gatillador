from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Crear una instancia del servicio para Chrome
service = Service()
driver = webdriver.Chrome(service=service)

# Obtener la versión de ChromeDriver
version = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
print(f"Versión de ChromeDriver: {version}")

# Cerrar el navegador
driver.quit()
