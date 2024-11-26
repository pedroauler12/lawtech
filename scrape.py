from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os

load_dotenv()

def scrape_website(website):
    chrome_driver_path = os.getenv("chrome_path")  # Altere para o caminho correto do seu chromedriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
    
    try:
        driver.get(website)
        html = driver.page_source
        print(html)
    
    finally:
        driver.quit()
        
scrape_website("https://portal.tjpr.jus.br/jurisprudencia/")