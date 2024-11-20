import requests

from bs4 import BeautifulSoup

# URL da pesquisa no STJ

url = ' https://www.stj.jus.br/portal/jurisprudencia/pesquisa/resultado'

# Parâmetros de pesquisa

params = {

'q': 'responsabilidade civil dano moral',

'paginacao': '50'

}

# Solicitação HTTP GET

response = requests.get (url, params=params)

# Analisando o conteúdo HTML com BeautifulSoup

soup = BeautifulSoup (response.content, 'html.parser')

# Extraindo os resultados da jurisprudência

resultados = soup.find_all ('div', class_='resultado-jurisprudencia')

# Iterando pelos resultados e imprimindo o título e link

for resultado in resultados:
    titulo = resultado.find ('h2').text
    link = resultado.find ('a')['href']
    
print (f'Título: {titulo}\nLink: {link}\n')