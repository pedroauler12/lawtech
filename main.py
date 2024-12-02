import csv
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

# Configuração do dotenv
load_dotenv()

# Configuração de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Log em arquivo
file_handler = logging.FileHandler("scraping.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Log no terminal
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

logger.info("Início do processo de scraping para todas as matérias.")

# Configuração do Selenium
chrome_driver_path = os.getenv("chrome_path")
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

logger.info("Driver do Selenium configurado.")

# Filtrar todos os links
links_filtrados = []

try:
    with open("resultados_links.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            links_filtrados.append(row)

    logger.info(f"Total de links filtrados: {len(links_filtrados)}")

    # Lista para armazenar os resultados
    resultados = []

    # Processar cada link filtrado
    for link_info in links_filtrados:
        link = link_info["Link"]
        materia = link_info["Matéria"]
        titulo = link_info["Título"]

        try:
            logger.info(f"Acessando o link: {link}")
            driver.get(link)

            # Aguarda até que o conteúdo da página esteja carregado
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "documento"))
            )

            # Analisa o conteúdo da página com BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "lxml")

            # Captura todos os documentos
            documentos = soup.find_all("div", class_="documento")

            for doc in documentos:
                documento_info = {
                    "Matéria": materia,
                    "Título": titulo
                }

                # Título do Documento
                titulo_doc = doc.find("div", class_="clsNumDocumento")
                documento_info["Número do Documento"] = titulo_doc.get_text(strip=True) if titulo_doc else "Não encontrado"

                # Identificação (Processo, Relator, etc.)
                identificacoes = doc.find_all("div", class_="paragrafoBRS")
                for identificacao in identificacoes:
                    subtitulo = identificacao.find("div", class_="docTitulo")
                    texto = identificacao.find("div", class_="docTexto")
                    if subtitulo and texto:
                        documento_info[subtitulo.get_text(strip=True)] = texto.get_text(strip=True)

                # Conteúdo Principal do Documento (textarea ou outros elementos)
                texto_area = doc.find("textarea", class_="textareaSemformatacao")
                if texto_area:
                    documento_info["Conteúdo Principal"] = texto_area.get_text(strip=True)

                # Adiciona o documento aos resultados
                resultados.append(documento_info)

            logger.info(f"Documentos capturados com sucesso para o link: {link}")

        except Exception as e:
            logger.error(f"Erro ao processar o link {link}: {e}")

finally:
    driver.quit()
    logger.info("Driver do Selenium encerrado.")

# Define as colunas do CSV
colunas = [
    "Matéria",
    "Título",
    "Número do Documento",
    "Processo",
    "Relator",
    "Órgão Julgador",
    "Data do Julgamento",
    "Data da Publicação/Fonte",
    "Ementa",
    "Acórdão",
    "Conteúdo Principal",
]

# Salva os resultados em um arquivo CSV
csv_filename = "documentos_todas_as_materias.csv"
try:
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=colunas)

        # Escreve o cabeçalho
        writer.writeheader()

        # Escreve os dados
        for documento in resultados:
            # Preenche os campos ausentes com valores vazios
            linha = {coluna: documento.get(coluna, "") for coluna in colunas}
            writer.writerow(linha)

    logger.info(f"Resultados salvos no arquivo '{csv_filename}'.")

except Exception as e:
    logger.error(f"Erro ao salvar os resultados no CSV: {e}")

logger.info("Processo de scraping para todas as matérias concluído.")
