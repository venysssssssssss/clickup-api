from typing import Literal
import pytest
from fastapi.testclient import TestClient
from fast import app

client = TestClient(app)

valid_list_ids = ["174940580", "192943657", "192943564", "192943568"]
valid_list_id = "174940580"  # Um ID de lista válido para teste
invalid_list_id = "123456789"  # Um ID de lista inválido para teste

@pytest.mark.parametrize("list_id", valid_list_id)
def test_successful_case(list_id: Literal['174940580']):
    response = client.get(f'https://clickup-api-yi7o.onrender.com/get_data_organized/174940580')
    assert response.status_code == 200

def test_failure_case():
    response = client.get(f'/get_data_organized/{invalid_list_id}')
    assert response.status_code == 400

@pytest.mark.parametrize("list_id", valid_list_ids)
def test_data_structure(list_id: str):
    response = client.get(f'/get_data_organized/{list_id}')
    data = response.json()
    assert all(isinstance(item, dict) for item in data)

@pytest.mark.parametrize("list_id", valid_list_ids)
def test_data_values(list_id: str):
    response = client.get(f'/get_data_organized/{list_id}')
    data = response.json()
    assert all('ID' in item for item in data)

def test_exception_handling():
    response = client.get(f'/get_data_organized/{invalid_list_id}')
    assert response.status_code == 400
