# Importação das bibliotecas necessárias
import os
import glob
import pandas as pd
from docx import Document
import spacy
from spacy.pipeline import EntityRuler

# 1. Função para extrair texto de arquivos .docx
def extract_text(docx_file):
    """
    Extrai o texto de um arquivo .docx.

    Parâmetros:
        docx_file (str): Caminho para o arquivo .docx.

    Retorna:
        str: Texto completo extraído do arquivo.
    """
    document = Document(docx_file)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# 2. Definir o diretório onde os arquivos estão armazenados
diretorio = 'peticoes'  # Substitua pelo caminho correto
os.chdir(diretorio)

# 3. Obter listas de arquivos para cada tipo, ordenadas
arquivos_pre = sorted(glob.glob('preCorrecao*.docx'))
arquivos_em_correcao = sorted(glob.glob('duranteCorrecao*.docx'))
arquivos_pos = sorted(glob.glob('posCorrecao*.docx'))

# 4. Verificar se o número de arquivos em cada lista é igual
assert len(arquivos_pre) == len(arquivos_em_correcao) == len(arquivos_pos), "Número de arquivos inconsistente."

# 5. Extrair textos e armazenar em listas
textos_pre = []
textos_em_correcao = []
textos_pos = []

for arquivo_pre, arquivo_em_correcao, arquivo_pos in zip(arquivos_pre, arquivos_em_correcao, arquivos_pos):
    texto_pre = extract_text(arquivo_pre)
    texto_em_correcao = extract_text(arquivo_em_correcao)
    texto_pos = extract_text(arquivo_pos)

    textos_pre.append(texto_pre)
    textos_em_correcao.append(texto_em_correcao)
    textos_pos.append(texto_pos)

# 6. Criar um DataFrame para organizar os dados
df_peticoes = pd.DataFrame({
    'texto_pre': textos_pre,
    'texto_em_correcao': textos_em_correcao,
    'texto_pos': textos_pos
})

# 7. Carregar o modelo de português do spaCy
nlp = spacy.load('pt_core_news_sm')

# 8. Criar o EntityRuler e adicionar antes do componente 'ner'

# 11. Definir a função de anonimização
def anonimizar_texto(texto):
    """
    Anonimiza o texto substituindo entidades nomeadas por placeholders.

    Parâmetros:
        texto (str): Texto original.

    Retorna:
        str: Texto anonimizado.
    """
    doc = nlp(texto)
    texto_anonimizado = texto
    for ent in doc.ents:
        if ent.label_ in [
            'PER', 'ORG', 'LOC', 'DATE', 'MONEY'
        ]:
            texto_anonimizado = texto_anonimizado.replace(ent.text, f'[{ent.label_}]')
    return texto_anonimizado

# 12. Aplicar a função de anonimização aos textos
df_peticoes['texto_pre_anonimizado'] = df_peticoes['texto_pre'].apply(anonimizar_texto)
df_peticoes['texto_em_correcao_anonimizado'] = df_peticoes['texto_em_correcao'].apply(anonimizar_texto)
df_peticoes['texto_pos_anonimizado'] = df_peticoes['texto_pos'].apply(anonimizar_texto)

# 13. Visualizar o DataFrame resultante (opcional)
pd.set_option('display.max_colwidth', None)
print(df_peticoes.head())
