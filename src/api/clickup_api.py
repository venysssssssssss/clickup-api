import asyncio
from typing import Dict, List, Union
import httpx
from fastapi import HTTPException
from src.utils.time_utils import parse_date, convert_time
from src.utils.text_utils import parse_task_text, extract_field_values
from src.cache.redis_cache import RedisCache

class ClickUpAPI:
    def __init__(self, api_key: str, timezone: str, redis_cache: RedisCache):
        self.api_key = api_key
        self.timezone = timezone
        self.headers = {'Authorization': api_key}
        self.semaphore = asyncio.Semaphore(10)
        self.cache = redis_cache

    async def fetch_clickup_data(self, url: str, query: Dict) -> Dict:
        try:
            async with self.semaphore, httpx.AsyncClient(timeout=180.0) as client:
                response = await client.get(url, headers=self.headers, params=query)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f'HTTP error: {str(e)}')

    async def fetch_all_tasks(self, url: str, query: Dict) -> List[Dict]:
        tasks = []
        page = 0
        while True:
            query['page'] = page
            data = await self.fetch_clickup_data(url, query)
            page_tasks = data.get('tasks', [])
            if not page_tasks:
                break
            tasks.extend(page_tasks)
            page += 1
            await asyncio.sleep(1)
        return tasks

    async def fetch_time_in_status(self, task_id: str) -> Dict:
        url = f"https://api.clickup.com/api/v2/task/{task_id}/time_in_status"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_tasks(self, list_id: str) -> List[Dict[str, Union[str, None]]]:
        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        query = {
            'archived': 'false',
            'include_markdown_description': 'true',
        }
        tasks = await self.fetch_all_tasks(url, query)
        for task in tasks:
            time_in_status = await self.fetch_time_in_status(task['id'])
            task['time_in_status'] = time_in_status
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
                'date_created': parse_date(task['date_created'], self.timezone),
                'date_updated': parse_date(task['date_updated'], self.timezone),
                'Status History': self.convert_status_history(task.get('time_in_status', {}))
            }

            task_text = parse_task_text(task.get('text_content', ''))
            field_values = extract_field_values(task_text)
            filtered_task.update(field_values)

            filtered_data.append(filtered_task)
        return filtered_data

    def convert_status_history(self, status_history: Dict) -> Dict:
        result = {}
        if 'current_status' in status_history and 'total_time' in status_history['current_status']:
            result['current_status'] = {
                'status': status_history['current_status']['status'],
                'time_in_status': convert_time(status_history['current_status']['total_time']['by_minute'])
            }
        if 'status_history' in status_history:
            result['status_history'] = [
                {
                    'status': status['status'],
                    'time_in_status': convert_time(status['total_time']['by_minute'])
                } for status in status_history['status_history'] if 'total_time' in status
            ]
        return result
