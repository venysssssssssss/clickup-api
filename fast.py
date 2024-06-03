import os
import re
from datetime import datetime

import httpx
import pytz
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# Load environment variables
load_dotenv()

# Set up FastAPI
app = FastAPI()

# Set up timezone
brt_zone = pytz.timezone('America/Sao_Paulo')

# Utilize environment variables for the API key
API_KEY = os.getenv('CLICKUP_API_KEY')

# Compile regular expressions once for reuse
FIELD_NAMES = [
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

FIELD_PATTERNS = {
    field_name: re.compile(
        rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in FIELD_NAMES])})\s*:|$)',
        re.IGNORECASE,
    )
    for field_name in FIELD_NAMES
}

async def fetch_clickup_data(url, headers, query):
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.get(url, headers=headers, params=query)
        response.raise_for_status()
        return response.json()

def parse_task_text(task_text):
    return task_text.replace('\n', ' ').replace('.:', '')

def parse_date(timestamp):
    return datetime.utcfromtimestamp(int(timestamp) / 1000).replace(tzinfo=pytz.utc).astimezone(brt_zone).strftime('%d-%m-%Y %H:%M:%S')

def extract_field_values(task_text):
    field_values = {field: '' for field in FIELD_NAMES}
    for field_name in FIELD_NAMES:
        pattern = FIELD_PATTERNS[field_name]
        match = pattern.search(task_text)
        if match:
            field_values[field_name] = match.group(1).strip()
    return field_values

@app.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    """
    Retrieve and organize data from ClickUp API.
    """
    if not list_id.isalnum():
        raise HTTPException(status_code=400, detail='Invalid list ID.')

    try:
        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        query = {'archived': 'false', 'include_markdown_description': 'true'}
        headers = {'Authorization': API_KEY}

        filtered_data = []
        page = 0
        while True:
            query['page'] = page
            data = await fetch_clickup_data(url, headers, query)
            tasks = data.get('tasks', [])
            if not tasks:
                break

            for project_count, task in enumerate(tasks, start=1 + page * 100):
                try:
                    filtered_task = {
                        'Projeto': project_count,
                        'ID': task['id'],
                        'Status': task['status'].get('status', ''),
                        'Name': task.get('name', ''),
                        'Priority': task.get('priority', {}).get('priority', None) if task.get('priority') else None,
                        'Líder': task.get('assignees', [{}])[0].get('username') if task.get('assignees') else None,
                        'Email líder': task.get('assignees', [{}])[0].get('email') if task.get('assignees') else None,
                        'date_created': parse_date(task['date_created']),
                        'date_updated': parse_date(task['date_updated']),
                    }

                    task_text = parse_task_text(task.get('text_content', ''))
                    field_values = extract_field_values(task_text)
                    filtered_task.update(field_values)

                    if ('💡 TIPO DE PROJETO' in filtered_task) and ('💡 R$ ANUAL (PREVISTO)' in filtered_task['💡 TIPO DE PROJETO']):
                        tipo_projeto_value = filtered_task['💡 TIPO DE PROJETO']
                        tipo_projeto_parts = tipo_projeto_value.split('💡 R$ ANUAL (PREVISTO)')
                        filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[0].strip()
                        filtered_task['💡 R$ ANUAL (PREVISTO)'] = tipo_projeto_parts[1].strip()

                    filtered_data.append(filtered_task)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f'Error processing a task: {str(e)}')

            page += 1

        return filtered_data
    except httpx.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f'HTTP error: {str(http_err)}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unknown error: {str(e)}')
