from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv
import time 

load_dotenv()

# Pegar o caminho do Chrome Driver do arquivo .env
chrome_driver_path = os.getenv("chrome_path")

# Configurar o serviço e opções
service = Service(chrome_driver_path)
options = Options()
options.add_argument("--start-maximized")  # Exemplo: abrir em tela cheia



# Inicializar o WebDriver
driver = webdriver.Chrome(service=service, options=options)
url =  "https://scon.stj.jus.br/SCON/pesquisa_pronta/listaPP.jsp"

driver.get(url)
time.sleep(5)

btn_abrir_todas = driver.find_element(By.ID, "btnAbrirTodas")
btn_abrir_todas.click()

# Capturar o elemento de interesse
time.sleep(2)  # Aguardar o carregamento do conteúdo
material = driver.find_element(By.ID, "divTitulo10")

# Obter o texto visível
print("Texto visível no elemento:")
print(material.text)



driver.quit()