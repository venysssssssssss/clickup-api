import asyncio

import pandas as pd
import pytz
from fastapi import FastAPI

from src.api.clickup_api import ClickUpAPI
from src.cache.redis_cache import RedisCache
from src.config import settings
from src.db.postgres import PostgresDB
from utils.task_utils import filter_tasks

app = FastAPI()

redis_cache = RedisCache(settings.REDIS_URL)
clickup_api = ClickUpAPI(settings.API_KEY, settings.TIMEZONE, redis_cache)
postgres_db = PostgresDB(
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER,
    settings.DB_PASS,
    settings.DB_SCHEMA,
)


@app.get('/get_data_organized/{list_id}')
async def get_data_organized(list_id: str):
    """
    Obtém e organiza os dados das tarefas de uma lista específica no ClickUp.

    Args:
        list_id (str): O ID da lista no ClickUp.

    Returns:
        list: Uma lista de tarefas filtradas.
    """
    print(f'Fetching tasks for list ID: {list_id}')
    tasks = await clickup_api.get_tasks(list_id)
    filtered_tasks, status_history_data = filter_tasks(
        tasks, settings.TIMEZONE
    )

    # Converting the list of dictionaries to pandas DataFrames
    df_tasks = pd.DataFrame(filtered_tasks)
    df_status_history = pd.DataFrame(status_history_data)

    # Saving the DataFrames to PostgreSQL
    if list_id == '192959544':
        postgres_db.save_to_postgres(df_tasks, 'lista_dados_inovacao')
        postgres_db.save_to_postgres(
            df_status_history, 'status_history_inovacao'
        )
    elif list_id == '174940580':
        postgres_db.save_to_postgres(df_tasks, 'lista_dados_negocios')
        postgres_db.save_to_postgres(
            df_status_history, 'status_history_negocios'
        )

    return filtered_tasks
