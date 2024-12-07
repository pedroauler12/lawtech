# Web Scraping Jurídico - Projeto de Extração de Dados

## Introdução

Este projeto foi desenvolvido com o objetivo de realizar o **web scraping de dados jurídicos** de um portal dinâmico. Nosso foco é coletar informações organizadas sobre **matérias jurídicas**, seus respectivos **títulos**, e os **documentos detalhados** relacionados a cada título. 

O resultado final é consolidado em arquivos CSV e XLSX para análise posterior. A coleta inclui detalhes como processos, ementas, acórdãos e jurisprudências citadas. A estrutura foi dividida em duas grandes etapas para facilitar o desenvolvimento e a organização.

---

## Parte 1: Extração de Links e Criação da Tabela Inicial

### Objetivo

Na primeira etapa, buscamos identificar e extrair os **links principais** que correspondem a diferentes **matérias jurídicas** e seus **títulos** associados. Esses links servem como entrada para a próxima fase do projeto, onde realizamos a coleta detalhada dos documentos.

### Estratégia

1. **Navegação Dinâmica**:
   - Utilizamos o Selenium para interagir com a página dinâmica e capturar os links relevantes.
   - Cada matéria contém títulos associados, e os links são extraídos sistematicamente.

2. **Estrutura da Página**:
   - Os botões de interação e as classes HTML foram inspecionados para identificar os elementos correspondentes.
   - Botões com classes como `btnAbreMateria` e `btnAbreTitulo` foram utilizados para navegar e expandir os elementos na página.

3. **Resultados**:
   - Os links extraídos foram organizados em um arquivo CSV chamado `resultados_links.csv`, contendo colunas para a **matéria**, o **título** e o **link**.

### Trecho Relevante do Código

```python
# Encontrar todos os botões que abrem as matérias
botoes_materias = driver.find_elements(By.CLASS_NAME, "btnAbreMateria")

# Loop para clicar em cada botão de matéria
for botao in botoes_materias:
    botao.click()
    time.sleep(2)  # Aguarda para garantir que o conteúdo seja carregado

    # Após abrir uma matéria, localizar os títulos
    botoes_titulos = driver.find_elements(By.CLASS_NAME, "btnAbreTitulo")
    for botao_titulo in botoes_titulos:
        titulo = botao_titulo.text.strip()
        link = botao_titulo.get_attribute("data-bs-target")
        resultados.append({"Matéria": materia, "Título": titulo, "Link": link})
```

## Parte 2: Extração de Documentos Relacionados a Cada Link

### Objetivo

Na segunda etapa, extraímos as informações detalhadas de cada **título** e seus respectivos **documentos**. Isso inclui dados como:

- **Processo**
- **Relator**
- **Órgão julgador**
- **Data do julgamento**
- **Ementa**
- **Acórdão**
- **Jurisprudências citadas**

### Estratégia

#### Navegação por Links:

- Para cada link identificado na etapa anterior, abrimos a página e coletamos os documentos listados.
- Caso existam múltiplas páginas de documentos, utilizamos a navegação com os botões da página para garantir que todos os documentos sejam coletados.

#### Coleta de Dados:

- Usamos o **BeautifulSoup** para extrair os dados estruturados dentro de cada documento.
- Identificamos elementos como `clsNumDocumento` para os números dos documentos e `paragrafoBRS` para os detalhes associados.

### Resultados:

Os resultados foram salvos em arquivos CSV e XLSX, como:

- **documentos_primeiro_link_por_materia.csv**
- **documentos_primeiro_link_por_materia.xlsx**

### Trecho Relevante do Código

#### Navegação entre Páginas

```python
while True:
    # Capturar os documentos da página atual
    capturar_documentos(materia, titulo)

    # Verificar se existe o botão de próxima página
    try:
        proxima_pagina = driver.find_element(By.CLASS_NAME, "iconeProximaPagina")
        if "inativo" in proxima_pagina.get_attribute("class"):
            logging.info("Nenhuma próxima página disponível. Concluído.")
            break
        else:
            proxima_pagina.click()  # Avança para a próxima página
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "documento"))
            )
    except Exception as e:
        logging.error(f"Erro ao navegar para a próxima página: {e}")
        break
``` 
## Conclusão

Este projeto demonstrou como o uso combinado de ferramentas como **Selenium**, **BeautifulSoup** e **pandas** pode facilitar a coleta de informações estruturadas de páginas dinâmicas.

Os dados coletados foram organizados em arquivos CSV e XLSX e estão prontos para análise, permitindo:

- **Estudos acadêmicos**
- **Automação de tarefas jurídicas**
- **Desenvolvimento de sistemas para indexação e pesquisa**