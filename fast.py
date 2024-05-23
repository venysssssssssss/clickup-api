import os
import re
import httpx
import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    """
    Retrieves data from ClickUp API for a given list ID and organizes it based on specific fields.

    Args:
        list_id (str): The ID of the ClickUp list.

    Returns:
        list: A list of dictionaries containing the filtered data.
    """
    url = f'https://api.clickup.com/api/v2/list/{list_id}/task'

    query = {
        'archived': 'false',
        'include_markdown_description': 'true',
    }

    headers = {'Authorization': 'pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2'}

    async with httpx.AsyncClient(timeout=140.0) as client:  # Aumenta o tempo limite para 120 segundos
        response = await client.get(url, headers=headers, params=query)

    if response.status_code == 200:
        data = response.json()
        filtered_data = []
        project_count = 0

        field_names = [
            'CARTEIRA DEMANDANTE',
            'E-MAIL',
            'ESCOPO',
            'OBS',
            'OBJETIVO DO GANHO',
            'KPI GANHO',
            '💡 TIPO DE PROJETO',
            'TIPO DE PROJETO',
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

        for task in data['tasks']:
            project_count += 1

            filtered_task = {
                'Projeto': project_count,
                'ID': task['id'],
                'Status': task['status']['status'],
                'Name': task['name'],
            }

            # Extraindo usernames dos assignees
            if 'assignees' in task:
                usernames = [assignee['username'] for assignee in task['assignees']]
                filtered_task['Líder'] = ', '.join(usernames)

            task_text = task['text_content'].replace('\n', ' ').replace('.:', '')

            field_values = {field: "" for field in field_names}

            for field_name in field_names:
                pattern = re.compile(rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in field_names])})\s*:|$)', re.IGNORECASE)
                match = pattern.search(task_text)
                if match:
                    field_value = match.group(1).strip() 
                    field_values[field_name] = field_value 

            filtered_task.update(field_values)

            if '💡 TIPO DE PROJETO' in filtered_task and '💡 R$ ANUAL (PREVISTO)' in filtered_task['💡 TIPO DE PROJETO']:
                tipo_projeto_value = filtered_task['💡 TIPO DE PROJETO']
                tipo_projeto_parts = tipo_projeto_value.split('💡 R$ ANUAL (PREVISTO)')
                filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[0].strip()
                filtered_task['💡 R$ ANUAL (PREVISTO)'] = tipo_projeto_parts[1].strip()

            filtered_data.append(filtered_task)

        return filtered_data
    else:
        raise HTTPException(
            status_code=400,
            detail=f'Erro ao fazer a solicitação. Código de status: {response.status_code}',
        )
