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

# Caminho do ChromeDriver (definido em .env)
chrome_driver_path = os.getenv("chrome_path")

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Lista para armazenar os resultados
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
            jurisprudencias_completas = []

            # Extrai o texto completo para tentar encontrar o título (entre parênteses)
            texto_completo = jurisprudencia.get_text(" ", strip=True)
            titulo_jurisprudencia = None
            titulo_match = re.search(r'\(([^)]+)\)', texto_completo)
            if titulo_match:
                # Inclui os parênteses também: 
                # Se quiser sem parênteses, use titulo_match.group(1)
                titulo_jurisprudencia = f"({titulo_match.group(1)})"

            # Encontra todos os links (processos citados)
            links = jurisprudencia.find_all("a")
            for link in links:
                processo = link.get_text(strip=True)
                # Tenta obter o texto subsequente ao link (irmão de texto)
                texto_apos_link = link.next_sibling
                uf = ""
                if texto_apos_link and isinstance(texto_apos_link, str):
                    texto_apos_link = texto_apos_link.strip()
                    # Procura UF no final do texto (ex: -SP, -RS)
                    uf_match = re.search(r'\-(\w{2})$', texto_apos_link)
                    if uf_match:
                        uf = uf_match.group(1)

                jurisprudencias_completas.append({
                    "Título da Jurisprudência": titulo_jurisprudencia if titulo_jurisprudencia else "",
                    "Tribunal": "STJ",
                    "Processo Citado": processo,
                    "Localização": uf
                })

            if jurisprudencias_completas:
                linhas_juris = []
                for j in jurisprudencias_completas:
                    linha_formatada = f"{j['Título da Jurisprudência']}\n{j['Tribunal']} - {j['Processo Citado']} - {j['Localização']}"
                    linhas_juris.append(linha_formatada)
                documento_info["Jurisprudência Citada"] = "\n\n".join(linhas_juris)
            else:
                documento_info["Jurisprudência Citada"] = "Jurisprudência citada não encontrada ou vazia"
        else:
            documento_info["Jurisprudência Citada"] = "Jurisprudência não citada"

        # Adiciona o documento aos resultados
        resultados.append(documento_info)

# Aqui vamos ler apenas o primeiro link da primeira matéria (para testes)
primeiro_link = None
with open("resultados_links.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    materias_processadas = set()
    for row in reader:
        materia = row["Matéria"]
        if materia not in materias_processadas:
            materias_processadas.add(materia)
            primeiro_link = row
            break

if primeiro_link:
    try:
        link = primeiro_link["Link"]
        materia = primeiro_link["Matéria"]
        titulo = primeiro_link["Título"]

        logging.info(f"Processando link único: {link} | Matéria: {materia} | Título: {titulo}")
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
        "Jurisprudência Citada",
    ]

    # Salva os resultados em um arquivo CSV
    csv_filename = "juris_teste.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=colunas)
        writer.writeheader()
        for documento in resultados:
            linha = {coluna: documento.get(coluna, "") for coluna in colunas}
            writer.writerow(linha)

    logging.info(f"Resultados salvos no arquivo '{csv_filename}'.")

    # Salva os resultados em um arquivo XLSX
    xlsx_filename = "juris_teste.xlsx"
    df = pd.DataFrame(resultados, columns=colunas)
    df.to_excel(xlsx_filename, index=False)

    logging.info(f"Resultados salvos no arquivo '{xlsx_filename}'.")
    print(f"Resultados salvos nos arquivos:\n- '{csv_filename}'\n- '{xlsx_filename}'")

else:
    logging.error("Nenhum link encontrado no arquivo resultados_links.csv")
    driver.quit()
