import asyncio
from datetime import datetime
from typing import Dict, List, Union

import httpx
import pytz
from fastapi import HTTPException

from utils.regex_utils import FIELD_NAMES, FIELD_PATTERNS

FIELD_NAMES_SET = set(
    FIELD_NAMES
)  # Convert FIELD_NAMES to a set for faster lookups


class ClickUpAPI:
    def __init__(self, api_key: str, timezone: str):
        self.api_key = api_key
        self.timezone = pytz.timezone(timezone)
        self.headers = {'Authorization': api_key}
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent tasks to 10

    async def fetch_clickup_data(
        self, url: str, query: Dict, retries: int = 3
    ) -> Dict:
        attempt = 0
        while attempt < retries:
            try:
                async with self.semaphore, httpx.AsyncClient(
                    timeout=180.0
                ) as client:
                    response = await client.get(
                        url, headers=self.headers, params=query
                    )
                    response.raise_for_status()
                    return response.json()
            except httpx.RequestError as e:
                attempt += 1
                if attempt >= retries:
                    raise HTTPException(
                        status_code=500, detail=f'HTTP error: {str(e)}'
                    )
                await asyncio.sleep(2**attempt)  # Exponential backoff

    async def fetch_all_tasks(
        self, url: str, query: Dict, start_page: int, end_page: int
    ) -> List[Dict]:
        tasks = []
        for page in range(start_page, end_page):
            query['page'] = page
            data = await self.fetch_clickup_data(url, query)
            tasks.extend(data.get('tasks', []))
            await asyncio.sleep(
                1
            )  # Add a delay between requests to avoid hitting the rate limit
        return tasks

    def parse_task_text(self, task_text: str) -> str:
        return (
            task_text.replace('\n', ' ').replace('.:', '') if task_text else ''
        )

    def parse_date(self, timestamp: int) -> str:
        return (
            datetime.utcfromtimestamp(int(timestamp) / 1000)
            .replace(tzinfo=pytz.utc)
            .astimezone(self.timezone)
            .strftime('%d-%m-%Y %H:%M:%S')
        )

    def extract_field_values(self, task_text: str) -> Dict[str, str]:
        field_values = {
            field: '' for field in FIELD_NAMES_SET
        }  # Use the set for initialization
        for field_name in FIELD_NAMES_SET:  # Iterate over the set
            pattern = FIELD_PATTERNS[field_name]
            match = pattern.search(task_text)
            if match:
                field_values[field_name] = match.group(1).strip()
        return field_values

    async def get_tasks(
        self, list_id: str
    ) -> List[Dict[str, Union[str, None]]]:
        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        initial_query = {
            'archived': 'false',
            'include_markdown_description': 'true',
            'page_size': 100,
        }

        # Define the date range for 2024
        start_date_2024 = int(
            datetime(2024, 1, 1).timestamp() * 1000
        )  # Start of 2024 in milliseconds
        end_date_2024 = int(
            datetime(2024, 12, 31, 23, 59, 59).timestamp() * 1000
        )  # End of 2024 in milliseconds

        if list_id == '192943568':
            initial_query.update(
                {
                    'include_closed': 'true',
                    'page_size': 1000,
                    'due_date_gt': start_date_2024,
                    'due_date_lt': end_date_2024,
                }
            )

        tasks = []
        page = 0
        while True:
            batch = await self.fetch_all_tasks(
                url, initial_query, page, page + 1
            )
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
                if task.get('priority')
                else None,
                'Líder': task.get('assignees', [{}])[0].get('username')
                if task.get('assignees')
                else None,
                'Email líder': task.get('assignees', [{}])[0].get('email')
                if task.get('assignees')
                else None,
                'date_created': self.parse_date(task['date_created']),
                'date_updated': self.parse_date(task['date_updated']),
            }

            task_text = self.parse_task_text(task.get('text_content', ''))
            field_values = self.extract_field_values(task_text)
            filtered_task.update(field_values)

            tipo_projeto = filtered_task.get('💡 TIPO DE PROJETO', '')
            if '💡 R$ ANUAL (PREVISTO)' in tipo_projeto:
                tipo_projeto_parts = tipo_projeto.split(
                    '💡 R$ ANUAL (PREVISTO)'
                )
                filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[
                    0
                ].strip()
                filtered_task['💡 R$ ANUAL (PREVISTO)'] = tipo_projeto_parts[
                    1
                ].strip()

            filtered_data.append(filtered_task)

        return filtered_data
