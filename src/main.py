import asyncio
import logging

import pandas as pd
import pytz
from fastapi import FastAPI

from src.api.clickup_api import ClickUpAPI
from src.cache.redis_cache import RedisCache
from src.config import settings
from src.db.postgres import PostgresDB

app = FastAPI()

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def get_table_name(list_id: str) -> str:
    """
    Retorna o nome da tabela baseado no list_id.
    """
    table_mapping = {
        '192959544': 'lista_dados_inovacao',
        '174940580': 'lista_dados_negocios',
    }
    return table_mapping.get(list_id, 'tasks')


@app.get('/get_data_organized/{list_id}')
async def get_data_organized(list_id: str):
    logger.info(f'Fetching tasks for list ID: {list_id}')
    tasks = await clickup_api.get_tasks(list_id)
    filtered_tasks = clickup_api.filter_tasks(tasks)

    # Converting the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(filtered_tasks)

    # Determine the table name based on the list_id
    table_name = get_table_name(list_id)
    logger.info(f'Saving data to table: {table_name}')

    # Saving the DataFrame to PostgreSQL
    postgres_db.save_to_postgres(df, table_name)

    return filtered_tasks
