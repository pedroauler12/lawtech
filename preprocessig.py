import pandas as pd
import spacy
from spacy.pipeline import EntityRuler
from docx import Document
import os
import glob
import openpyxl

# Função para extrair texto de um arquivo .docx
def extract_text(docx_file):
    document = Document(docx_file)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Carregar o modelo de português do spaCy
nlp = spacy.load('pt_core_news_sm')

# Adicionar o EntityRuler ao pipeline
ruler = nlp.add_pipe("entity_ruler", before='ner')

# Definir padrões personalizados
patterns = [
    {
        "label": "NUM_OAB",
        "pattern": [
            {"TEXT": {"REGEX": r"OAB[/-][A-Z]{2}"}},  
            {"LOWER": "nº"},
            {"TEXT": {"REGEX": r"\d{3}\.\d{3}"}}
        ]
    },
    {
        "label": "CPF",
        "pattern": [{"TEXT": {"REGEX": r"\d{3}\.\d{3}\.\d{3}-\d{2}"}}]
    },
    {
        "label": "CNPJ",
        "pattern": [{"TEXT": {"REGEX": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"}}]
    },
    {
        "label": "RG",
        "pattern": [{"TEXT": {"REGEX": r"\d{2}\.\d{3}\.\d{3}-\d{1}"}}]
    },
    {
        "label": "TELEFONE",
        "pattern": [{"TEXT": {"REGEX": r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"}}]
    },
    {
        "label": "ENDERECO",
        "pattern": [
            {"LOWER": {"IN": ["rua", "avenida", "travessa", "alameda", "praça"]}},
            {"IS_TITLE": True, "OP": "+"},
            {"LOWER": "nº"},
            {"LIKE_NUM": True},
            {"IS_PUNCT": True},
            {"IS_TITLE": True, "OP": "+"},
            {"LOWER": "cep"},
            {"TEXT": {"REGEX": r"\d{5}-\d{3}"}}
        ]
    },
    # Data de Evento
    {
        "label": "DATA_EVENTO",
        "pattern": [{"TEXT": {"REGEX": r"\d{1,2} de [a-zç]+ de \d{4}"}}]
    },
    # Padrões para EMAIL
    {
        "label": "EMAIL",
        "pattern": [
            {"LOWER": "e-mail"},
            {"ORTH": ":"},
            {"TEXT": {"REGEX": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"}}
        ]
    },
    {
        "label": "EMAIL",
        "pattern": [{"TEXT": {"REGEX": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"}}]
    },
    {
        "label": "ORG",
        "pattern": [
            {"IS_TITLE": True, "OP": "+"},  # Um ou mais tokens com a primeira letra maiúscula
            {"TEXT": "S.A."}                  # Token terminando com "S.A."
        ]
    }
]

# Adicionar os padrões ao EntityRuler
ruler.add_patterns(patterns)

# Função para anonimizar o texto
def anonimizar_texto(texto):
    doc = nlp(texto)
    texto_anonimizado = texto
    for ent in doc.ents:
        if ent.label_ in ['NUM_OAB', 'CPF', 'CNPJ', 'RG', 'TELEFONE', 'ENDERECO', 'DATA_EVENTO', 'PER', 'ORG', 'EMAIL', 'NUM_PROCESSO']:
            placeholder = f'[{ent.label_}]'
            texto_anonimizado = texto_anonimizado.replace(ent.text, placeholder)
    return texto_anonimizado

# Diretório onde os arquivos estão armazenados
diretorio = 'peticoes'

# Navegar até o diretório
os.chdir(diretorio)

# Coletar os arquivos pré-corrigidos
arquivos_pre = sorted(glob.glob('preCorrecao1.docx'))

# Extrair o texto da primeira petição pré-corrigida
texto_pre = extract_text(arquivos_pre[0])

# Processar o texto com spaCy
doc = nlp(texto_pre)

# Separar o texto em linhas
linhas = texto_pre.split('\n')

# Inicializar a lista para armazenar as linhas da tabela
tabela = []

# Inicializar dicionário para contar ocorrências de cada label por linha
from collections import defaultdict

for linha_num, linha in enumerate(linhas, start=1):
    doc_linha = nlp(linha)
    entidades = [(ent.text, ent.label_) for ent in doc_linha.ents]
    
    # Inicializar dicionário para a linha
    linha_dict = {'linha_num': linha_num}
    
    # Contadores para duplicar colunas se necessário
    contadores = defaultdict(int)
    
    for ent_text, ent_label in entidades:
        contadores[ent_label] += 1
        label_col = f"{ent_label}_{contadores[ent_label]}" if contadores[ent_label] > 1 else ent_label
        linha_dict[label_col] = ent_text
    
    # Adicionar a coluna 'TEXT' com o conteúdo restante
    # Remover as entidades do texto
    texto_sem_entidades = linha
    for ent_text, ent_label in entidades:
        texto_sem_entidades = texto_sem_entidades.replace(ent_text, '')
    
    linha_dict['TEXT'] = texto_sem_entidades.strip()
    
    tabela.append(linha_dict)

# Criar o DataFrame
df_tabela = pd.DataFrame(tabela)

# Exibir a tabela
print(df_tabela.head())

# Salvar a tabela para revisão (opcional)
df_tabela.to_xlsx('tabela_anotada_peticao1_pre.xlsx', index=False)
