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
import re

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

chrome_driver_path = os.getenv("chrome_path")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

resultados = []

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

        # Captura da Jurisprudência Citada (se existir)
        jurisprudencia = doc.find("div", class_="campoVeja")
        if jurisprudencia:
            html_juris = jurisprudencia.decode_contents()
            blocks = re.split(r'<br\s*/?>\s*<br\s*/?>', html_juris, flags=re.IGNORECASE)

            titulos_juris = []
            processos_juris = []

            for block in blocks:
                block = block.strip()
                if not block:
                    continue

                block_soup = BeautifulSoup(block, "lxml")
                block_text = block_soup.get_text(separator="\n", strip=True)
                lines = block_text.split("\n")

                # Extrai o título da jurisprudência
                titulo_jurisprudencia = ""
                for l in lines:
                    if l.startswith("(") and ")" in l:
                        title_match = re.search(r"\(([^)]*)\)", l)
                        if title_match:
                            titulo_jurisprudencia = f"({title_match.group(1)})"
                        break

                # Encontra todos os links (processos)
                links = block_soup.find_all("a")
                block_processes = []
                for link in links:
                    processo = link.get_text(strip=True)
                    texto_apos_link = link.next_sibling
                    uf = ""
                    if texto_apos_link and isinstance(texto_apos_link, str):
                        texto_apos_link = texto_apos_link.strip()
                        texto_apos_link = texto_apos_link.rstrip(",")
                        uf_match = re.search(r'\-(\w{2})$', texto_apos_link)
                        if uf_match:
                            uf = uf_match.group(1)

                    if uf:
                        block_processes.append(f"{processo} - {uf}")
                    else:
                        block_processes.append(processo)

                titulos_juris.append(titulo_jurisprudencia if titulo_jurisprudencia else "")
                processos_juris.append(", ".join(block_processes) if block_processes else "")

            documento_info["Jurisprudência Título(s)"] = "\n\n".join(titulos_juris)
            documento_info["Jurisprudência Processo(s)"] = "\n\n".join(processos_juris)

        else:
            documento_info["Jurisprudência Título(s)"] = "Jurisprudência não citada"
            documento_info["Jurisprudência Processo(s)"] = "Jurisprudência não citada"

        resultados.append(documento_info)

# Identificar o primeiro link de cada matéria
materias_processadas = set()
primeiros_links = []

with open("resultados_links.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        materia = row["Matéria"]
        if materia not in materias_processadas:
            materias_processadas.add(materia)
            primeiros_links.append(row)

# Processar o primeiro link de cada matéria
try:
    for link_info in primeiros_links:
        link = link_info["Link"]
        materia = link_info["Matéria"]
        titulo = link_info["Título"]

        logging.info(f"Processando link: {link} | Matéria: {materia} | Título: {titulo}")
        driver.get(link)

        while True:
            capturar_documentos(materia, titulo)

            try:
                proxima_pagina = driver.find_element(By.CLASS_NAME, "iconeProximaPagina")
                if "inativo" in proxima_pagina.get_attribute("class"):
                    logging.info("Nenhuma próxima página disponível. Concluído.")
                    break
                else:
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
    "Jurisprudência Título(s)",
    "Jurisprudência Processo(s)"
]

csv_filename = "juris_primeiro_link_por_materia.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=colunas)
    writer.writeheader()
    for documento in resultados:
        linha = {coluna: documento.get(coluna, "") for coluna in colunas}
        writer.writerow(linha)

logging.info(f"Resultados salvos no arquivo '{csv_filename}'.")

xlsx_filename = "juris_primeiro_link_por_materia.xlsx"
df = pd.DataFrame(resultados, columns=colunas)
df.to_excel(xlsx_filename, index=False)

logging.info(f"Resultados salvos no arquivo '{xlsx_filename}'.")
print(f"Resultados salvos nos arquivos:\n- '{csv_filename}'\n- '{xlsx_filename}'")
