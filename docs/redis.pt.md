# Documentação da Classe RedisCache

Este documento fornece uma visão detalhada da classe `RedisCache`, utilizada para interagir com um banco de dados Redis para armazenar e recuperar dados de forma eficiente.

## Classe: RedisCache

### Inicializador

Inicializa uma instância da classe `RedisCache`, configurando a conexão com um servidor Redis especificado pela URL.

#### Parâmetros
- `redis_url` (str): A URL de conexão com o Redis.

#### Comportamento
- Ao inicializar, a conexão com o Redis é testada automaticamente. Se a conexão falhar, uma exceção HTTP será lançada.

### Métodos

#### `test_redis_connection()`
Testa a conexão com o servidor Redis para garantir que está ativa e funcional.

##### Exceções
- `HTTPException`: Lançada se a conexão com o Redis falhar, com o status code 500 e uma mensagem detalhada do erro.

##### Efeitos Colaterais
- Imprime uma mensagem no console indicando sucesso ou falha na conexão.

#### `get(key: str) -> Union[List, None]`
Recupera os dados armazenados no Redis associados à chave especificada.

##### Parâmetros
- `key` (str): A chave dos dados a serem obtidos.

##### Retorna
- `Union[List, None]`: Retorna os dados deserializados armazenados sob a chave especificada, ou `None` se não existirem dados para a chave.

##### Comportamento
- Se ocorrer um erro ao acessar o Redis, uma mensagem de erro é impressa e `None` é retornado.

#### `set(key: str, data: List, ttl: int = 600)`
Armazena os dados no Redis associados a uma chave, com um tempo de vida especificado.

##### Parâmetros
- `key` (str): A chave sob a qual os dados serão armazenados.
- `data` (List): Os dados a serem armazenados.
- `ttl` (int, opcional): O tempo de vida dos dados em segundos. O padrão é 600 segundos (10 minutos).

##### Comportamento
- Armazena os dados serializados no Redis. Se ocorrer um erro durante o armazenamento, uma mensagem de erro é impressa.

### Exceções Comuns
- `redis.RedisError`: Capturada e tratada dentro dos métodos `get` e `set`, resultando na impressão de mensagens de erro no console em caso de falha nas operações.

## Uso

A classe `RedisCache` é projetada para ser utilizada em aplicações que requerem armazenamento de dados rápido e eficiente com capacidade de expiração automática. Ela é particularmente útil em cenários de cache de dados para aplicações web, onde a velocidade de acesso aos dados é crítica.

