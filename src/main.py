import pandas as pd
import pytz
from fastapi import FastAPI

from src.api.clickup_api import ClickUpAPI
from src.cache.redis_cache import RedisCache
from src.config import settings
from src.db.postgres import PostgresDB
from src.utils.task_utils import filter_tasks  # Atualize a importação

app = FastAPI()

# Parâmetros de conexão Redis
host = "oregon-redis.render.com"
port = 6379
username = "red-cpn3p3o8fa8c73aqq8q0"
password = "vYcELCVWAem69bACEgQRp6XKnpCAcHfH"

# Inicializa o cache Redis
redis_cache = RedisCache(host=settings.HOST_CACHE, port=settings.PORT_CACHE, username=settings.USER_CACHE, password=settings.PASS_CACHE)
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
    print(f'Fetching tasks for list ID: {list_id}')
    tasks = await clickup_api.get_tasks(list_id)
    filtered_tasks, status_history_data = filter_tasks(
        tasks, settings.TIMEZONE
    )

    df_tasks = pd.DataFrame(filtered_tasks)
    df_status_history = pd.DataFrame(status_history_data)

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

    return {'filtered_tasks': filtered_tasks}
