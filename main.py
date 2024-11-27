import json
import os
import time
import csv
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


load_dotenv()

# Pegar o caminho do Chrome Driver do arquivo .env
chrome_driver_path = os.getenv("chrome_path")

# Configurar o serviço e opções
service = Service(chrome_driver_path)
options = Options()
options.add_argument("--start-maximized")  # Exemplo: abrir em tela cheia



# Inicializar o WebDriver
driver = webdriver.Chrome(service=service, options=options)
url =  "https://scon.stj.jus.br/SCON/pesquisa_pronta/listaPP.jsp"

driver.get(url)


wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btnAbreMateria")))

# Localizar todos os botões das matérias
botoes_materias = driver.find_elements(By.CLASS_NAME, "btnAbreMateria")

resultados = {}

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

        # Lista para armazenar os títulos da matéria atual
        titulos = []

        # Loop para percorrer cada título dentro da matéria
        for botao_titulo in botoes_titulos:
            # Obter o nome do título
            nome_titulo = botao_titulo.text.strip()

            # Expandir o título, se necessário
            if botao_titulo.get_attribute("aria-expanded") != "true":
                driver.execute_script("arguments[0].scrollIntoView(true);", botao_titulo)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", botao_titulo)

            # Adicionar o título à lista
            titulos.append(nome_titulo)

        # Adicionar a matéria e seus títulos ao dicionário de resultados
        resultados[nome_materia] = titulos

    except Exception as e:
        print(f"Erro ao processar a matéria ou título: {e}")
 
time.sleep(5)
driver.quit()

# Salvar os resultados em um arquivo JSON
with open("resultados.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

# Exibir os resultados no console
print(json.dumps(resultados, ensure_ascii=False, indent=4))

# Exportar resultados para um arquivo CSV
with open("resultados.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Escrever o cabeçalho
    writer.writerow(["Matéria", "Título"])
    # Escrever os dados
    for materia, titulos in resultados.items():
        for titulo in titulos:
            writer.writerow([materia, titulo])
print("Resultados salvos no arquivo 'resultados.csv'.")