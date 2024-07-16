

```markdown
# Documentação do Projeto

Este projeto utiliza o framework FastAPI para criar uma API que interage com o serviço ClickUp e armazena dados em um banco de dados PostgreSQL. A aplicação também faz uso de um cache Redis para melhorar a performance.

## Arquivo `src/main.py`

### Dependências

```python
import asyncio
import pandas as pd
import pytz
from fastapi import FastAPI

from src.api.clickup_api import ClickUpAPI
from src.cache.redis_cache import RedisCache
from src.config import settings
from src.db.postgres import PostgresDB
```

### Inicialização da Aplicação

A aplicação FastAPI é inicializada da seguinte forma:

```python
app = FastAPI()
```

### Inicialização das Instâncias de Cache, API e Banco de Dados

Criamos instâncias das classes `RedisCache`, `ClickUpAPI` e `PostgresDB` utilizando configurações definidas em `settings`.

```python
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
```

### Endpoint: `/get_data_organized/{list_id}`

Este endpoint obtém e organiza os dados das tarefas de uma lista específica no ClickUp.

#### Definição

```python
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
        postgres_db.save_to_postgres(df_status_history, 'status_history_inovacao')
    elif list_id == '174940580':
        postgres_db.save_to_postgres(df_tasks, 'lista_dados_negocios')
        postgres_db.save_to_postgres(df_status_history, 'status_history_negocios')

    return filtered_tasks
```

#### Descrição

- **Args**:
  - `list_id` (str): O ID da lista no ClickUp.

- **Returns**:
  - `list`: Uma lista de tarefas filtradas.

#### Funcionamento

1. O endpoint recebe um `list_id` como parâmetro.
2. Utiliza o `clickup_api` para obter as tarefas da lista especificada.
3. Filtra as tarefas e obtém os dados do histórico de status.
4. Converte as listas de dicionários em DataFrames do pandas.
5. Salva os DataFrames em tabelas específicas no PostgreSQL, dependendo do `list_id`.
6. Retorna a lista de tarefas filtradas.

#### Condicional `list_id`

- Se `list_id` for '192959544', os dados são salvos nas tabelas `lista_dados_inovacao` e `status_history_inovacao`.
- Se `list_id` for '174940580', os dados são salvos nas tabelas `lista_dados_negocios` e `status_history_negocios`.

### Considerações Finais

Este arquivo principal (`src/main.py`) configura e inicializa os componentes principais da aplicação, define o endpoint e implementa a lógica necessária para obter, filtrar e salvar os dados das tarefas do ClickUp. A documentação detalhada aqui visa fornecer uma compreensão clara e acessível de como o código funciona, mesmo para aqueles que não têm familiaridade com programação.
```

Espero que isso atenda às suas necessidades. Se precisar de mais alguma coisa, é só avisar.