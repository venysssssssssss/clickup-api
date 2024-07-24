import requests


def get_all_tasks(list_id):
    """Busca todas as tarefas de uma lista específica."""
    url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
    headers = {'Authorization': 'pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2'}
    query = {
        'include_subtasks': 'true',
        'page': 0,  # Começamos na primeira página
    }
    tasks = []

    while True:
        response = requests.get(url, headers=headers, params=query)
        data = response.json()
        tasks.extend(data.get('tasks', []))

        # Verifica se há mais páginas
        if 'next' in data.get('pagination', {}):
            query['page'] += 1
        else:
            break

    return tasks


def sum_ganho_anual(tasks):
    """Calcula a soma dos valores do campo '💡 R$ GANHO ANUAL'."""
    total_sum = 0.0
    for task in tasks:
        custom_fields = task.get('custom_fields', [])
        ganho_anual_field = next(
            (
                field
                for field in custom_fields
                if field.get('name') == '💡 R$ GANHO ANUAL '
            ),
            None,
        )
        if ganho_anual_field and 'value' in ganho_anual_field:
            try:
                total_sum += float(ganho_anual_field['value'])
            except ValueError:
                print(
                    f"Valor não numérico encontrado: {ganho_anual_field['value']}"
                )

    return total_sum


def format_value(value):
    """Formata o valor em mil (K) e milhões (M) para melhor visualização."""
    if value >= 1_000_000:
        return f'{value / 1_000_000:.2f}M'
    elif value >= 1000:
        return f'{value / 1000:.2f}K'
    return f'{value:.2f}'


# List ID da lista de tarefas
list_id = '192959544'
tasks = get_all_tasks(list_id)
total_ganho_anual = sum_ganho_anual(tasks)
formatted_total = format_value(total_ganho_anual)
print(f"Soma Total de '💡 R$ GANHO ANUAL': {formatted_total}")
