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
import time

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("processo_scraping.log", mode="a"),
        logging.StreamHandler()
    ]
)

def iniciar_driver():
    chrome_driver_path = os.getenv("chrome_path")
    service = Service(chrome_driver_path)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

driver = iniciar_driver()

# Definindo as colunas para o CSV
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

# Nome do arquivo CSV para salvar progressivamente
csv_filename = "juris_teste_parcial.csv"

# Se quiser, você pode verificar se o arquivo já existe e, se sim, contar quantas linhas já existem.
# Isso permite retomar o processo de onde parou, mas isso é opcional neste exemplo.

resultados = []  # Armazena temporariamente os resultados do lote atual
links_por_lote = 350

def salvar_resultados_parciais():
    """Salva os resultados atuais no arquivo CSV e limpa a lista."""
    if not resultados:
        return
    modo = "a" if os.path.exists(csv_filename) else "w"
    with open(csv_filename, modo, newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=colunas)
        if modo == "w":
            writer.writeheader()
        for doc in resultados:
            linha = {coluna: doc.get(coluna, "") for coluna in colunas}
            writer.writerow(linha)
    resultados.clear()  # Limpa os resultados da memória, pois já foram salvos

def capturar_documentos(materia, titulo):
    soup = BeautifulSoup(driver.page_source, "lxml")
    documentos = soup.find_all("div", class_="documento")
    logging.info(f"Encontrados {len(documentos)} documentos na página atual para a matéria '{materia}' e título '{titulo}'.")

    for doc in documentos:
        documento_info = {
            "Matéria": materia,
            "Título": titulo
        }

        titulo_doc = doc.find("div", class_="clsNumDocumento")
        documento_info["Número do Documento"] = titulo_doc.get_text(strip=True) if titulo_doc else "Não encontrado"

        identificacoes = doc.find_all("div", class_="paragrafoBRS")
        for identificacao in identificacoes:
            subtitulo = identificacao.find("div", class_="docTitulo")
            texto = identificacao.find("div", class_="docTexto")
            if subtitulo and texto:
                documento_info[subtitulo.get_text(strip=True)] = texto.get_text(strip=True)

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

                titulo_jurisprudencia = ""
                for l in lines:
                    if l.startswith("(") and ")" in l:
                        title_match = re.search(r"\(([^)]*)\)", l)
                        if title_match:
                            titulo_jurisprudencia = f"({title_match.group(1)})"
                        break

                links = block_soup.find_all("a")
                block_processes = []
                for link_elm in links:
                    processo = link_elm.get_text(strip=True)
                    texto_apos_link = link_elm.next_sibling
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
                if block_processes:
                    processos_juris.append(", ".join(block_processes))
                else:
                    processos_juris.append("")

            documento_info["Jurisprudência Título(s)"] = "\n\n".join(titulos_juris) if titulos_juris else ""
            documento_info["Jurisprudência Processo(s)"] = "\n\n".join(processos_juris) if processos_juris else ""
        else:
            documento_info["Jurisprudência Título(s)"] = "Jurisprudência não citada"
            documento_info["Jurisprudência Processo(s)"] = "Jurisprudência não citada"

        resultados.append(documento_info)

try:
    with open("resultados_links.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        todos_links = list(reader)

    total_links = len(todos_links)

    for i, link_info in enumerate(todos_links):
        link = link_info["Link"]
        materia = link_info["Matéria"]
        titulo = link_info["Título"]

        logging.info(f"Processando link ({i+1}/{total_links}): {link} | Matéria: {materia} | Título: {titulo}")
        driver.get(link)

        while True:
            capturar_documentos(materia, titulo)

            try:
                proxima_pagina = driver.find_element(By.CLASS_NAME, "iconeProximaPagina")
                if "inativo" in proxima_pagina.get_attribute("class"):
                    logging.info(f"Concluído a navegação para: {materia} - {titulo}")
                    break
                else:
                    proxima_pagina.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "documento"))
                    )
                    logging.info("Avançando para a próxima página...")
            except Exception as e:
                logging.error(f"Erro ao navegar para a próxima página em {materia} - {titulo}: {e}")
                break

        # Após processar este link, verificar se atingimos 350 links
        if (i + 1) % links_por_lote == 0 and (i + 1) < total_links:
            # Salva resultados parciais antes de reiniciar o driver
            salvar_resultados_parciais()

            logging.info("Atingiu o limite de 350 links, reiniciando o driver e aguardando 20s...")
            driver.quit()
            time.sleep(20)  
            driver = iniciar_driver()

    # Ao final, se ainda houver resultados não salvos, salve agora
    salvar_resultados_parciais()

finally:
    driver.quit()

# Agora que temos tudo salvo em juris_teste_parcial.csv,
# podemos convertê-lo em XLSX no final, se quiser:

df = pd.read_csv(csv_filename, encoding='utf-8')
xlsx_filename = "juris_teste.xlsx"
df.to_excel(xlsx_filename, index=False)

logging.info(f"Resultados finais salvos no arquivo '{xlsx_filename}'.")
print(f"Resultados salvos nos arquivos:\n- '{csv_filename}'\n- '{xlsx_filename}'")
