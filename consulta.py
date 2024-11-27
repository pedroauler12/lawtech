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


def consulta_processo(numero_processo):

    url_pesquisa = "https://processo.stj.jus.br/processo/pesquisa/?aplicacao=processos.ea"
    driver.get(url_pesquisa)

    campo_numero_unico = driver.find_element(By.ID, "idNumeroUnico")
    campo_numero_unico.send_keys(numero_processo)

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
    driver.quit()
    return texto_ultima_fase

    

print(consulta_processo("10035034420168260101"))
