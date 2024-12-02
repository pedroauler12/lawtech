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
        logging.FileHandler("processo_scraping.log", mode="a"),  # Salva em arquivo
        logging.StreamHandler()  # Exibe no terminal
    ]
)

# Configuração do Selenium
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Caminho do ChromeDriver (carregado do arquivo .env)
chrome_driver_path = os.getenv("chrome_path")

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Lê os 10 primeiros links de cada matéria
links_por_materia = {}
with open("resultados_links.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        materia = row["Matéria"]
        if materia not in links_por_materia:
            links_por_materia[materia] = []
        if len(links_por_materia[materia]) < 10:
            links_por_materia[materia].append(row)

# Lista para armazenar os resultados
resultados = []

# Processar cada link
try:
    for materia, links in links_por_materia.items():
        for link_info in links:
            link = link_info["Link"]
            titulo = link_info["Título"]

            logging.info(f"Processando link: {link} | Matéria: {materia} | Título: {titulo}")
            try:
                driver.get(link)

                # Aguarda até que o conteúdo da página esteja carregado
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "documento"))
                )

                # Analisa o conteúdo da página com BeautifulSoup
                soup = BeautifulSoup(driver.page_source, "lxml")

                # Captura todos os documentos
                documentos = soup.find_all("div", class_="documento")
                logging.info(f"Encontrados {len(documentos)} documentos no link.")

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
                        jurisprudencia_parts = jurisprudencia.get_text(separator="\n", strip=True).split("\n")
                        links = jurisprudencia.find_all("a")

                        for part, link in zip(jurisprudencia_parts, links):
                            texto_link = link.get_text(strip=True)
                            link_formatado = f"{part}\nSTJ - {texto_link}"
                            jurisprudencias_completas.append(link_formatado)

                        documento_info["Jurisprudência Citada"] = "\n\n".join(jurisprudencias_completas)
                    else:
                        documento_info["Jurisprudência Citada"] = "Jurisprudência não citada"

                    # Adiciona o documento aos resultados
                    resultados.append(documento_info)

                    logging.info(f"Capturado documento: {documento_info.get('Número do Documento', 'Sem título')}")

            except Exception as e:
                logging.error(f"Erro ao processar link: {link} | Erro: {e}")

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
    "Jurisprudência Citada",
]

# Salva os resultados em um arquivo CSV
csv_filename = "documentos_jurisprudencia_top10.csv"
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
xlsx_filename = "documentos_jurisprudencia_top10.xlsx"
df = pd.DataFrame(resultados, columns=colunas)
df.to_excel(xlsx_filename, index=False)

logging.info(f"Resultados salvos no arquivo '{xlsx_filename}'.")
print(f"Resultados salvos nos arquivos:\n- '{csv_filename}'\n- '{xlsx_filename}'")
