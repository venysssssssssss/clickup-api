import asyncio
import logging
from typing import Dict, List, Union

import httpx
from fastapi import HTTPException

from src.utils.date_utils import parse_date
from src.utils.task_utils import filter_tasks
from src.utils.time_utils import fetch_time_in_status
#ok
logger = logging.getLogger(__name__)


class ClickUpAPI:
    def __init__(self, api_key: str, timezone: str, redis_cache):
        if not api_key:
            raise ValueError('API key must be provided')

        self.api_key = api_key
        self.timezone = timezone
        self.headers = {'Authorization': api_key}
        self.semaphore = asyncio.Semaphore(10)
        self.cache = redis_cache

    async def fetch_clickup_data(self, url: str, query: Dict) -> Dict:
        try:
            async with self.semaphore, httpx.AsyncClient(
                timeout=120.0
            ) as client:
                response = await client.get(
                    url, headers=self.headers, params=query
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, detail=f'HTTP error: {str(e)}'
            )

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
        return tasks

    async def fetch_all_time_in_status(self, tasks: List[Dict]) -> None:
        async with httpx.AsyncClient() as client:
            tasks_with_time_in_status = await asyncio.gather(
                *[
                    fetch_time_in_status(task['id'], client, self.headers)
                    for task in tasks
                    if 'id' in task
                ]
            )
            for task, time_in_status in zip(tasks, tasks_with_time_in_status):
                task['time_in_status'] = time_in_status

    async def get_tasks(
        self, list_id: str
    ) -> List[Dict[str, Union[str, None]]]:
        cache_key = f'tasks_{list_id}'
        cached_tasks = self.cache.get(cache_key)
        if cached_tasks:
            logger.info('Using cached data')
            return cached_tasks

        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        query = {
            'archived': 'false',
            'include_markdown_description': 'true',
            'page_size': 100,
        }  # Use a page size if supported
        tasks = await self.fetch_all_tasks(url, query)
        await self.fetch_all_time_in_status(tasks)
        valid_tasks = [task for task in tasks if 'id' in task]
        self.cache.set(cache_key, valid_tasks)
        return valid_tasks
