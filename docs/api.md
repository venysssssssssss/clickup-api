# ClickUp API Documentation

## Overview
The `ClickUpAPI` class interacts with the ClickUp API to fetch and process task data, using Redis for caching and supporting asynchronous HTTP requests.

## Class: ClickUpAPI

### Attributes:
- `api_key`: The API key for authentication with ClickUp.
- `timezone`: The timezone to use for date/time conversions.
- `headers`: Headers for HTTP requests, including the API key.
- `semaphore`: Limits the number of concurrent tasks to avoid overwhelming the server.
- `redis`: Redis client for caching.
- `FIELD_NAMES_SET`: Set of field names for faster lookup.

### Methods:
- `__init__(self, api_key: str, timezone: str, redis_url: str)`: Initializes the ClickUpAPI instance.
- `test_redis_connection(self)`: Tests the connection to the Redis server.
- `get_from_cache(self, key: str) -> Union[List, None]`: Retrieves data from the Redis cache.
- `set_in_cache(self, key: str, data: List, ttl: int = 600)`: Stores data in the Redis cache with a TTL.
- `fetch_clickup_data(self, url: str, query: Dict, retries: int = 3) -> Dict`: Asynchronously fetches data from the ClickUp API.
- `fetch_all_tasks(self, url: str, query: Dict) -> List[Dict]`: Asynchronously fetches all tasks, handling pagination.
- `parse_task_text(self, task_text: str) -> str`: Parses and cleans up task text.
- `parse_date(self, timestamp: int) -> str`: Converts a timestamp to a formatted date string.
- `extract_field_values(self, task_text: str) -> Dict[str, str]`: Extracts specific field values from task text using regex patterns.
- `get_tasks(self, list_id: str) -> List[Dict[str, Union[str, None]]]`: Fetches and caches tasks from a specific list.
- `filter_tasks(self, tasks: List[Dict]) -> List[Dict]`: Filters and processes tasks for specific fields and formatting.

## Detailed Method Documentation

### `__init__(self, api_key: str, timezone: str, redis_url: str)`
Initializes the ClickUpAPI instance.

#### Parameters:
- `api_key` (str): The ClickUp API key.
- `timezone` (str): The timezone for date/time conversions.
- `redis_url` (str): The URL of the Redis server.

### `test_redis_connection(self)`
Tests the connection to the Redis server. Raises an HTTPException if the connection fails.

### `get_from_cache(self, key: str) -> Union[List, None]`
Retrieves data from the Redis cache.

#### Parameters:
- `key` (str): The cache key.

#### Returns:
- Union[List, None]: The cached data or None if not found.

### `set_in_cache(self, key: str, data: List, ttl: int = 600)`
Stores data in the Redis cache with a TTL.

#### Parameters:
- `key` (str): The cache key.
- `data` (List): The data to cache.
- `ttl` (int, optional): Time-to-live for the cache entry. Default is 600 seconds.

### `fetch_clickup_data(self, url: str, query: Dict, retries: int = 3) -> Dict`
Asynchronously fetches data from the ClickUp API.

#### Parameters:
- `url` (str): The API endpoint URL.
- `query` (Dict): Query parameters for the API request.
- `retries` (int, optional): Number of retry attempts in case of failure. Default is 3.

#### Returns:
- Dict: The JSON response from the API.

### `fetch_all_tasks(self, url: str, query: Dict) -> List[Dict]`
Asynchronously fetches all tasks, handling pagination.

#### Parameters:
- `url` (str): The API endpoint URL.
- `query` (Dict): Query parameters for the API request.

#### Returns:
- List[Dict]: A list of tasks.

### `parse_task_text(self, task_text: str) -> str`
Parses and cleans up task text.

#### Parameters:
- `task_text` (str): The text content of a task.

#### Returns:
- str: The cleaned-up task text.

### `parse_date(self, timestamp: int) -> str`
Converts a timestamp to a formatted date string.

#### Parameters:
- `timestamp` (int): The timestamp to convert.

#### Returns:
- str: The formatted date string.

### `extract_field_values(self, task_text: str) -> Dict[str, str]`
Extracts specific field values from task text using regex patterns.

#### Parameters:
- `task_text` (str): The text content of a task.

#### Returns:
- Dict[str, str]: A dictionary of extracted field values.

### `get_tasks(self, list_id: str) -> List[Dict[str, Union[str, None]]]`
Fetches and caches tasks from a specific list.

#### Parameters:
- `list_id` (str): The ID of the task list.

#### Returns:
- List[Dict[str, Union[str, None]]]: A list of tasks with relevant fields.

### `filter_tasks(self, tasks: List[Dict]) -> List[Dict]`
Filters and processes tasks for specific fields and formatting.

#### Parameters:
- `tasks` (List[Dict]): The list of tasks to filter.

#### Returns:
- List[Dict]: The filtered and processed list of tasks.

## Usage Example

```python
from clickup_api import ClickUpAPI
import asyncio

api_key = 'your_clickup_api_key'
timezone = 'UTC'
redis_url = 'redis://localhost:6379/0'
list_id = 'your_list_id'

clickup_api = ClickUpAPI(api_key, timezone, redis_url)

async def main():
    tasks = await clickup_api.get_tasks(list_id)
    filtered_tasks = clickup_api.filter_tasks(tasks)
    print(filtered_tasks)

asyncio.run(main())
```