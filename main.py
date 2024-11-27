import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
from dotenv import load_dotenv
import time

# Carregar variáveis de ambiente
load_dotenv()

# Pegar o caminho do Chrome Driver do arquivo .env
chrome_driver_path = os.getenv("chrome_path")

# Configurar o serviço e opções do Chrome
service = Service(chrome_driver_path)
options = Options()
options.add_argument("--start-maximized")

# Inicializar o WebDriver
driver = webdriver.Chrome(service=service, options=options)
url = "https://scon.stj.jus.br/SCON/pesquisa_pronta/listaPP.jsp"

driver.get(url)
time.sleep(5)

# Esperar que os botões das matérias estejam carregados
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btnAbreMateria")))

# Localizar os botões das matérias
botoes_materias = driver.find_elements(By.CLASS_NAME, "btnAbreMateria")

# Dicionário para armazenar os resultados
resultados = []

# Loop para percorrer cada matéria
for botao_materia in botoes_materias:
    try:
        # Obter o nome da matéria
        nome_materia = botao_materia.text.strip()

        # Expandir a matéria, se necessário
        if botao_materia.get_attribute("aria-expanded") != "true":
            driver.execute_script("arguments[0].scrollIntoView(true);", botao_materia)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", botao_materia)

        # Esperar que os títulos dentro da matéria estejam carregados
        div_materia_id = botao_materia.get_attribute("data-bs-target").lstrip("#")
        wait.until(EC.presence_of_element_located((By.ID, div_materia_id)))

        # Localizar os botões dos títulos dentro da matéria
        div_materia = driver.find_element(By.ID, div_materia_id)
        botoes_titulos = div_materia.find_elements(By.CLASS_NAME, "btnAbreTitulo")

        # Loop para percorrer cada título dentro da matéria
        for botao_titulo in botoes_titulos:
            try:
                # Obter o nome do título
                nome_titulo = botao_titulo.text.strip()

                # Expandir o título, se necessário
                if botao_titulo.get_attribute("aria-expanded") != "true":
                    driver.execute_script("arguments[0].scrollIntoView(true);", botao_titulo)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", botao_titulo)

                # Capturar os links associados ao título
                div_titulo_id = botao_titulo.get_attribute("data-bs-target").lstrip("#")
                div_titulo = driver.find_element(By.ID, div_titulo_id)
                links = div_titulo.find_elements(By.TAG_NAME, "a")

                # Adicionar os links ao resultado
                for link in links:
                    texto_link = link.text.strip()
                    href_link = link.get_attribute("href") or "javascript:;"
                    if texto_link:
                        resultados.append({
                            "materia": nome_materia,
                            "titulo": nome_titulo,
                            "texto_link": texto_link,
                            "link": href_link
                        })

            except Exception as e:
                print(f"Erro ao processar o título {botao_titulo.text}: {e}")

    except Exception as e:
        print(f"Erro ao processar a matéria {botao_materia.text}: {e}")

# Fechar o WebDriver
driver.quit()

# Salvar os resultados em um arquivo JSON
with open("resultados_links.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)
print("Resultados salvos no arquivo 'resultados_links.json'.")

# Exportar resultados para um arquivo CSV
with open("resultados_links.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Escrever o cabeçalho
    writer.writerow(["Matéria", "Título", "Texto do Link", "Link"])
    # Escrever os dados
    for item in resultados:
        writer.writerow([item["materia"], item["titulo"], item["texto_link"], item["link"]])
print("Resultados salvos no arquivo 'resultados_links.csv'.")
