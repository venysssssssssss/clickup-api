import os
import re
from datetime import datetime
import asyncio
from typing import List, Dict, Union

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


class ClickUpAPI:
    def __init__(self, api_key: str, timezone: str):
        self.api_key = api_key
        self.timezone = pytz.timezone(timezone)
        self.headers = {'Authorization': api_key}
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent tasks to 10

    async def fetch_clickup_data(self, url: str, query: Dict, retries: int = 3) -> Dict:
        attempt = 0
        while attempt < retries:
            try:
                async with self.semaphore, httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.get(url, headers=self.headers, params=query)
                    response.raise_for_status()
                    return response.json()
            except httpx.RequestError as e:
                attempt += 1
                if attempt >= retries:
                    raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def fetch_all_tasks(self, url: str, initial_query: Dict, start_page: int, end_page: int) -> List[Dict]:
        tasks = []
        for page in range(start_page, end_page):
            query = initial_query.copy()
            query['page'] = page
            data = await self.fetch_clickup_data(url, query)
            tasks.extend(data.get('tasks', []))
        return tasks

    def parse_task_text(self, task_text: str) -> str:
        if task_text is None:
            return ''
        return task_text.replace('\n', ' ').replace('.:', '')

    def parse_date(self, timestamp: int) -> str:
        return (
            datetime.utcfromtimestamp(int(timestamp) / 1000)
            .replace(tzinfo=pytz.utc)
            .astimezone(self.timezone)
            .strftime('%d-%m-%Y %H:%M:%S')
        )

    def extract_field_values(self, task_text: str) -> Dict[str, str]:
        field_values = {field: '' for field in FIELD_NAMES}
        for field_name in FIELD_NAMES:
            pattern = FIELD_PATTERNS[field_name]
            match = pattern.search(task_text)
            if match:
                field_values[field_name] = match.group(1).strip()
        return field_values

    async def get_tasks(self, list_id: str) -> List[Dict[str, Union[str, None]]]:
        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        initial_query = {
            'archived': 'false',
            'include_markdown_description': 'true',
        }

        if list_id == '192943568':

            initial_query.update({'include_closed': "true"})
            # Specific logic for large list ID 192943568
            tasks = await asyncio.gather(*[
                self.fetch_all_tasks(url, initial_query, i, i + 10)
                for i in range(0, 4600, 10)
            ])
            tasks = [task for sublist in tasks for task in sublist]  # Flatten the list
        else:
            tasks = []
            page = 0
            while True:
                initial_query['page'] = page
                data = await self.fetch_clickup_data(url, initial_query)
                batch = data.get('tasks', [])
                if not batch:
                    break
                tasks.extend(batch)
                page += 1

        return tasks

    def filter_tasks(self, tasks: List[Dict]) -> List[Dict]:
        filtered_data = []

        for project_count, task in enumerate(tasks, start=1):
            filtered_task = {
                'Projeto': project_count,
                'ID': task['id'],
                'Status': task['status'].get('status', ''),
                'Name': task.get('name', ''),
                'Priority': task.get('priority', {}).get('priority', None)
                if task.get('priority') else None,
                'Líder': task.get('assignees', [{}])[0].get('username')
                if task.get('assignees') else None,
                'Email líder': task.get('assignees', [{}])[0].get('email')
                if task.get('assignees') else None,
                'date_created': self.parse_date(task['date_created']),
                'date_updated': self.parse_date(task['date_updated']),
            }

            task_text = self.parse_task_text(task.get('text_content', ''))
            field_values = self.extract_field_values(task_text)
            filtered_task.update(field_values)

            if ('💡 TIPO DE PROJETO' in filtered_task) and (
                '💡 R$ ANUAL (PREVISTO)' in filtered_task['💡 TIPO DE PROJETO']
            ):
                tipo_projeto_value = filtered_task['💡 TIPO DE PROJETO']
                tipo_projeto_parts = tipo_projeto_value.split('💡 R$ ANUAL (PREVISTO)')
                filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[0].strip()
                filtered_task['💡 R$ ANUAL (PREVISTO)'] = tipo_projeto_parts[1].strip()

            filtered_data.append(filtered_task)

        return filtered_data


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
        clickup_api = ClickUpAPI(api_key=API_KEY, timezone='America/Sao_Paulo')
        tasks = await clickup_api.get_tasks(list_id)
        filtered_data = clickup_api.filter_tasks(tasks)
        return filtered_data
    except httpx.HTTPError as http_err:
        raise HTTPException(
            status_code=500, detail=f'HTTP error: {str(http_err)}'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unknown error: {str(e)}')
