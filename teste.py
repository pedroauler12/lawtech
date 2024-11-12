from docx import Document
import os
import glob
import pandas as pd
import spacy
from spacy.pipeline import EntityRuler
from collections import defaultdict

# Função para extrair texto de um arquivo .docx
def extract_text(docx_file):
    document = Document(docx_file)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Diretório onde os arquivos estão armazenados
diretorio = 'peticoes'

# Navegar até o diretório
os.chdir(diretorio)

# Coleta dos arquivos pré-corrigidos
arquivos_pre = sorted(glob.glob('preCorrecao*.docx'))

# Verificar se há pelo menos um arquivo
if not arquivos_pre:
    raise FileNotFoundError("Nenhum arquivo pré-corrigido encontrado no diretório especificado.")

# Extrair texto da primeira petição pré-corrigida
texto_pre = extract_text(arquivos_pre[0])

# Carregar o modelo de português do spaCy
nlp = spacy.load('pt_core_news_sm')

# Inicializar o EntityRuler com overwrite_ents=True para priorizar os padrões personalizados
ruler = nlp.add_pipe("entity_ruler", before='ner', config={"overwrite_ents": True})

# Definir padrões personalizados para PER, ORG e as novas labels
patterns = [
    # 1. Pessoas com Prefixos "Dr.", "Dra.", "Sr.", "Sra." (case-insensitive) - Nome próprio (title case)
    {
        "label": "PER",
        "pattern": [
            {"LOWER": {"IN": ["dr", "dr.", "dra", "dra.", "sr", "sr.", "sra", "sra."]}},  # Prefixos
            {"IS_TITLE": True},        # Nome próprio (nome)
            {"IS_TITLE": True, "OP": "+"}        # Nome próprio (uma ou mais palavras com inicial maiúscula)
        ]
    },
    # 2. Pessoas com Prefixos "Dr.", "Dra.", "Sr.", "Sra." (case-insensitive) - Nome próprio (all caps)
    {
        "label": "PER",
        "pattern": [
            {"LOWER": {"IN": ["dr", "dr.", "dra", "dra.", "sr", "sr.", "sra", "sra."]}},  # Prefixos
            {"IS_UPPER": True},        # Nome próprio (nome)
            {"IS_UPPER": True, "OP": "+"}        # Nome próprio (uma ou mais palavras em caixa alta)
        ]
    },
    # 3. Pessoas completamente em caixa alta (sem prefixo)
    {
        "label": "PER",
        "pattern": [
            {"IS_UPPER": True, "OP": "+"},        # Uma ou mais palavras em caixa alta
        ]
    },
    # 4. Organizações em Caixa Alta
    {
        "label": "ORG",
        "pattern": [
            {"IS_UPPER": True, "OP": "+"},       # Uma ou mais palavras em caixa alta
            {"TEXT": {"NOT_IN": ["DR", "DR.", "DRA", "DRA.", "SR", "SR.", "SRA", "SRA."]}}  # Excluir padrões de pessoas
        ]
    },
    # 5. OAB
    {
        "label": "OAB",
        "pattern": [
            {"TEXT": {"REGEX": r"OAB[-/]?[A-Z]{2}"}},  # "OAB/SP", "OAB-SP", etc.
            {"LOWER": "nº"},                         # "nº"
            {"TEXT": {"REGEX": r"\d{3}\.\d{3}"}},     # Número de registro (ex: "84.009")
        ]
    },
    # 6. EMAIL
    {
        "label": "EMAIL",
        "pattern": [
            {"TEXT": {"REGEX": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"}}
        ]
    },
    # 7. TELEFONE
    {
        "label": "TELEFONE",
        "pattern": [
            {"TEXT": {"REGEX": r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"}}
        ]
    },
    # 8. DATA (Formato com Mês por Extenso)
     {
        "label": "DATA",
        "pattern": [
            {"TEXT": {"REGEX": r"\b\d{1,2}/\d{1,2}/\d{4}\b"}}  # Formato 16/08/2024
        ]
    },
    {
        "label": "DATA",
        "pattern": [
            {"TEXT": {"REGEX": r"\b\d{1,2} de [a-zç]+ de \d{4}\b"}}  # Formato 02 de setembro de 2024
        ]
    },
    # 9. CNPJ
    {
        "label": "CNPJ",
        "pattern": [
            {"TEXT": {"REGEX": r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"}}
        ]
    },
    # 10. CPF
    {
        "label": "CPF",
        "pattern": [
            {"TEXT": {"REGEX": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"}}
        ]
    }
]

# Adicionar os padrões ao EntityRuler
ruler.add_patterns(patterns)

# Função para anonimizar o texto de uma linha substituindo as entidades por seus placeholders
def anonimizar_texto_linha(linha):
    doc = nlp(linha)
    texto_anonimizado = linha
    # Ordenar as entidades por posição de início (start_char) em ordem decrescente
    entidades = sorted(doc.ents, key=lambda ent: ent.start_char, reverse=True)
    for ent in entidades:
        if ent.label_ in ['ORG', 'PER', 'OAB', 'EMAIL', 'TELEFONE', 'DATA', 'CNPJ', 'CPF']:
            placeholder = f'[{ent.label_}]'
            # Substituir a entidade no texto
            texto_anonimizado = texto_anonimizado[:ent.start_char] + placeholder + texto_anonimizado[ent.end_char:]
    return texto_anonimizado

# Processar o texto pré-corrigido e dividir em linhas
linhas = texto_pre.split('\n')

# Inicializar uma lista para armazenar os dados da tabela
dados_tabela = []

# Iterar sobre cada linha e identificar entidades
for idx, linha in enumerate(linhas):
    if not linha.strip():
        continue  # Pular linhas vazias
    doc_linha = nlp(linha)
    entidades = [(ent.text, ent.label_) for ent in doc_linha.ents]
    
    linha_dict = {}
    
    if entidades:
        # Contar quantas vezes cada label aparece para duplicar colunas se necessário
        label_counts = defaultdict(int)
        for ent_text, ent_label in entidades:
            label_counts[ent_label] += 1
        
        # Criar um dicionário para a linha com as entidades
        for ent_text, ent_label in entidades:
            count = label_counts[ent_label]
            if count > 1:
                label_name = f"{ent_label}_{count}"
                label_counts[ent_label] -= 1
            else:
                label_name = ent_label
            linha_dict[label_name] = ent_text
    
    # Anonimizar o texto da linha
    texto_anonimizado = anonimizar_texto_linha(linha)
    
    # Adicionar a coluna 'TEXT' com o texto anonimizado
    linha_dict['TEXT'] = texto_anonimizado
    
    # Adicionar o dicionário da linha à lista
    dados_tabela.append(linha_dict)

# Definir todas as labels, garantindo que todas as colunas sejam criadas
all_labels = ['PER', 'ORG', 'OAB', 'EMAIL', 'TELEFONE', 'DATA', 'CNPJ', 'CPF', 'TEXT']

# Determinar todas as colunas necessárias, incluindo as novas labels
todas_colunas = set(all_labels)
for linha in dados_tabela:
    todas_colunas.update(linha.keys())

# Ordenar as colunas para melhor organização
todas_colunas = sorted(todas_colunas)

# Criar o DataFrame com todas as colunas, preenchendo com NaN onde não houver dados
df_entidades = pd.DataFrame(dados_tabela, columns=todas_colunas)

# Exibir o DataFrame resultante
print("\nTabela de Entidades Identificadas:")
print(df_entidades)

import openpyxl
df_entidades.to_excel('ent_ident.xlsx', engine='openpyxl', index=False)
