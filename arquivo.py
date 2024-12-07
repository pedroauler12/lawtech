import csv
import logging
import os
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("processo_scraping.log", mode="a"),
        logging.StreamHandler()
    ]
)

# Configuração do Selenium
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Caminho do ChromeDriver
chrome_driver_path = os.getenv("chrome_path")

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Lista para armazenar os resultados
resultados = []

# Função para capturar documentos de uma página
def capturar_documentos(materia, titulo):
    soup = BeautifulSoup(driver.page_source, "lxml")
    documentos = soup.find_all("div", class_="documento")
    logging.info(f"Encontrados {len(documentos)} documentos na página atual.")

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

        # Captura a Jurisprudência Citada (se existir)
        jurisprudencia = doc.find("div", class_="campoVeja")
        if jurisprudencia:
            jurisprudencias_completas = []
            processos_completos = []
            jurisprudencia_parts = jurisprudencia.get_text(separator="\n", strip=True).split("\n")
            links = jurisprudencia.find_all("a")

            for part, link in zip(jurisprudencia_parts, links):
                if "STJ" in part:  # Captura o título da jurisprudência
                    jurisprudencias_completas.append(part.strip())
                if "STJ" in link.get_text():  # Captura o processo
                    processos_completos.append(link.get_text(strip=True))

            # Formatar os campos de jurisprudências e processos relacionados
            documento_info["Jurisprudências Citadas"] = ", ".join(jurisprudencias_completas)
            documento_info["Processos Relacionados"] = "; ".join(processos_completos)
        else:
            documento_info["Jurisprudências Citadas"] = "Nenhuma jurisprudência citada"
            documento_info["Processos Relacionados"] = "Nenhum processo relacionado"

        # Adiciona o documento aos resultados
        resultados.append(documento_info)

# Ler o primeiro link do arquivo resultados_links.csv
with open("resultados_links.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    first_link_info = next(reader)

# Processar apenas o primeiro link
try:
    link = first_link_info["Link"]
    materia = first_link_info["Matéria"]
    titulo = first_link_info["Título"]

    logging.info(f"Processando link: {link} | Matéria: {materia} | Título: {titulo}")
    driver.get(link)

    while True:
        # Captura os documentos da página atual
        capturar_documentos(materia, titulo)

        # Verifica se existe o botão de próxima página
        try:
            proxima_pagina = driver.find_element(By.CLASS_NAME, "iconeProximaPagina")
            if "inativo" in proxima_pagina.get_attribute("class"):
                logging.info("Nenhuma próxima página disponível. Concluído.")
                break
            else:
                # Clique no botão para avançar para a próxima página
                proxima_pagina.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "documento"))
                )
                logging.info("Avançando para a próxima página...")
        except Exception as e:
            logging.error(f"Erro ao navegar para a próxima página: {e}")
            break

finally:
    driver.quit()

# Define as colunas do CSV e XLSX
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
    "Jurisprudências Citadas",
    "Processos Relacionados",
]

# Salva os resultados em um arquivo CSV
csv_filename = "arquivo_teste.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=colunas)

    # Escreve o cabeçalho
    writer.writeheader()

    # Escreve os dados
    for documento in resultados:
        linha = {coluna: documento.get(coluna, "") for coluna in colunas}
        writer.writerow(linha)

logging.info(f"Resultados salvos no arquivo '{csv_filename}'.")

# Salva os resultados em um arquivo XLSX
xlsx_filename = "arquivo_teste.xlsx"
df = pd.DataFrame(resultados, columns=colunas)
df.to_excel(xlsx_filename, index=False)

logging.info(f"Resultados salvos no arquivo '{xlsx_filename}'.")
print(f"Resultados salvos nos arquivos:\n- '{csv_filename}'\n- '{xlsx_filename}'")
