import os
import re
import httpx
import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get('/get_clickup_data/{list_id}')
async def get_clickup_data(list_id: str):
    # Define o caminho da pasta onde os dados serão salvos
    data_folder = 'data'

    # Verifica se a pasta 'data' existe e a cria se não existir
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    url = f'https://api.clickup.com/api/v2/list/{list_id}/task'

    # Parâmetros da consulta
    query = {
        'archived': 'false',
        'include_markdown_description': 'true',
    }

    # Cabeçalhos da solicitação
    headers = {'Authorization': 'pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2'}

    # Fazendo a solicitação
    response = requests.get(url, headers=headers, params=query)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Convertendo a resposta JSON em um DataFrame pandas
        data = response.json()
        tasks = data['tasks']

        # Lista para armazenar os dados das tarefas
        task_data = []

        # Percorre cada tarefa
        for task in tasks:
            # Dicionário para armazenar os dados da tarefa atual
            task_dict = {}

            # Adiciona os campos principais ao dicionário da tarefa
            task_dict['id'] = task['id']
            task_dict['name'] = task['name']
            task_dict['text_content'] = task['text_content'].replace('\n', ' ')
            task_dict['status'] = task['status']['status']
            task_dict['date_created'] = task['date_created']
            task_dict['date_updated'] = task['date_updated']
            task_dict['url'] = task['url']

            # Percorre cada campo personalizado na tarefa
            for field in task['custom_fields']:
                # Adiciona o valor do campo personalizado ao dicionário da tarefa
                if 'value' in field:
                    task_dict[field['name']] = field['value']
                else:
                    task_dict[field['name']] = None

            # Adiciona o dicionário da tarefa à lista de dados das tarefas
            task_data.append(task_dict)

        # Converte a lista de dados das tarefas em um DataFrame pandas
        df = pd.DataFrame(task_data)

        # Substitui valores de ponto flutuante não compatíveis com JSON
        df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

        # Define o caminho completo do arquivo CSV
        csv_file_path = os.path.join(
            data_folder, f'dados_clickup_{list_id}.xlsx'
        )

        # Salva o DataFrame em um arquivo CSV
        df.to_excel(csv_file_path, index=False)

        # Retorna a estrutura dos dados e a mensagem de sucesso
        return {
            'message': f'Dados salvos com sucesso em "{csv_file_path}"',
            'data': df.to_dict(),
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f'Erro ao fazer a solicitação. Código de status: {response.status_code}',
        )


@app.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    url = f'https://api.clickup.com/api/v2/list/{list_id}/task'

    # Parâmetros da consulta
    query = {
        'archived': 'false',
        'include_markdown_description': 'true',
    }

    # Cabeçalhos da solicitação
    headers = {'Authorization': 'pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2'}

    # Fazendo a solicitação
    response = requests.get(url, headers=headers, params=query)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Convertendo a resposta JSON em um dicionário
        data = response.json()

        # Lista para armazenar os dados filtrados
        filtered_data = []

        # Variável para contar projetos
        project_count = 0

        # Lista de nomes de campos conhecidos
        field_names = [
            'CARTEIRA DEMANDANTE',
            'E-MAIL',
            'ESCOPO',
            'OBS',
            'OBJETIVO DO GANHO',
            'KPI GANHO',
            '💡 TIPO DE PROJETO',
            'TIPO DE OPERAÇÃO',
            'PRODUTO',
            'OPERAÇÃO',
            'SITE',
            'UNIDADE DE NEGÓCIO',
            'DIRETOR TAHTO',
            'CLIENTE',
            'TIPO',
            '💡 R$ ANUAL (PREVISTO)',
            'GERENTE OI',
            'FERRAMENTA ENVOLVIDA',
            'CENÁRIO PROPOSTO',
        ]

        # Percorre cada tarefa
        for task in data['tasks']:
            # Incrementa o contador de projetos
            project_count += 1

            # Dicionário para armazenar os dados filtrados da tarefa
            filtered_task = {
                'Projeto': project_count,
                'ID': task['id'],
                'Status': task['status']['status'],
            }

            # Texto da tarefa sem quebras de linha
            task_text = (
                task['text_content'].replace('\n', ' ').replace('.:', '')
            )

            # Adiciona os campos ao dicionário filtrado
            for field_name in field_names:
                # Encontra o campo no texto da tarefa
                match = re.search(
                    f'{field_name}\s*:\s*(.*?)(?=\s*{"|".join(field_names)}\s*:|$)',
                    task_text,
                    re.IGNORECASE,
                )
                if match:
                    field_value = match.group(1).strip()
                    filtered_task[field_name] = field_value

            # Verificação específica para "💡 R$ ANUAL (PREVISTO)"
            if '💡 TIPO DE PROJETO' in filtered_task:
                tipo_projeto_value = filtered_task['💡 TIPO DE PROJETO']
                if '💡 R$ ANUAL (PREVISTO)' in tipo_projeto_value:
                    tipo_projeto_parts = tipo_projeto_value.split(
                        '💡 R$ ANUAL (PREVISTO)'
                    )
                    filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[
                        0
                    ].strip()
                    filtered_task[
                        '💡 R$ ANUAL (PREVISTO)'
                    ] = tipo_projeto_parts[1].strip()

            # Adiciona os dados filtrados à lista
            filtered_data.append(filtered_task)

        # Retorna os dados filtrados
        return filtered_data
    else:
        raise HTTPException(
            status_code=400,
            detail=f'Erro ao fazer a solicitação. Código de status: {response.status_code}',
        )
