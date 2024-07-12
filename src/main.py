import asyncio
import pandas as pd
from fastapi import FastAPI
from src.api.clickup_api import ClickUpAPI
from src.cache.redis_cache import RedisCache
from src.db.postgres import PostgresDB
from src.config import settings
import pytz

app = FastAPI()

redis_cache = RedisCache(settings.REDIS_URL)
clickup_api = ClickUpAPI(settings.API_KEY, settings.TIMEZONE, redis_cache)
postgres_db = PostgresDB(
    settings.DB_HOST, settings.DB_PORT, settings.DB_NAME,
    settings.DB_USER, settings.DB_PASS, settings.DB_SCHEMA
)

@app.get("/get_data_organized/{list_id}")
async def get_data_organized(list_id: str):
    print(f"Fetching tasks for list ID: {list_id}")
    tasks = await clickup_api.get_tasks(list_id)
    filtered_tasks = clickup_api.filter_tasks(tasks)
    
    # Converting the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(filtered_tasks)
    
    # Saving the DataFrame to PostgreSQL
    postgres_db.save_to_postgres(df, 'tasks')
    
    return filtered_tasks
