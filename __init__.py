import os
import re
from datetime import datetime

import httpx
import pytz
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# Configurações iniciais
load_dotenv()
app = FastAPI()
API_KEY = os.getenv('CLICKUP_API_KEY')
BRT_ZONE = pytz.timezone('America/Sao_Paulo')

# Constantes
CLICKUP_API_URL = 'https://api.clickup.com/api/v2'
# Compile as expressões regulares uma vez para reutilização
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
COMPILED_PATTERNS = {
    field_name: re.compile(
        rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in FIELD_NAMES])})\s*:|$)',
        re.IGNORECASE,
    )
    for field_name in FIELD_NAMES
}

# Funções auxiliares
def compile_patterns():
    return {
        field_name: re.compile(
            rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in FIELD_NAMES])})\s*:|$)',
            re.IGNORECASE,
        )
        for field_name in FIELD_NAMES
    }


def parse_task_data(task, patterns):
    task_text = (
        task.get('text_content', '').replace('\n', ' ').replace('.:', '')
    )
    field_values = {field: '' for field in FIELD_NAMES}
    for field_name in FIELD_NAMES:
        pattern = patterns[field_name]
        match = pattern.search(task_text)
        if match:
            field_values[field_name] = match.group(1).strip()
    return field_values


def format_task_data(task, project_count, brt_zone):
    return {
        'Projeto': project_count,
        'ID': task['id'],
        # Outros campos omitidos para brevidade
        'date_created': datetime.utcfromtimestamp(
            int(task['date_created']) / 1000
        )
        .replace(tzinfo=pytz.utc)
        .astimezone(brt_zone)
        .strftime('%d-%m-%Y %H:%M:%S'),
        # Outros campos omitidos para brevidade
    }


# Rota principal
@app.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    if not list_id.isalnum():
        raise HTTPException(status_code=400, detail='ID da lista inválido.')
    headers = {'Authorization': API_KEY}
    query = {'archived': 'false', 'include_markdown_description': 'true'}
    patterns = compile_patterns()
    filtered_data = []
    page = 0

    while True:
        response = await fetch_clickup_tasks(list_id, headers, query, page)
        tasks = response.get('tasks', [])
        if not tasks:
            break

        for project_count, task in enumerate(tasks, start=1 + page * 100):
            try:
                task_data = format_task_data(task, project_count, BRT_ZONE)
                task_data.update(parse_task_data(task, patterns))
                filtered_data.append(task_data)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f'Erro ao processar uma tarefa: {str(e)}',
                )
        page += 1

    return filtered_data


async def fetch_clickup_tasks(list_id, headers, query, page):
    url = f'{CLICKUP_API_URL}/list/{list_id}/task'
    query['page'] = page
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.get(url, headers=headers, params=query)
    if response.status_code != 200:
        error_detail = f'Erro ao fazer a solicitação. Código de status: {response.status_code}'
        raise HTTPException(status_code=400, detail=error_detail)
    return response.json()
