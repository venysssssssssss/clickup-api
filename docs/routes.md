# clickup_routes.py Documentation

## Overview
This script sets up a FastAPI router for handling ClickUp-related endpoints. It includes a route to fetch and organize data from the ClickUp API.

## Environment Variables
- The script uses environment variables to access the ClickUp API key and Redis URL. These are loaded using `os.getenv`.

## Setup Steps

### Imports and Router Initialization
- **Imports**: Necessary libraries and modules are imported. The ClickUpAPI class is imported from the `clickup_api` module.
- **Router Initialization**: An instance of the FastAPI `APIRouter` is created.
    ```python
    import os
    import httpx
    from fastapi import APIRouter, HTTPException
    from api.clickup_api import ClickUpAPI  # Importe ajustado conforme a estrutura do seu projeto

    router = APIRouter()
    ```

### Load Environment Variables
- **API Key and Redis URL**: The ClickUp API key and Redis URL are loaded from environment variables.
    ```python
    API_KEY = os.getenv('CLICKUP_API_KEY')
    REDIS_URL = os.getenv('REDIS_URL')   # URL interna do Redis no Render
    ```

### Endpoint Definition
- **Get Data Organized**: An endpoint is defined to fetch and organize data from the ClickUp API. It uses the `ClickUpAPI` class to fetch and filter tasks.
    ```python
    @router.get('/get_data_organized/{list_id}')
    async def get_clickup_data(list_id: str):
        if not list_id.isalnum():
            raise HTTPException(status_code=400, detail='Invalid list ID.')

        try:
            clickup_api = ClickUpAPI(
                api_key=API_KEY, timezone='America/Sao_Paulo', redis_url=REDIS_URL
            )
            tasks = await clickup_api.get_tasks(list_id)
            filtered_data = clickup_api.filter_tasks(tasks)
            return filtered_data
        except httpx.HTTPError as http_err:
            raise HTTPException(
                status_code=500, detail=f'HTTP error: {str(http_err)}'
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Unknown error: {str(e)}')
    ```

## Complete Code

```python
import os
import httpx
from fastapi import APIRouter, HTTPException
from api.clickup_api import ClickUpAPI  # Importe ajustado conforme a estrutura do seu projeto

router = APIRouter()

API_KEY = os.getenv('CLICKUP_API_KEY')
REDIS_URL = os.getenv('REDIS_URL')   # URL interna do Redis no Render

@router.get('/get_data_organized/{list_id}')
async def get_clickup_data(list_id: str):
    if not list_id.isalnum():
        raise HTTPException(status_code=400, detail='Invalid list ID.')

    try:
        clickup_api = ClickUpAPI(
            api_key=API_KEY, timezone='America/Sao_Paulo', redis_url=REDIS_URL
        )
        tasks = await clickup_api.get_tasks(list_id)
        filtered_data = clickup_api.filter_tasks(tasks)
        return filtered_data
    except httpx.HTTPError as http_err:
        raise HTTPException(
            status_code=500, detail=f'HTTP error: {str(http_err)}'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail='Unknown error: {str(e)}')
```