import os
import re
from datetime import datetime

import httpx
import pytz
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

brt_zone = pytz.timezone('America/Sao_Paulo')

load_dotenv()
app = FastAPI()

# Utilize variáveis de ambiente para a chave de API
API_KEY = os.getenv('CLICKUP_API_KEY')

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

FIELD_PATTERNS = {
    field_name: re.compile(
        rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in FIELD_NAMES])})\s*:|$)',
        re.IGNORECASE,
    )
    for field_name in FIELD_NAMES
}


@app.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    """
    Retrieve and organize data from ClickUp API.
    """
    # Validação do list_id
    if not list_id.isalnum():
        raise HTTPException(status_code=400, detail='ID da lista inválido.')

    try:
        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        query = {'archived': 'false', 'include_markdown_description': 'true'}
        headers = {'Authorization': API_KEY}

        async with httpx.AsyncClient(
            timeout=180.0
        ) as client:  # Timeout reduzido
            response = await client.get(url, headers=headers, params=query)

        if response.status_code != 200:
            error_detail = f'Erro ao fazer a solicitação. Código de status: {response.status_code}'
            raise HTTPException(status_code=400, detail=error_detail)

        data = response.json()
        filtered_data = []

        for project_count, task in enumerate(data.get('tasks', []), start=1):
            try:
                filtered_task = {
                    'Projeto': project_count,
                    'ID': task['id'],
                    'Status': task['status'].get('status', ''),
                    'Name': task.get('name', ''),
                    'Priority': task.get('priority', {}).get('priority', None)
                    if task.get('priority')
                    else None,
                    'Líder': task.get('assignees', [{}])[0].get('username')
                    if task.get('assignees')
                    else None,
                    'Email líder': task.get('assignees', [{}])[0].get('email')
                    if task.get('assignees')
                    else None,
                    'date_created': datetime.utcfromtimestamp(
                        int(task['date_created']) / 1000
                    )
                    .replace(tzinfo=pytz.utc)
                    .astimezone(brt_zone)
                    .strftime('%d-%m-%Y %H:%M:%S'),
                    'date_updated': datetime.utcfromtimestamp(
                        int(task['date_updated']) / 1000
                    )
                    .replace(tzinfo=pytz.utc)
                    .astimezone(brt_zone)
                    .strftime('%d-%m-%Y %H:%M:%S'),
                }

                task_text = (
                    task.get('text_content', '')
                    .replace('\n', ' ')
                    .replace('.:', '')
                )
                field_values = {field: '' for field in FIELD_NAMES}

                for field_name in FIELD_NAMES:
                    pattern = FIELD_PATTERNS[field_name]
                    match = pattern.search(task_text)
                    if match:
                        field_values[field_name] = match.group(1).strip()

                filtered_task.update(field_values)

                if (
                    '💡 TIPO DE PROJETO' in filtered_task
                    and '💡 R$ ANUAL (PREVISTO)'
                    in filtered_task['💡 TIPO DE PROJETO']
                ):
                    tipo_projeto_value = filtered_task['💡 TIPO DE PROJETO']
                    tipo_projeto_parts = tipo_projeto_value.split(
                        '💡 R$ ANUAL (PREVISTO)'
                    )
                    filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[
                        0
                    ].strip()
                    filtered_task[
                        '💡 R$ ANUAL (PREVISTO)'
                    ] = tipo_projeto_parts[1].strip()

                filtered_data.append(filtered_task)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f'Erro ao processar uma tarefa: {str(e)}',
                )

        return filtered_data
    except httpx.HTTPError as http_err:
        raise HTTPException(
            status_code=500,
            detail=f'Erro na solicitação HTTP: {str(http_err)}',
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Erro desconhecido: {str(e)}',
        )