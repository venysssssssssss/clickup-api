import requests
import pandas as pd
import os

# Define o caminho da pasta onde os dados serão salvos
data_folder = 'data'

# Verifica se a pasta 'data' existe e a cria se não existir
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# ID da lista no ClickUp
list_id = "174940580"
url = f"https://api.clickup.com/api/v2/list/{list_id}/task"

# Parâmetros da consulta
query = {
    "archived": "false",
    "include_markdown_description": "true",
    "page": "0",
}

# Cabeçalhos da solicitação
headers = {"Authorization": "pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2"}

# Fazendo a solicitação
response = requests.get(url, headers=headers, params=query)

# Verificando se a solicitação foi bem-sucedida
if response.status_code == 200:
    # Convertendo a resposta JSON em um DataFrame pandas
    data = response.json()
    df = pd.json_normalize(data['tasks'])
    
    # Define o caminho completo do arquivo Excel
    excel_file_path = os.path.join(data_folder, f'dados_clickup_{list_id}.xlsx')

    # Salva o DataFrame em um arquivo Excel
    df.to_excel(excel_file_path, index=False)
    
    print(f'Dados salvos com sucesso em "{excel_file_path}"')
else:
    print(f"Erro ao fazer a solicitação. Código de status: {response.status_code}")
