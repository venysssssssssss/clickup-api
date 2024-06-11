import pytest
from fastapi.testclient import TestClient

from src.fast import app

client = TestClient(app)

valid_list_id = '174940580'

invalid_list_id = '123456789'


def test_successful_case():
    """
    Test case to verify the successful retrieval of data from the API.

    This function sends a GET request to the '/get_data_organized/{valid_list_id}' endpoint
    and asserts that the response status code is 200. It then checks that the response data
    is a list of dictionaries.

    Returns:
        None
    """
    response = client.get(f'/get_data_organized/{valid_list_id}')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)


def test_failure_case():
    """
    Test case for failure scenario when getting organized data.

    This test case sends a GET request to the '/get_data_organized' endpoint with an invalid list ID.
    It asserts that the response status code is 500, indicating a server error.
    """
    response = client.get(f'/get_data_organized/{invalid_list_id}')
    assert response.status_code == 500


def test_data_structure_and_values():
    """
    Test the structure and values of the data returned from the API.

    This function sends a GET request to the API endpoint '/get_data_organized/{valid_list_id}'
    and asserts that the response status code is 200. It then checks the structure and values
    of the returned data.

    The expected_fields list contains the names of the expected fields in the data. The function
    iterates over each item in the data and asserts that all expected fields are present. It also
    checks the data types of specific fields.

    Raises:
        AssertionError: If any of the assertions fail.

    """
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
