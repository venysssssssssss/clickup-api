import httpx
from typing import Dict

async def fetch_time_in_status(task_id: str, client: httpx.AsyncClient, headers: Dict[str, str]) -> Dict:
    url = f'https://api.clickup.com/api/v2/task/{task_id}/time_in_status'
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
