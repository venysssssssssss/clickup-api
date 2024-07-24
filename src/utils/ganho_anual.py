from typing import Dict, List, Union

from fastapi import logger

def get_ganho_anual(task):
    """
    Extrai o valor do campo "💡 R$ GANHO ANUAL" de uma tarefa.
    """
    custom_fields = task.get("custom_fields", [])
    ganho_anual_field = next((field for field in custom_fields if field.get("name") == "💡 R$ GANHO ANUAL "), None)
    if ganho_anual_field and 'value' in ganho_anual_field:
        try:
            return float(ganho_anual_field['value'])
        except ValueError:
            print(f"Valor não numérico encontrado: {ganho_anual_field['value']}")
    return None
