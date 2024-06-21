# Dockerfile Documentation

## Overview
This Dockerfile is used to create a container for a FastAPI application. It uses Python 3.10 and Poetry for dependency management.

## Instructions Breakdown

### Base Image
- **Python 3.10.0**: The Dockerfile starts by pulling the official Python 3.10.0 image.
    ```dockerfile
    FROM python:3.10.0
    ```

### Install Poetry
- **Poetry**: Poetry is installed using pip to manage project dependencies.
    ```dockerfile
    RUN pip install poetry
    ```

### Copy Project Files
- **Copy pyproject.toml and poetry.lock**: These files are copied to the `/src` directory in the container. These files contain the project's dependency specifications.
    ```dockerfile
    COPY . /src
    ```

### Set Working Directory
- **Working Directory**: The working directory inside the container is set to `/src`.
    ```dockerfile
    WORKDIR /src
    ```

### Install Dependencies
- **Install Dependencies**: Poetry is used to install the project's dependencies specified in `pyproject.toml` and `poetry.lock`, without installing the project itself.
    ```dockerfile
    RUN poetry install --no-root
    ```

### Copy Application Code
- **Copy Remaining Code**: The rest of the application code is copied into the `/src` directory.
    ```dockerfile
    COPY . .
    ```

### Expose Port
- **Expose Port 8000**: The container exposes port 8000 to allow external access to the FastAPI application.
    ```dockerfile
    EXPOSE 8000
    ```

### Run the Application
- **Command to Run Application**: The container is set to run the FastAPI application using Uvicorn. It will listen on all network interfaces (`0.0.0.0`) and use port 8000.
    ```dockerfile
    CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

## Complete Dockerfile

```dockerfile
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
