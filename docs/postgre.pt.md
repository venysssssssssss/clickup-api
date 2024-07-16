# Documentação da Classe PostgresDB

Esta documentação fornece detalhes sobre a classe `PostgresDB`, projetada para interagir com um banco de dados PostgreSQL, permitindo operações como verificar a existência de tabelas e salvar dados de um DataFrame do pandas.

## Classe: PostgresDB

### Inicializador

Inicializa uma instância da classe `PostgresDB`, configurando a conexão com o banco de dados PostgreSQL.

#### Parâmetros:
- `host` (str): O nome do host ou endereço IP do servidor PostgreSQL.
- `port` (str): O número da porta do servidor PostgreSQL.
- `dbname` (str): O nome do banco de dados PostgreSQL.
- `user` (str): O nome de usuário para autenticação no servidor PostgreSQL.
- `password` (str): A senha para autenticação no servidor PostgreSQL.
- `schema` (str, opcional): O esquema a ser usado no banco de dados PostgreSQL. Padrão é 'public'.

#### Atributos:
- `schema` (str): O esquema usado no banco de dados.
- `database_url` (str): A URL para conexão com o banco de dados.
- `engine` (sqlalchemy.engine.Engine): O engine SQLAlchemy para conexão com o banco de dados.

### Métodos

#### `save_to_postgres(df: pd.DataFrame, table_name: str)`
Salva um DataFrame do pandas em uma tabela do PostgreSQL. Se a tabela já existir, os dados serão substituídos.

##### Parâmetros:
- `df` (pd.DataFrame): O DataFrame a ser salvo.
- `table_name` (str): O nome da tabela onde o DataFrame será salvo.

##### Exceções:
- `SQLAlchemyError`: Lançada se ocorrer um erro durante a operação de salvamento no banco de dados.

##### Comportamento:
- A função verifica primeiro se a tabela existe utilizando o método `table_exists`. Se existir, utiliza o parâmetro `replace` para a função `to_sql`, caso contrário, usa `fail`.

#### `table_exists(table_name: str) -> bool`
Verifica se uma tabela especificada existe no esquema configurado do banco de dados PostgreSQL.

##### Parâmetros:
- `table_name` (str): O nome da tabela a ser verificada.

##### Retorna:
- `bool`: `True` se a tabela existir, `False` caso contrário.

##### Detalhes:
- A consulta SQL verificando a existência da tabela é executada através do engine SQLAlchemy, utilizando o esquema definido no inicializador da classe.

## Exemplo de Uso

```python
# Configuração da conexão com o banco de dados
db = PostgresDB(
    host="localhost",
    port="5432",
    dbname="meu_banco",
    user="usuario",
    password="senha",
    schema="meu_esquema"
)

# DataFrame exemplo para salvar
df = pd.DataFrame({
    "coluna1": [1, 2, 3],
    "coluna2": ["A", "B", "C"]
})

# Salvar DataFrame no PostgreSQL
db.save_to_postgres(df, "minha_tabela")
```