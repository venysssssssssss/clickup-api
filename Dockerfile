# Use a imagem base oficial do Python
FROM python:3.10.0

# Instale o Poetry
RUN pip install poetry

# Copia o pyproject.toml e o poetry.lock para o diretório de trabalho
COPY . /src

# Define o diretório de trabalho dentro do container
WORKDIR /src

# Instala as dependências do projeto usando o Poetry
RUN poetry install --no-root

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# Expõe a porta 8000 para acesso à aplicação FastAPI
EXPOSE 8000

# Define o comando para rodar a aplicação
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
