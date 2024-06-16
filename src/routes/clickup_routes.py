import os

import httpx
from fastapi import APIRouter, HTTPException

from api.clickup_api import ClickUpAPI  # Corrigido aqui

router = APIRouter()

API_KEY = os.getenv('CLICKUP_API_KEY')


@router.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    if not list_id.isalnum():
        raise HTTPException(status_code=400, detail='[Invalid list ID.')

    try:
        clickup_api = ClickUpAPI(api_key=API_KEY, timezone='America/Sao_Paulo')
        tasks = await clickup_api.get_tasks(list_id)
        filtered_data = clickup_api.filter_tasks(tasks)
        return filtered_data
    except httpx.HTTPError as http_err:
        raise HTTPException(
            status_code=500, detail=f'HTTP error: {str(http_err)}'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unknown error: {str(e)}')
