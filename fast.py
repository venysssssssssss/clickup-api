import re
import httpx
from fastapi import FastAPI, HTTPException
from datetime import datetime

app = FastAPI()

@app.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    """
    Retrieve and organize data from ClickUp API.

    Args:
        list_id (str): The ID of the ClickUp list.

    Returns:
        list: A list of dictionaries containing the filtered data.
    """
    url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
    query = {'archived': 'false', 'include_markdown_description': 'true'}
    headers = {'Authorization': 'pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2'}

    async with httpx.AsyncClient(timeout=140.0) as client:
        response = await client.get(url, headers=headers, params=query)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f'Erro ao fazer a solicitação. Código de status: {response.status_code}')

    data = response.json()
    filtered_data = []
    field_names = [
        'CARTEIRA DEMANDANTE', 'E-MAIL', 'ESCOPO', 'OBS', 'OBJETIVO DO GANHO',
        'KPI GANHO', '💡 TIPO DE PROJETO', 'TIPO DE PROJETO', 'TIPO DE OPERAÇÃO',
        'PRODUTO', 'OPERAÇÃO', 'SITE', 'UNIDADE DE NEGÓCIO', 'DIRETOR TAHTO',
        'CLIENTE', 'TIPO', '💡 R$ ANUAL (PREVISTO)', 'GERENTE OI', 'FERRAMENTA ENVOLVIDA',
        'CENÁRIO PROPOSTO',
    ]

    for project_count, task in enumerate(data['tasks'], start=1):
        filtered_task = {
            'Projeto': project_count,
            'ID': task['id'],
            'Status': task['status']['status'],
            'Name': task['name'],
            'Priority': task.get('priority', {}).get('priority') if task.get('priority') is not None else None,
            'Líder': task.get('assignees', [{}])[0].get('username') if task.get('assignees') else None,
            'Email líder': task.get('assignees', [{}])[0].get('email') if task.get('assignees') else None,
            'date_created': datetime.utcfromtimestamp(int(task['date_created']) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            'date_updated': datetime.utcfromtimestamp(int(task['date_updated']) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
        }

        task_text = task['text_content'].replace('\n', ' ').replace('.:', '')
        field_values = {field: '' for field in field_names}

        for field_name in field_names:
            pattern = re.compile(
                rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in field_names])})\s*:|$)',
                re.IGNORECASE,
            )
            match = pattern.search(task_text)
            if match:
                field_values[field_name] = match.group(1).strip()

        filtered_task.update(field_values)

        if '💡 TIPO DE PROJETO' in filtered_task and '💡 R$ ANUAL (PREVISTO)' in filtered_task['💡 TIPO DE PROJETO']:
            tipo_projeto_value = filtered_task['💡 TIPO DE PROJETO']
            tipo_projeto_parts = tipo_projeto_value.split('💡 R$ ANUAL (PREVISTO)')
            filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[0].strip()
            filtered_task['💡 R$ ANUAL (PREVISTO)'] = tipo_projeto_parts[1].strip()

        filtered_data.append(filtered_task)

    return filtered_data
