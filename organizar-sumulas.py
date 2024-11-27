import pandas as pd
import re

# Caminho para o CSV antigo
sumulas_antigas_path = 'sumulas.csv'

# Carregar o CSV antigo
sumulas_antigas_df = pd.read_csv(sumulas_antigas_path)

# Função para processar cada linha do campo 'conteudo'
def processar_sumula(conteudo):
    # Regex para capturar o número da súmula
    numero_match = re.search(r'Súmula\s*(\d+)', conteudo)
    numero = numero_match.group(1) if numero_match else None

    # Regex para capturar o título da súmula
    titulo_match = re.search(r'Súmula\s*\d+\s*([^\n]+)', conteudo)
    titulo = titulo_match.group(1).strip() if titulo_match else None

    # Regex para capturar o conteúdo da súmula
    conteudo_match = re.search(r'(?:\n|^)(?:DIREITO.*?\-.*?\.)(.*?)(?=\d{1,2}\/\d{1,2}\/\d{4})', conteudo, re.DOTALL)
    conteudo_texto = conteudo_match.group(1).strip() if conteudo_match else None

    # Regex para capturar as datas da súmula
    datas_match = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', conteudo)
    datas = ', '.join(datas_match) if datas_match else None

    return {
        "numero": numero,
        "titulo": titulo,
        "conteudo": conteudo_texto,
        "datas": datas
    }

# Processar todas as linhas do CSV antigo
sumulas_organizadas = sumulas_antigas_df['conteudo'].apply(processar_sumula)

# Converter o resultado para um DataFrame
sumulas_organizadas_df = pd.DataFrame(sumulas_organizadas.tolist())

# Salvar o novo CSV com as súmulas organizadas
csv_organizado_path = 'sumulas_organizadas.csv'
sumulas_organizadas_df.to_csv(csv_organizado_path, index=False, encoding='utf-8')

# Exibir o caminho do novo arquivo gerado
print(f"Súmulas organizadas foram salvas no arquivo: {csv_organizado_path}")
