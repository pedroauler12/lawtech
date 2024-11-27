from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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


wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btnAbreMateria")))

# Localizar todos os botões das matérias
botoes_materias = driver.find_elements(By.CLASS_NAME, "btnAbreMateria")

for botao in botoes_materias:
    try:
        # Verificar se a matéria já está expandida
        if botao.get_attribute("aria-expanded") == "true":
            print(f"Matéria {botao.get_attribute('data-bs-target')} já está expandida. Pulando...")
            continue

        # Rolar para o botão estar visível (evita problemas de clique)
        driver.execute_script("arguments[0].scrollIntoView(true);", botao)
        time.sleep(1)  # Pausa breve para estabilizar o scroll

        # Usar JavaScript para clicar no botão
        driver.execute_script("arguments[0].click();", botao)
        print(f"Matéria {botao.get_attribute('data-bs-target')} foi aberta.")

        # Pausa para permitir a abertura da matéria
        time.sleep(2)

    except Exception as e:
        print(f"Erro ao processar o botão: {e}")

# temos o id div de cada area do direito , sendo id="divMateria*" onde * é um numero de 1 a 13

'''
time.sleep(2)
materia = driver.find_element(By.ID, "divMateria1")
print(materia.text)



# Capturar o elemento de interesse

materia = driver.find_element(By.ID, "divTitulo10")

# Obter o texto visível
print("Texto visível no elemento:")
print(materia.text)
'''

driver.quit()