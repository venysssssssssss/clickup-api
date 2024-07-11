import asyncio
from fastapi import FastAPI
from src.api.clickup_api import ClickUpAPI
from src.cache.redis_cache import RedisCache
from src.config import settings

app = FastAPI()

redis_cache = RedisCache(settings.REDIS_URL)
clickup_api = ClickUpAPI(settings.API_KEY, settings.TIMEZONE, redis_cache)

@app.get("/tasks/{list_id}")
async def get_tasks(list_id: str):
    tasks = await clickup_api.get_tasks(list_id)
    filtered_tasks = clickup_api.filter_tasks(tasks)
    return filtered_tasks
