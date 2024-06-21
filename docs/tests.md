cat << 'EOF' > testes_fastapi.md
# Testes Automatizados em Pytest para FastAPI

## Visão Geral
Este arquivo contém testes automatizados utilizando Pytest para verificar o comportamento da API FastAPI implementada no arquivo `backup.py`.

## Configuração Inicial
Antes de executar os testes, o ambiente deve estar configurado com o Pytest instalado e um cliente de teste configurado para interagir com a aplicação FastAPI.

```python
import pytest
from fastapi.testclient import TestClient
from backup import app

client = TestClient(app)

valid_list_id = '174940580'
invalid_list_id = '123456789'
