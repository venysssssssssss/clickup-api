# Estrutura do Projeto e Arquivo `main.py`

## Estrutura do Projeto

```plaintext
project/
│
├── src/
│   ├── api/
│   │   └── clickup_api.py
│   ├── cache/
│   │   └── redis_cache.py
│   ├── config/
│   │   └── settings.py
│   ├── db/
│   │   └── postgres.py
│   └── main.py
│
└── requirements.txt
```

## Arquivo `main.py`

```python
import asyncio
import pandas as pd
import pytz
from fastapi import FastAPI
from src.api.clickup_api import ClickUpAPI
from src.cache.redis_cache import RedisCache
from src.config import settings
from src.db.postgres import PostgresDB

app = FastAPI()

redis_cache = RedisCache(settings.REDIS_URL)
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
    """
    Obtém e organiza os dados das tarefas de uma lista específica no ClickUp.

    Args:
        list_id (str): O ID da lista no ClickUp.

    Returns:
        list: Uma lista de tarefas filtradas.
    """
    print(f'Fetching tasks for list ID: {list_id}')
    tasks = await clickup_api.get_tasks(list_id)
    filtered_tasks, status_history_data = clickup_api.filter_tasks(tasks)

    # Converting the list of dictionaries to pandas DataFrames
    df_tasks = pd.DataFrame(filtered_tasks)
    df_status_history = pd.DataFrame(status_history_data)

    # Saving the DataFrames to PostgreSQL
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

    return filtered_tasks
```

## Endpoints

### GET /get_data_organized/{list_id}

Obtém e organiza os dados das tarefas de uma lista específica no ClickUp.

#### Parâmetros

- `list_id` (str): O ID da lista no ClickUp.

#### Retorno

- `list`: Uma lista de tarefas filtradas.

## Descrição dos Módulos

### clickup_api

Módulo personalizado para interagir com a API do ClickUp. Responsável por obter e filtrar tarefas.

### redis_cache

Módulo personalizado para implementar o cache utilizando Redis, melhorando a performance ao evitar requisições redundantes.

### settings

Módulo que contém as configurações do projeto, como URLs de conexão e chaves de API.

### postgres

Módulo personalizado para interagir com o banco de dados PostgreSQL. Inclui funções para salvar DataFrames do pandas no banco de dados.

## Funcionalidades

- **Integração com ClickUp**: Obtém dados de tarefas de listas específicas.
- **Filtragem de Tarefas**: Filtra tarefas e histórico de status.
- **Armazenamento no PostgreSQL**: Converte dados em DataFrames e armazena no banco de dados.

## Considerações Finais

Este projeto demonstra uma integração eficiente entre FastAPI, ClickUp e PostgreSQL, utilizando boas práticas de programação assíncrona e manipulação de dados com pandas.