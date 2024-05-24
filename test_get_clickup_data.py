import pytest
from fast import app
from fastapi.testclient import TestClient

client = TestClient(app)

valid_list_id = '174940580'  # Um ID de lista válido para teste
invalid_list_id = '123456789'  # Um ID de lista inválido para teste


def test_successful_case():
    response = client.get(f'/get_data_organized/{valid_list_id}')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)


def test_failure_case():
    response = client.get(f'/get_data_organized/{invalid_list_id}')
    assert response.status_code == 500


def test_data_structure_and_values():
    response = client.get(f'/get_data_organized/{valid_list_id}')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)

    expected_fields = [
        'Projeto',
        'ID',
        'Status',
        'Name',
        'Priority',
        'Líder',
        'Email líder',
        'date_created',
        'date_updated',
        'CARTEIRA DEMANDANTE',
        'E-MAIL',
        'ESCOPO',
        'OBS',
        'OBJETIVO DO GANHO',
        'KPI GANHO',
        '💡 TIPO DE PROJETO',
        'TIPO DE PROJETO',
        'TIPO DE OPERAÇÃO',
        'PRODUTO',
        'OPERAÇÃO',
        'SITE',
        'UNIDADE DE NEGÓCIO',
        'DIRETOR TAHTO',
        'CLIENTE',
        'TIPO',
        '💡 R$ ANUAL (PREVISTO)',
        'GERENTE OI',
        'FERRAMENTA ENVOLVIDA',
        'CENÁRIO PROPOSTO',
    ]

    for item in data:
        assert all(field in item for field in expected_fields)
        assert isinstance(item['Projeto'], int)
        assert isinstance(item['ID'], str)
        assert isinstance(item['Status'], str)
        assert isinstance(item['Name'], str)
        assert item['Priority'] is None or isinstance(item['Priority'], str)
        assert item['Líder'] is None or isinstance(item['Líder'], str)
        assert item['Email líder'] is None or isinstance(
            item['Email líder'], str
        )
        assert isinstance(item['date_created'], str)
        assert isinstance(item['date_updated'], str)
        assert all(
            isinstance(value, str)
            for value in item.values()
            if isinstance(value, str)
        )
        assert all(
            isinstance(value, int)
            for value in item.values()
            if isinstance(value, int) and value is not None
        )
