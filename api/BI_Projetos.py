import requests
import pandas as pd
import datetime
import os

# Verifica se a pasta 'data' existe e a cria se não existir
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# IDs das listas dentro da pasta "Carteira de Negócios"
list_ids = ["174940580", "192943657", "192943564", "192943568", "900700594787"]

# Funções para extrair os dados de cada campo
def extract_field(task, field_name):
    try:
        for field in task['custom_fields']:
            if field['name'] == field_name:
                return field['value']
    except Exception as e:
        print(f"Erro ao extrair campo '{field_name}': {e}")
        return "---"

# Lista de campos personalizados que você deseja extrair
custom_fields = ['Nome', 'Escopo', '💡 RESTRIÇÕES', 'Tem impacto de privacidade (LGPD)', '.: ADMINISTRATIVO :.', '.: COMUNICAÇÃO :.', '.: FÁBRICA DE CONTEÚDOS :.', '.: FINANCEIRO :.', '.: MIS :.', '.: PLANEJAMENTO :.', '.: PROCESSOS :.', '.: QUALIDADE :.', '.: RH DAP :.', '.: RH RECRUTAMENTO E SELE.: TI FAST TRACKING (SISTEMAS) :.', '.: TI GOVERNANÇA :.', '.: TI MICROINFORMATICA :.', '.: TI OPERAÇÕES :.', '💡 ESTE PROJETO É REGULATÓRIO?', '💡 RISCO', 'FOCAL', 'GERENTE/SUPERINTENDENTE', 'DATA IMPLANTAÇÃO']

# DataFrame para armazenar os dados
df_marks = pd.DataFrame(columns=custom_fields)

# Iterar sobre cada lista e extrair os dados
for list_id in list_ids:
    print(f"Extraindo dados da lista {list_id}")
    page = 0
    while True:
        page += 1
        print(f"Página {page}...")

        # URL da lista atual
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task?page={page}"
        
        # Parâmetros da consulta
        query = {"include_closed": "true"}
        
        # Cabeçalhos da solicitação
        headers = {
            "Content-Type": "application/json",
            "Authorization": "pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2",
            "charset": "utf-8",
        }
        
        # Fazendo a solicitação
        response = requests.get(url, headers=headers, params=query)
        data = response.json()
        
        # Verifica se há tarefas nesta página
        if not data['tasks']:
            print("Nenhuma tarefa encontrada.")
            break
        
        # Itera sobre cada tarefa na página e extrai os dados
        for task in data['tasks']:
            new_row = {}
            for field_name in custom_fields:
                new_row[field_name] = extract_field(task, field_name)
            df_marks = pd.concat([df_marks, pd.DataFrame([new_row])], ignore_index=True)

# Define o caminho completo do arquivo Excel
excel_file_path = os.path.join(data_folder, 'dados_clickup.xlsx')

# Salva o DataFrame em um arquivo Excel
df_marks.to_excel(excel_file_path, index=False)

print(f'Dados salvos com sucesso em "{excel_file_path}"')
