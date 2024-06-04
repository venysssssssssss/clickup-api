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

# Compile regular expressions once for reuse
FIELD_PATTERNS = {
    field_name: re.compile(
        rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in FIELD_NAMES])})\s*:|$)',
        re.IGNORECASE,
    )
    for field_name in FIELD_NAMES
}

async def fetch_clickup_data(url, headers, query):
    """
    Fetches data from the ClickUp API.

    Args:
        url (str): The URL of the API endpoint.
        headers (dict): The headers to be included in the request.
        query (dict): The query parameters to be included in the request.

    Returns:
        dict: The JSON response from the API.

    Raises:
        HTTPException: If there is an HTTP error while making the API request.
    """
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.get(url, headers=headers, params=query)
        response.raise_for_status()
        return response.json()

def parse_task_text(task_text):
    """
    Parses the given task text by replacing newline characters with spaces and removing '.:' characters.

    Args:
        task_text (str): The task text to be parsed.

    Returns:
        str: The parsed task text.
    """
    if task_text is None:
        return ''
    return task_text.replace('\n', ' ').replace('.:', '')


def parse_date(timestamp):
    """
    Parses a timestamp and converts it to a formatted date string.

    Args:
        timestamp (int): The timestamp to parse.

    Returns:
        str: The formatted date string.

    """
    return datetime.utcfromtimestamp(int(timestamp) / 1000).replace(tzinfo=pytz.utc).astimezone(brt_zone).strftime('%d-%m-%Y %H:%M:%S')

def extract_field_values(task_text):
    """
    Extracts field values from the given task text.

    Args:
        task_text (str): The text of the task.

    Returns:
        dict: A dictionary containing field names as keys and their corresponding values as values.
    """
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

    Parameters:
    - list_id (str): The ID of the ClickUp list.

    Returns:
    - filtered_data (list): A list of dictionaries containing the filtered and organized data.

    Raises:
    - HTTPException: If the list ID is invalid or if there is an error processing a task.
    - HTTPException: If there is an HTTP error while making the API request.
    - HTTPException: If there is an unknown error.

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
