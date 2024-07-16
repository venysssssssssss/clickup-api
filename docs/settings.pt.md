# Documentação do Módulo de Configurações

Este documento detalha as variáveis de configuração carregadas e utilizadas pela aplicação, que são essenciais para a conexão com serviços externos e para definir comportamentos específicos do ambiente de produção.

## Variáveis de Configuração

### Geral
- `API_KEY` (str): Chave de API usada para autenticação em serviços externos.

### Timezone
- `TIMEZONE` (str): O fuso horário utilizado pela aplicação. O valor padrão é 'UTC'.

### Redis
- `REDIS_URL` (str): A URL de conexão com o servidor Redis.

### Banco de Dados de Produção
- `DB_HOST` (str): O hostname do banco de dados de produção.
- `DB_PORT` (str): O número da porta para a conexão com o banco de dados de produção.
- `DB_NAME` (str): O nome do banco de dados de produção.
- `DB_USER` (str): O nome de usuário utilizado para conectar ao banco de dados de produção.
- `DB_PASS` (str): A senha para conexão com o banco de dados de produção.
- `DB_SCHEMA` (str): O esquema utilizado no banco de dados de produção.

## Carregamento das Configurações

No início do módulo, as configurações são carregadas a partir de um arquivo `.env` usando a biblioteca `dotenv`, que é responsável por importar e disponibilizar as variáveis de ambiente definidas no arquivo para o ambiente de execução da aplicação.

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
```