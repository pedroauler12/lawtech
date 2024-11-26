
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
import pandas as pd 

load_dotenv()


options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


chrome_driver_path = os.getenv("chrome_path")  # Altere para o caminho correto do seu chromedriver

# Configuração do WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://scon.stj.jus.br/SCON/jurisprudencia/toc.jsp?numDocsPagina=10&tipo_visualizacao=&filtroPorNota=&ref=&data=&p=true&b=ACOR&thesaurus=JURIDICO&i=10&l=10&tp=T&operador=E&livre=ACORDAOS&b=ACOR")


#elemento por nome da classe
#element = driver.find_element(By.CLASS_NAME, "author")
element = driver.find_element(By.CLASS_NAME, "listadocumentos")


print(element.text)

driver.quit()
