# Documentação do Dockerfile para Aplicação FastAPI com Poetry

Este Dockerfile é configurado para construir uma imagem Docker para uma aplicação FastAPI, utilizando o gerenciador de pacotes Poetry para gerenciar as dependências do Python.

## Estrutura do Dockerfile

```dockerfile
# Utiliza a imagem oficial do Python 3.10.0 como base
FROM python:3.10.0

# Instala o gerenciador de pacotes Poetry
RUN pip install poetry

# Copia o arquivo pyproject.toml e o arquivo de bloqueio poetry.lock para o diretório de trabalho
COPY . /src

# Define o diretório de trabalho dentro do container
WORKDIR /src

# Instala as dependências do projeto definidas no Poetry, exceto o próprio projeto (opção --no-root)
RUN poetry install --no-root

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# Expõe a porta 8000, configurada para a aplicação FastAPI acessar a rede
EXPOSE 8000

# Define o comando padrão para iniciar a aplicação usando Poetry e Uvicorn
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```