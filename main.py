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
time.sleep(2)




url_pesquisa = "https://processo.stj.jus.br/processo/pesquisa/?aplicacao=processos.ea"
driver.get(url_pesquisa)

time.sleep(5)
# encontrar campo do número unico 

campo_numero_unico = driver.find_element(By.ID, "idNumeroUnico")
#digitar numero do processo #1003503-44.2016.8.26.0101

campo_numero_unico.send_keys("10035034420168260101")

time.sleep(5)
#encontrar botao de enviar consulta

btn_consulta = driver.find_element(By.ID, "idBotaoPesquisarFormularioExtendido")


#clique no botao de enviar consulta

btn_consulta.click()
time.sleep(5)
 
#encontrar o elemento do texto
elemento_ultima_fase = driver.find_element(By.ID, "idProcessoDetalhesBloco4")

#capturar o texto do elemento
texto_ultima_fase = elemento_ultima_fase.text

print(texto_ultima_fase)

driver.quit()
