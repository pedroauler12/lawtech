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

links_casos_notorios = []
links_direito_administrativo = []
with open("resultados_links.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["Matéria"] == "Casos Notórios":
            links_casos_notorios.append(row)
        elif row["Matéria"] == "Direito Administrativo" and len(links_direito_administrativo) < 10:
            links_direito_administrativo.append(row)

# Combinar os dois conjuntos de links
links_filtrados = links_casos_notorios + links_direito_administrativo

# Lista para armazenar os resultados
resultados = []

# Processar cada link filtrado
try:
    for link_info in links_filtrados:
        link = link_info["Link"]
        materia = link_info["Matéria"]
        titulo = link_info["Título"]

        print(f"Acessando o link: {link}")
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

finally:
    driver.quit()

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
csv_filename = "documentos_casos_notorios_direito_administrativo.csv"
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