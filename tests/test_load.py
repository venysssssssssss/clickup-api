import asyncio
import os
import time
from datetime import datetime
from unittest.mock import patch

import httpx
import pytest

from api.clickup_api import ClickUpAPI

API_KEY = os.getenv('CLICKUP_API_KEY')
TIMEZONE = 'UTC'
REDIS_URL = os.getenv('redis_test')
BASE_URL = 'https://api.clickup.com/api/v2/list/192943568/task'
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
        end_date_2024 = int(
            datetime(2024, 12, 31, 23, 59, 59).timestamp() * 1000
        )
        params = {
            'archived': 'false',
            'include_markdown_description': 'true',
            'page_size': 100,
            'include_closed': 'true',
            'due_date_gt': start_date_2024,
            'due_date_lt': end_date_2024,
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            tasks = [
                fetch_tasks(client, BASE_URL, params)
                for _ in range(n_requests)
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return responses

    # Helper function to calculate average duration
    def calculate_average_duration(responses):
        durations = [
            response[1]
            for response in responses
            if isinstance(response, tuple)
        ]
        if durations:
            return sum(durations) / len(durations)
        return 0

    # Teste com 10 requisições simultâneas
    responses_10 = await run_load_test(10)
    avg_duration_10 = calculate_average_duration(responses_10)
    print('Average duration for 10 requests:', avg_duration_10)

    # Teste com 20 requisições simultâneas
    responses_20 = await run_load_test(20)
    avg_duration_20 = calculate_average_duration(responses_20)
    print('Average duration for 20 requests:', avg_duration_20)

    # Teste com 50 requisições simultâneas
    responses_50 = await run_load_test(50)
    avg_duration_50 = calculate_average_duration(responses_50)
    print('Average duration for 50 requests:', avg_duration_50)

    # Teste com 90 requisições simultâneas
    responses_90 = await run_load_test(90)
    avg_duration_90 = calculate_average_duration(responses_90)
    print('Average duration for 90 requests:', avg_duration_90)


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
