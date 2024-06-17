import asyncio
import json
from datetime import datetime
from typing import Dict, List, Union

import httpx
import msgpack  # Importação do pacote MessagePack para serialização eficiente
import pytz
import redis
from fastapi import HTTPException

from utils.regex_utils import FIELD_NAMES, FIELD_PATTERNS

FIELD_NAMES_SET = set(FIELD_NAMES)  # Convert FIELD_NAMES to a set for faster lookups

class ClickUpAPI:
    def __init__(self, api_key: str, timezone: str, redis_url: str):
        self.api_key = api_key
        self.timezone = pytz.timezone(timezone)
        self.headers = {'Authorization': api_key}
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent tasks to 10
        self.redis = redis.StrictRedis.from_url(redis_url)
        self.test_redis_connection()

    def test_redis_connection(self):
        try:
            self.redis.ping()
            print('Successfully connected to Redis')
        except redis.ConnectionError as e:
            print(f'Failed to connect to Redis: {e}')
            raise HTTPException(status_code=500, detail=f'Failed to connect to Redis: {e}')

    def get_from_cache(self, key: str) -> Union[Dict, None]:
        try:
            cached_data = self.redis.hgetall(key)  # Utilização de hashes do Redis para melhorar o acesso
            if cached_data:
                return {field.decode('utf-8'): msgpack.unpackb(value) for field, value in cached_data.items()}
            return None
        except redis.RedisError as e:
            print(f'Redis get error: {e}')
            return None

    def set_in_cache(self, key: str, data: Dict, ttl: int = 600):
        try:
            for field, value in data.items():
                self.redis.hset(key, field, msgpack.packb(value))  # Utilização de MessagePack para serialização eficiente
            self.redis.expire(key, ttl)
        except redis.RedisError as e:
            print(f'Redis set error: {e}')

    async def fetch_clickup_data(self, url: str, query: Dict, retries: int = 3) -> Dict:
        try:
            async with self.semaphore, httpx.AsyncClient(timeout=180.0) as client:
                response = await client.get(url, headers=self.headers, params=query)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f'HTTP error: {str(e)}')

    async def fetch_all_tasks(self, url: str, query: Dict, start_page: int, end_page: int) -> List[Dict]:
        tasks = []
        for page in range(start_page, end_page):
            query['page'] = page
            data = await self.fetch_clickup_data(url, query)
            tasks.extend(data.get('tasks', []))
            await asyncio.sleep(1)  # Add a delay between requests to avoid hitting the rate limit
        return tasks

    def parse_task_text(self, task_text: str) -> str:
        return task_text.replace('\n', ' ').replace('.:', '') if task_text else ''

    def parse_date(self, timestamp: int) -> str:
        return (datetime.utcfromtimestamp(int(timestamp) / 1000)
                .replace(tzinfo=pytz.utc)
                .astimezone(self.timezone)
                .strftime('%d-%m-%Y %H:%M:%S'))

    def extract_field_values(self, task_text: str) -> Dict[str, str]:
        field_values = {field: '' for field in FIELD_NAMES_SET}  # Use the set for initialization
        for field_name in FIELD_NAMES_SET:  # Iterate over the set
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
            'page_size': 100,
        }

        # Define the date range for 2024
        start_date_2024 = int(datetime(2024, 1, 1).timestamp() * 1000)  # Start of 2024 in milliseconds
        end_date_2024 = int(datetime(2024, 12, 31, 23, 59, 59).timestamp() * 1000)  # End of 2024 in milliseconds

        if list_id == '192943568':
            initial_query.update({
                'include_closed': 'true',
                'page_size': 1000,
                'due_date_gt': start_date_2024,
                'due_date_lt': end_date_2024,
            })

        tasks = []
        page = 0
        while True:
            cache_key = f'{url}_{json.dumps(initial_query, sort_keys=True)}_page_{page}'
            cached_data = self.get_from_cache(cache_key)
            if cached_data:
                print(f"Page {page}: Data fetched from cache")
                tasks.extend(cached_data.get('tasks', []))
            else:
                print(f"Page {page}: Fetching data from API")
                data = await self.fetch_all_tasks(url, initial_query, page, page + 1)
                if not data:
                    break
                tasks.extend(data)
                if page == 0:
                    self.set_in_cache(cache_key, {f'task_{i}': task for i, task in enumerate(data)}, ttl=600)
            page += 1

        # Verificar se os dados do cache estão atualizados
        cache_key = f'{url}_{json.dumps(initial_query, sort_keys=True)}_all'
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            cached_tasks = [task for task in cached_data.values()]
            if len(cached_tasks) == len(tasks):
                print("Using cached tasks")
                return cached_tasks
            else:
                print("Updating cache with new tasks")
                self.set_in_cache(cache_key, {f'task_{i}': task for i, task in enumerate(tasks)}, ttl=600)
        else:
            self.set_in_cache(cache_key, {f'task_{i}': task for i, task in enumerate(tasks)}, ttl=600)

        print(f"Total tasks fetched: {len(tasks)}")
        return tasks

    def filter_tasks(self, tasks: List[Dict]) -> List[Dict]:
        filtered_data = []
        for project_count, task in enumerate(tasks, start=1):
            filtered_task = {
                'Projeto': project_count,
                'ID': task['id'],
                'Status': task['status'].get('status', ''),
                'Name': task.get('name', ''),
                'Priority': task.get('priority', {}).get('priority', None) if task.get('priority') else None,
                'Líder': task.get('assignees', [{}])[0].get('username') if task.get('assignees') else None,
                'Email líder': task.get('assignees', [{}])[0].get('email') if task.get('assignees') else None,
                'date_created': self.parse_date(task['date_created']),
                'date_updated': self.parse_date(task['date_updated']),
            }

            task_text = self.parse_task_text(task.get('text_content', ''))
            field_values = self.extract_field_values(task_text)
            filtered_task.update(field_values)

            tipo_projeto = filtered_task.get('💡 TIPO DE PROJETO', '')
            if '💡 R$ ANUAL (PREVISTO)' in tipo_projeto:
                tipo_projeto_parts = tipo_projeto.split('💡 R$ ANUAL (PREVISTO)')
                filtered_task['💡 TIPO DE PROJETO'] = tipo_projeto_parts[0].strip()
                filtered_task['💡 R$ ANUAL (PREVISTO)'] = tipo_projeto_parts[1].strip()

            filtered_data.append(filtered_task)

        return filtered_data
