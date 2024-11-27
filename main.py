import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv()

# Configuração do Selenium
options = Options()

chrome_driver_path = os.getenv("chrome_path")
service = Service(chrome_driver_path)
options = Options()




service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Lê o primeiro link da tabela CSV
with open("resultados/resultados_links.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    primeiro_link = next(reader)["Link"]

# Realiza o scraping da página do link
resultados = []

try:
    print(f"Acessando o link: {primeiro_link}")
    driver.get(primeiro_link)

    # Aguarda até que o conteúdo da página esteja carregado
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "documento"))
    )

    # Analisa o conteúdo da página com BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Captura todos os documentos
    documentos = soup.find_all("div", class_="documento")

    for doc in documentos:
        documento_info = {}

        # Título do Documento
        titulo = doc.find("div", class_="clsNumDocumento")
        documento_info["Número do Documento"] = titulo.get_text(strip=True) if titulo else "Não encontrado"

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

finally:
    driver.quit()

# Define as colunas do CSV
colunas = [
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
csv_filename = "documentos_estruturados.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=colunas)

    # Escreve o cabeçalho
    writer.writeheader()

    # Escreve os dados
    for documento in resultados:
        # Preenche os campos ausentes com valores vazios
        linha = {coluna: documento.get(coluna, "") for coluna in colunas}
        writer.writerow(linha)

print(f"Resultados salvos no arquivo '{csv_filename}'.")
