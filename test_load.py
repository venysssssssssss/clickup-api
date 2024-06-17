import os
import pytest
import httpx
import time
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from api.clickup_api import ClickUpAPI

API_KEY = os.getenv('CLICKUP_API_KEY')
TIMEZONE = "UTC"
REDIS_URL = os.getenv('redis_test')
BASE_URL = "https://api.clickup.com/api/v2/list/192943568/task"
HEADERS = {'Authorization': API_KEY}

@pytest.fixture
def clickup_api():
    return ClickUpAPI(API_KEY, TIMEZONE, REDIS_URL)

@pytest.mark.asyncio
async def test_load():
    async def fetch_tasks(client, url, params):
        start_time = time.perf_counter()
        try:
            response = await client.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            end_time = time.perf_counter()
            duration = end_time - start_time
            return response.json(), duration
        except Exception as e:
            end_time = time.perf_counter()
            duration = end_time - start_time
            return e, duration

    async def run_load_test(n_requests):
        start_date_2024 = int(datetime(2024, 1, 1).timestamp() * 1000)
        end_date_2024 = int(datetime(2024, 12, 31, 23, 59, 59).timestamp() * 1000)
        params = {
            'archived': 'false',
            'include_markdown_description': 'true',
            'page_size': 100,
            'include_closed': 'true',
            'due_date_gt': start_date_2024,
            'due_date_lt': end_date_2024,
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            tasks = [fetch_tasks(client, BASE_URL, params) for _ in range(n_requests)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return responses

    # Teste com 10 requisições simultâneas
    responses_10 = await run_load_test(10)
    durations_10 = []
    for response in responses_10:
        if isinstance(response, tuple):
            data, duration = response
            durations_10.append(duration)
            assert isinstance(data, dict)
        else:
            assert isinstance(response, httpx.HTTPStatusError)

    print("Durations:", durations_10)

# Mock do Redis
@pytest.fixture
def mock_redis():
    with patch('redis.StrictRedis') as MockRedis:
        mock_instance = MockRedis.return_value
        mock_instance.ping.return_value = True
        yield mock_instance

@pytest.fixture
def clickup_api_with_mock_redis(mock_redis):
    return ClickUpAPI(API_KEY, TIMEZONE, REDIS_URL)

@pytest.mark.asyncio
async def test_load_with_mock_redis(clickup_api_with_mock_redis):
    await test_load()
