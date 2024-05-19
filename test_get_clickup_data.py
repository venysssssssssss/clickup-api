import pytest
import httpx
from httpx import Response
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from fast import app  # Substitua 'your_module_name' pelo nome do módulo onde a função está definida

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_clickup_data_success():
    list_id = "valid_list_id"
    mock_response = {
        "tasks": [
            {
                "id": "86dtd2kjv",
                "status": {"status": "planejamento"},
                "text_content": """
                    CARTEIRA DEMANDANTE :.:
                    TAHTO
                    E-MAIL :.:
                    ricardo.junior@tahto.com.br
                    ESCOPO :.:
                    ...
                """
            }
        ]
    }

    async def mock_get(*args, **kwargs):
        return Response(200, json=mock_response)

    with patch('httpx.AsyncClient.get', new=mock_get):
        response = client.get(f"/get_data_organized/{list_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['ID'] == "86dtd2kjv"
        assert data[0]['Status'] == "planejamento"
        assert data[0]['CARTEIRA DEMANDANTE'] == "TAHTO"
        assert data[0]['E-MAIL'] == "ricardo.junior@tahto.com.br"

@pytest.mark.asyncio
async def test_get_clickup_data_no_tasks():
    list_id = "valid_list_id"
    mock_response = {"tasks": []}

    async def mock_get(*args, **kwargs):
        return Response(200, json=mock_response)

    with patch('httpx.AsyncClient.get', new=mock_get):
        response = client.get(f"/get_data_organized/{list_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

@pytest.mark.asyncio
async def test_get_clickup_data_api_error():
    list_id = "invalid_list_id"

    async def mock_get(*args, **kwargs):
        return Response(400, json={"err": "Invalid list ID"})

    with patch('httpx.AsyncClient.get', new=mock_get):
        response = client.get(f"/get_data_organized/{list_id}")
        assert response.status_code == 400
        assert "Erro ao fazer a solicitação. Código de status: 400" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_clickup_data_invalid_response():
    list_id = "valid_list_id"
    mock_response = {"invalid_key": "invalid_value"}

    async def mock_get(*args, **kwargs):
        return Response(200, json=mock_response)

    with patch('httpx.AsyncClient.get', new=mock_get):
        response = client.get(f"/get_data_organized/{list_id}")
        assert response.status_code == 500
        assert response.json() == {"detail": "Formato de resposta inesperado."}
