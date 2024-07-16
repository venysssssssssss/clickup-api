```python
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Union

import httpx
import pytz
from fastapi import HTTPException
import logging

from src.utils.regex_utils import FIELD_NAMES_SET, FIELD_PATTERNS

logger = logging.getLogger(__name__)

class ClickUpAPI:
    def __init__(self, api_key: str, timezone: str, redis_cache):
        """
        Inicializa a classe ClickUpAPI com a chave de API, fuso horário e cache Redis.

        Args:
            api_key (str): Chave de API para autenticação.
            timezone (str): Fuso horário para conversão de datas.
            redis_cache: Instância de cache Redis para armazenamento temporário.
        """
        if not api_key:
            raise ValueError('API key must be provided')

        self.api_key = api_key
        self.timezone = pytz.timezone(timezone)
        self.headers = {'Authorization': api_key}
        self.semaphore = asyncio.Semaphore(10)
        self.cache = redis_cache

    async def fetch_clickup_data(self, url: str, query: Dict) -> Dict:
        """
        Realiza uma requisição assíncrona para obter dados da API do ClickUp.

        Args:
            url (str): URL da API.
            query (Dict): Parâmetros da consulta.

        Returns:
            Dict: Dados da resposta da API.
        """
        try:
            async with self.semaphore, httpx.AsyncClient(
                timeout=60.0
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
        """
        Busca todas as tarefas paginadas da API do ClickUp.

        Args:
            url (str): URL da API para busca de tarefas.
            query (Dict): Parâmetros da consulta.

        Returns:
            List[Dict]: Lista de todas as tarefas encontradas.
        """
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

    async def fetch_time_in_status(
        self, task_id: str, client: httpx.AsyncClient
    ) -> Dict:
        """
        Obtém o tempo em status de uma tarefa específica.

        Args:
            task_id (str): ID da tarefa.
            client (httpx.AsyncClient): Cliente HTTP assíncrono para requisições.

        Returns:
            Dict: Dados do tempo em status da tarefa.
        """
        url = f'https://api.clickup.com/api/v2/task/{task_id}/time_in_status'
        response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def fetch_all_time_in_status(self, tasks: List[Dict]) -> None:
        """
        Busca o tempo em status de todas as tarefas fornecidas.

        Args:
            tasks (List[Dict]): Lista de tarefas.

        """
        async with httpx.AsyncClient() as client:
            tasks_with_time_in_status = await asyncio.gather(
                *[
                    self.fetch_time_in_status(task['id'], client)
                    for task in tasks
                    if 'id' in task
                ]
            )
            for task, time_in_status in zip(tasks, tasks_with_time_in_status):
                task['time_in_status'] = time_in_status

    def filter_tasks(
        self, tasks: List[Dict]
    ) -> (List[Dict], List[Dict]):   # type: ignore
        """
        Filtra as tarefas para extrair dados relevantes e histórico de status.

        Args:
            tasks (List[Dict]): Lista de tarefas a serem filtradas.

        Returns:
            Tuple[List[Dict], List[Dict]]: Dados filtrados das tarefas e histórico de status.
        """
        filtered_data = []
        status_history_data = []
        for project_count, task in enumerate(tasks, start=1):
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
                    'date_created': self.parse_date(task['date_created']),
                    'date_updated': self.parse_date(task['date_updated']),
                }

                task_text = self.parse_task_text(task.get('text_content', ''))
                field_values = self.extract_field_values(task_text)
                filtered_task.update(field_values)

                filtered_data.append(filtered_task)

                status_history = self.convert_status_history(
                    task.get('time_in_status', {})
                )
                for entry in status_history.get('status_history', []):
                    status_history_data.append(
                        {
                            'task_id': task['id'],
                            'status': entry['status'],
                            'time_in_status': entry['time_in_status'],
                            'timestamp': datetime.now(self.timezone),
                        }
                    )
            except KeyError as e:
                logger.error(f"Missing key {e} in task {task}")
                continue

        return filtered_data, status_history_data

    def parse_date(self, timestamp: int) -> str:
        """
        Converte um timestamp em milissegundos para uma string de data formatada.

        Args:
            timestamp (int): Timestamp em milissegundos.

        Returns:
            str: String formatada da data.
        """
        return (
            datetime.utcfromtimestamp(int(timestamp) / 1000)
            .replace(tzinfo=pytz.utc)
            .astimezone(self.timezone)
            .strftime('%d-%m-%Y %H:%M:%S')
        )

    @staticmethod
    def convert_time(time_in_minutes: int) -> str:
        """
        Converte o tempo em minutos para uma string formatada.

        Args:
            time_in_minutes (int): Tempo em minutos.

        Returns:
            str: String formatada do tempo.
        """
        if time_in_minutes < 60:
            return f'{time_in_minutes} minutos'
        elif time_in_minutes < 1440:
            hours = time_in_minutes / 60
            return f'{hours:.1f} horas'
        else:
            days = time_in_minutes / 1440
            return f'{days:.1f} dias'

    @staticmethod
    def parse_task_text(task_text: str) -> str:
        """
        Remove caracteres especiais do texto da tarefa.

        Args:
            task_text (str): Texto da tarefa.

        Returns:
            str: Texto da tarefa limpo.
        """
        return (
            task_text.replace('\n', ' ').replace('.:', '') if task_text else ''
        )

    @staticmethod
    def extract_field_values(task_text: str) -> Dict[str, str]:
        """
        Extrai valores dos campos especificados no texto da tarefa.

        Args:
            task_text (str): Texto da tarefa.

        Returns:
            Dict[str, str]: Dicionário com valores dos campos extraídos.
        """
        field_values = {field: '' for field in FIELD_NAMES_SET}
        for field_name in FIELD_NAMES_SET:
            pattern = FIELD_PATTERNS[field_name]
            match = pattern.search(task_text)
            if match:
                field_values[field_name] = match.group(1).strip()
        return field_values

    def convert_status_history(self, status_history: Dict) -> Dict:
        """
        Converte o histórico de status de uma tarefa para um formato mais legível.

        Args:
            status_history (Dict): Histórico de status da tarefa.

        Returns:
            Dict: Histórico de status convertido.
        """
        result = {}
        if (
            'current_status' in status_history
            and 'total_time' in status_history['current_status']
        ):
            result['current_status'] = {
                'status': status_history['current_status']['status'],
                'time_in_status': self.convert_time(
                    status_history['current_status']['total_time']['by_minute']
                ),
            }
        if 'status_history' in status_history:
            result['status_history'] = [
                {
                    'status': status['status'],
                    'time_in_status': self.convert_time(
                        status['total_time']['by_minute']
                    ),
                }
                for status in status_history['status_history']
                if 'total_time' in status
            ]
        return result

    async def get_tasks(
        self, list_id: str
    ) -> List[Dict[str, Union[str, None]]]:
        """
        Obtém todas as tarefas de uma lista específica.

        Args:
            list_id (str): ID da lista de tarefas.

        Returns:
            List[Dict[str, Union[str, None]]]: Lista de tarefas encontradas.
        """
        cache_key = f'tasks_{list_id}'
        cached_tasks = self.cache.get(cache_key)
        if cached_tasks:
            print('Using cached data')
            return cached_tasks

        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        query = {
            'archived': 'false',
            'include_markdown_description': 'true',
        }
        tasks = await self.fetch_all_tasks(url, query)
        await self.fetch_all_time_in_status(tasks)
        valid_tasks = [task for task in tasks if 'id' in task]  # Ensure all tasks have 'id' before caching
        self.cache.set(cache_key, valid_tasks)
        return valid_tasks
