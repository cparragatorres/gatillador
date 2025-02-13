from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Intentar obtener la ubicación de ChromeDriver
try:
    service = Service()
    driver = webdriver.Chrome(service=service)

    # Mostrar la ruta del ejecutable de ChromeDriver
    print(f"Ubicación de ChromeDriver: {service.path}")

    driver.quit()
except Exception as e:
    print(f"Error: {e}")
