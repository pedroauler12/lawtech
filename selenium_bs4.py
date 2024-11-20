from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configuração para modo headless
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Configuração do WebDriver
driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)

# Acessa a página
driver.get("https://scon.stj.jus.br/SCON/pesquisar.jsp?b=SUMU&tipo=sumula")
soup = BeautifulSoup(driver.page_source, "lxml")
author_tag = soup.find("div", class_="listadocumentos", id="listaSumulas")

# Retorna apenas o conteúdo de texto da tag
author_text = author_tag.text if author_tag else "Autor não encontrado"
print(author_text)

# Encerra o navegador
driver.quit()
