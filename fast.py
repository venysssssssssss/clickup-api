import os
import re
from datetime import datetime

import httpx
import pytz
from fastapi import FastAPI, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

brt_zone = pytz.timezone('America/Sao_Paulo')

app = FastAPI()

# Utilize variáveis de ambiente para a chave de API e URL do Redis
API_KEY = os.getenv('CLICKUP_API_KEY')
REDIS_URL = os.getenv('REDIS_URL')

# Inicialize o backend de cache do Redis
@app.on_event("startup")
async def startup():
    redis = RedisBackend(REDIS_URL)
    FastAPICache.init(redis, prefix="fastapi-cache")

# Restante do código...

@app.get('/get_data_organized/{list_id}')
@cache(expire=86400)  # Cache com tempo de expiração de 1 dia
async def get_clickup_data(list_id: str):
    # Validação do list_id
    if not list_id.isalnum():
        raise HTTPException(status_code=400, detail='ID da lista inválido.')

    # Verifique se os dados estão em cache e se houve alguma alteração
    cached_data = await FastAPICache.get(list_id)
    if cached_data:
        # Implemente a lógica para verificar se os dados em cache estão atualizados
        # Se estiverem atualizados, retorne o cached_data
        # Se não, continue para fazer uma nova solicitação à API
        pass

    try:
        url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
        query = {'archived': 'false', 'include_markdown_description': 'true'}
        headers = {'Authorization': API_KEY}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=query)

        if response.status_code != 200:
            error_detail = f'Erro ao fazer a solicitação. Código de status: {response.status_code}'
            raise HTTPException(status_code=400, detail=error_detail)

        data = response.json()
        # Processamento dos dados...

        # Salve os dados processados no cache antes de retornar
        await FastAPICache.set(list_id, data, expire=86400)

        return data
    except httpx.HTTPError as http_err:
        raise HTTPException(
            status_code=500,
            detail=f'Erro na solicitação HTTP: {str(http_err)}',
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Erro desconhecido: {str(e)}',
        )
