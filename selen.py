
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"))

driver.get("https://quotes.toscrape.com/")


#elemento por nome da classe
#element = driver.find_element(By.CLASS_NAME, "author")
element = driver.find_element(By.TAG_NAME, "small")

print(element.text)

driver.quit()
