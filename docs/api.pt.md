# Documentação da API ClickUp

Este documento fornece uma visão detalhada da classe `ClickUpAPI`, que é utilizada para interagir com a API do ClickUp para gerenciar tarefas e obter dados específicos de status.

## Classe: ClickUpAPI

### Inicializador
Inicializa uma instância da classe `ClickUpAPI`.

#### Parâmetros:
- `api_key` (str): A chave de API do ClickUp.
- `timezone` (str): O fuso horário utilizado para converter as datas.
- `redis_cache`: O objeto de cache Redis utilizado para armazenar os dados em cache.

#### Exceções:
- Lança `ValueError` se a chave de API não for fornecida.

### Métodos

#### `async fetch_clickup_data(url: str, query: Dict) -> Dict`
Faz uma requisição assíncrona para a API do ClickUp e retorna os dados em formato JSON.

##### Parâmetros:
- `url` (str): A URL da API do ClickUp.
- `query` (Dict): Os parâmetros da consulta.

##### Retorna:
- `Dict`: Os dados da resposta em formato JSON.

##### Exceções:
- Lança `HTTPException` se ocorrer um erro na requisição HTTP.

#### `async fetch_all_tasks(url: str, query: Dict) -> List[Dict]`
Faz uma requisição assíncrona para a API do ClickUp e retorna todas as tarefas em formato de lista de dicionários.

##### Parâmetros:
- `url` (str): A URL da API do ClickUp.
- `query` (Dict): Os parâmetros da consulta.

##### Retorna:
- `List[Dict]`: Uma lista de dicionários contendo as informações das tarefas.

#### `async fetch_time_in_status(task_id: str, client: httpx.AsyncClient) -> Dict`
Obtém o tempo gasto em cada status de uma tarefa específica.

##### Parâmetros:
- `task_id` (str): O ID da tarefa.
- `client` (httpx.AsyncClient): O cliente HTTP utilizado para fazer a requisição.

##### Retorna:
- `Dict`: Os dados do tempo em cada status da tarefa em formato JSON.

#### `async fetch_all_time_in_status(tasks: List[Dict]) -> None`
Obtém o tempo em status para todas as tarefas fornecidas.

##### Parâmetros:
- `tasks` (List[Dict]): Uma lista de dicionários contendo as informações das tarefas.

#### `filter_tasks(tasks: List[Dict]) -> (List[Dict], List[Dict])`
Filtra as tarefas retornando apenas as informações relevantes e o histórico de status.

##### Parâmetros:
- `tasks` (List[Dict]): Uma lista de dicionários contendo as informações das tarefas.

##### Retorna:
- `Tuple[List[Dict], List[Dict]]`: Uma tupla contendo a lista de tarefas filtradas e o histórico de status.

#### Métodos Estáticos

##### `convert_time(time_in_minutes: int) -> str`
Converte o tempo em minutos para uma string formatada.

###### Parâmetros:
- `time_in_minutes` (int): O tempo em minutos.

###### Retorna:
- `str`: O tempo formatado em minutos, horas ou dias.

##### `parse_task_text(task_text: str) -> str`
Remove quebras de linha e caracteres especiais do texto da tarefa.

###### Parâmetros:
- `task_text` (str): O texto da tarefa.

###### Retorna:
- `str`: O texto da tarefa formatado.

##### `extract_field_values(task_text: str) -> Dict[str, str]`
Extrai os valores dos campos do texto da tarefa.

###### Parâmetros:
- `task_text` (str): O texto da tarefa.

###### Retorna:
- `Dict[str, str]`: Um dicionário contendo os valores dos campos extraídos do texto da tarefa.

##### `convert_status_history(status_history: Dict) -> Dict`
Converte o histórico de status em um formato mais legível.

###### Parâmetros:
- `status_history` (Dict): O histórico de status da tarefa.

###### Retorna:
- `Dict`: O histórico de status convertido em formato mais legível.

#### `async get_tasks(list_id: str) -> List[Dict[str, Union[str, None]]]`
Obtém as tarefas de uma lista específica.

##### Parâmetros:
- `list_id` (str): O ID da lista.

##### Retorna:
- `List[Dict[str, Union[str, None]]]`: Uma lista de dicionários contendo as informações das tarefas.
