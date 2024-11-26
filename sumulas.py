import logging
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from dotenv import load_dotenv

load_dotenv()

# Configuração básica do logging
logging.basicConfig(
    filename='scraping.log',  # Nome do arquivo de log
    filemode='a',              # 'a' para append, 'w' para sobrescrever
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato das mensagens
    level=logging.INFO         # Nível mínimo de severidade a ser registrado
)

# Configuração para modo headless
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Caminho para o chromedriver (ajuste conforme necessário)
chrome_driver_path = os.getenv("chrome_path")  # Altere para o caminho correto do seu chromedriver

# Configuração do WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Lista para armazenar os textos das súmulas
sumulas = []

# Inicialização do parâmetro 'i'
i = 1
sumulas_per_page = 10  # Número de súmulas por página

try:
    while True:
        url = (
            f"https://scon.stj.jus.br/SCON/sumstj/toc.jsp?"
            f"documentosSelecionadosParaPDF=&numDocsPagina={sumulas_per_page}&tipo_visualizacao=&data=&p=false&"
            f"tipo=sumula&b=SUMU&i={i}&l=10&ordenacao=-%40NUM&operador=E"
        )
        logging.info(f"Acessando a URL: {url}")
        driver.get(url)
        
        try:
            # Espera até que o elemento com id 'listaSumulas' esteja presente
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "listaSumulas"))
            )
        except Exception as e:
            logging.error(f"Erro ao carregar a página para i={i}: {e}")
            break  # Sai do loop se não for possível carregar a página
        
        # Espera adicional para garantir que todo o conteúdo seja carregado
        time.sleep(2)
        
        # Analisa o conteúdo da página com BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "lxml")
        sumulas_tag = soup.find("div", class_="listadocumentos", id="listaSumulas")
        
        if sumulas_tag:
            # Extrai o texto e adiciona à lista
            sumula_text = sumulas_tag.get_text(separator="\n", strip=True)
            # Verifica se o texto não está vazio
            if sumula_text:
                sumulas.append({'i': i, 'conteudo': sumula_text})
                logging.info(f"Capturado para i={i}: {sumula_text[:100]}...")  # Exibe os primeiros 100 caracteres
            else:
                logging.info(f"Nenhuma súmula encontrada para i={i}. Finalizando o scraping.")
                break  # Sai do loop se não houver súmulas na página
        else:
            logging.info(f"Súmulas não encontradas para i={i}. Finalizando o scraping.")
            break  # Sai do loop se o elemento 'listaSumulas' não for encontrado
        
        # Incrementa 'i' para a próxima página
        i += sumulas_per_page
        
        # Opcional: aguarda um curto período antes da próxima requisição
        time.sleep(1)

finally:
    # Encerra o navegador
    driver.quit()
    logging.info("Navegador encerrado.")

# Salva os dados em um arquivo CSV
csv_filename = 'sumulas.csv'
try:
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['i', 'conteudo']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for sumula in sumulas:
            writer.writerow(sumula)
    logging.info(f"Dados salvos em {csv_filename}")
except Exception as e:
    logging.error(f"Erro ao salvar dados no CSV: {e}")

