import asyncio
import json
from datetime import datetime
from typing import Dict, List, Union
import re

import httpx
import pytz
from fastapi import HTTPException
import logging

from src.utils.regex_utils import FIELD_NAMES_SET, FIELD_PATTERNS

logger = logging.getLogger(__name__)

class ClickUpAPI:
    def __init__(self, api_key: str, timezone: str, redis_cache):
        """
        Inicializa uma instância da classe ClickUpAPI.

        Parâmetros:
        - api_key (str): A chave de API do ClickUp.
        - timezone (str): O fuso horário utilizado para converter as datas.
        - redis_cache: O objeto de cache Redis utilizado para armazenar os dados em cache.
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
        Faz uma requisição assíncrona para a API do ClickUp e retorna os dados em formato JSON.

        Parâmetros:
        - url (str): A URL da API do ClickUp.
        - query (Dict): Os parâmetros da consulta.

        Retorna:
        - Dict: Os dados da resposta em formato JSON.
        """
        try:
            async with self.semaphore, httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=self.headers, params=query)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f'HTTP error: {str(e)}')

    async def fetch_all_tasks(self, url: str, query: Dict) -> List[Dict]:
        """
        Faz uma requisição assíncrona para a API do ClickUp e retorna todas as tarefas.

        Parâmetros:
        - url (str): A URL da API do ClickUp.
        - query (Dict): Os parâmetros da consulta.

        Retorna:
        - List[Dict]: Uma lista de dicionários contendo as informações das tarefas.
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

    async def fetch_time_in_status(self, task_id: str, client: httpx.AsyncClient) -> Dict:
        """
        Faz uma requisição assíncrona para a API do ClickUp e retorna o tempo em cada status de uma tarefa.

        Parâmetros:
        - task_id (str): O ID da tarefa.
        - client (httpx.AsyncClient): O cliente HTTP utilizado para fazer a requisição.

        Retorna:
        - Dict: Os dados do tempo em cada status da tarefa em formato JSON.
        """
        url = f'https://api.clickup.com/api/v2/task/{task_id}/time_in_status'
        response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def fetch_all_time_in_status(self, tasks: List[Dict]) -> None:
        """
        Faz uma requisição assíncrona para a API do ClickUp e retorna o tempo em cada status de todas as tarefas.

        Parâmetros:
        - tasks (List[Dict]): Uma lista de dicionários contendo as informações das tarefas.

        Retorna:
        - None
        """
        async with httpx.AsyncClient() as client:
            tasks_with_time_in_status = await asyncio.gather(
                *[self.fetch_time_in_status(task['id'], client) for task in tasks if 'id' in task]
            )
            for task, time_in_status in zip(tasks, tasks_with_time_in_status):
                task['time_in_status'] = time_in_status

    def filter_tasks(self, tasks: List[Dict]) -> (List[Dict], List[Dict]): # type: ignore
        """
        Filtra as tarefas retornando apenas as informações relevantes e o histórico de status.

        Parâmetros:
        - tasks (List[Dict]): Uma lista de dicionários contendo as informações das tarefas.

        Retorna:
        - Tuple[List[Dict], List[Dict]]: Uma tupla contendo a lista de tarefas filtradas e o histórico de status.
        """
        filtered_data = []
        status_history_data = []
        emoji_pattern = re.compile(
            "["u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE)
        
        for project_count, task in enumerate(tasks, start=1):
            try:
                date_created = self.parse_date(task['date_created'])
                date_updated = self.parse_date(task['date_updated'])

                filtered_task = {
                    'task_id': task['id'],
                    'Status': emoji_pattern.sub(r'', task['status'].get('status', '')),
                    'Name': task.get('name', ''),
                    'Priority': task.get('priority', {}).get('priority', None) if task.get('priority') else None,
                    'Líder': task.get('assignees', [{}])[0].get('username') if task.get('assignees') else None,
                    'Email líder': task.get('assignees', [{}])[0].get('email') if task.get('assignees') else None,
                    'date_created_data': date_created['data'],
                    'date_created_ano': date_created['ano'],
                    'date_created_hora': date_created['hora'],
                    'date_updated_data': date_updated['data'],
                    'date_updated_ano': date_updated['ano'],
                    'date_updated_hora': date_updated['hora'],
                }

                task_text = self.parse_task_text(task.get('text_content', ''))
                field_values = self.extract_field_values(task_text)
                filtered_task.update(field_values)

                filtered_data.append(filtered_task)

                status_history = self.convert_status_history(task.get('time_in_status', {}))
                for entry in status_history.get('status_history', []):
                    status_history_data.append({
                        'task_id': task['id'],
                        'status': emoji_pattern.sub(r'', entry['status']),
                        'time_in_status': self.convert_time_to_days(entry['time_in_status']),
                        'timestamp': datetime.now(self.timezone),
                    })
            except KeyError as e:
                logger.error(f"Missing key {e} in task {task}")
                continue

        return filtered_data, status_history_data

    def parse_date(self, timestamp: int) -> Dict[str, str]:
        """
        Converte um timestamp em milissegundos para um dicionário contendo data, ano e hora.

        Parâmetros:
        - timestamp (int): O timestamp em milissegundos.

        Retorna:
        - Dict[str, str]: Um dicionário com data, ano e hora separadas.
        """
        dt = datetime.utcfromtimestamp(int(timestamp) / 1000).replace(tzinfo=pytz.utc).astimezone(self.timezone)
        return {
            'data': dt.strftime('%d-%m-%Y'),
            'ano': dt.strftime('%Y'),
            'hora': dt.strftime('%H:%M:%S')
        }

    @staticmethod
    def convert_time(time_in_minutes: int) -> str:
        """
        Converte o tempo em minutos para uma string formatada.

        Parâmetros:
        - time_in_minutes (int): O tempo em minutos.

        Retorna:
        - str: O tempo formatado.
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
        Remove quebras de linha e caracteres especiais do texto da tarefa.

        Parâmetros:
        - task_text (str): O texto da tarefa.

        Retorna:
        - str: O texto da tarefa formatado.
        """
        return task_text.replace('\n', ' ').replace('.:', '') if task_text else ''

    @staticmethod
    def extract_field_values(task_text: str) -> Dict[str, str]:
        """
        Extrai os valores dos campos do texto da tarefa.

        Parâmetros:
        - task_text (str): O texto da tarefa.

        Retorna:
        - Dict[str, str]: Um dicionário contendo os valores dos campos extraídos do texto da tarefa.
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
        Converte o histórico de status em um formato mais legível.

        Parâmetros:
        - status_history (Dict): O histórico de status da tarefa.

        Retorna:
        - Dict: O histórico de status convertido em formato mais legível.
        """
        result = {}
        if 'current_status' in status_history and 'total_time' in status_history['current_status']:
            result['current_status'] = {
                'status': status_history['current_status']['status'],
                'time_in_status': self.convert_time(status_history['current_status']['total_time']['by_minute']),
            }
        if 'status_history' in status_history:
            result['status_history'] = [
                {
                    'status': status['status'],
                    'time_in_status': self.convert_time(status['total_time']['by_minute']),
                }
                for status in status_history['status_history']
                if 'total_time' in status
            ]
        return result

    @staticmethod
    def convert_time_to_days(time_str: str) -> float:
        """
        Converte uma string de tempo em um valor float representando dias.

        Parâmetros:
        - time_str (str): O tempo em string, por exemplo '23.7 horas' ou '48.1 dias'.

        Retorna:
        - float: O tempo convertido em dias.
        """
        if 'horas' in time_str:
            hours = float(time_str.split()[0])
            return hours / 24
        elif 'dias' in time_str:
            return float(time_str.split()[0])
        elif 'minutos' in time_str:
            minutes = float(time_str.split()[0])
            return minutes / 1440  # 1440 minutos em um dia
        else:
            return 0.0

    async def get_tasks(self, list_id: str) -> List[Dict[str, Union[str, None]]]:
        """
        Obtém as tarefas de uma lista específica.

        Parâmetros:
        - list_id (str): O ID da lista.

        Retorna:
        - List[Dict[str, Union[str, None]]]: Uma lista de dicionários contendo as informações das tarefas.
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
