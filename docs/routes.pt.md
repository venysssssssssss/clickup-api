# Documentação do Endpoint `/get_data_organized/{list_id}`

Este documento detalha o endpoint `get_data_organized/{list_id}`, que é responsável por recuperar e organizar dados de tarefas do ClickUp utilizando uma API personalizada e armazenamento em cache via Redis.

## Descrição

O endpoint recupera as tarefas de uma lista específica no ClickUp, filtra essas tarefas para dados relevantes, e retorna esses dados organizados para o usuário. Ele valida a lista e configurações de ambiente antes de executar as operações.

## Endpoint: `GET /get_data_organized/{list_id}`

### Parâmetros

- `list_id` (str): O identificador da lista de tarefas no ClickUp. Deve ser um valor alfanumérico para garantir que é um ID válido.

### Respostas

- **200 OK**: Retorna os dados das tarefas filtrados e organizados.
- **400 Bad Request**: Retorna uma mensagem de erro se o `list_id` não for alfanumérico.
- **500 Internal Server Error**: Retorna uma mensagem de erro se a chave API ou a URL do Redis não estiverem configuradas corretamente, ou se ocorrer um erro durante a recuperação ou processamento dos dados.

### Validações e Configurações

- Verifica se `list_id` é alfanumérico.
- Confirma que a chave API (`API_KEY`) e a URL do Redis (`REDIS_URL`) estão definidas, levantando exceções HTTP com código de status 500 se alguma estiver ausente.

### Processamento

1. **Criação da Instância ClickUpAPI**: Uma instância de `ClickUpAPI` é criada com as configurações da API e do Redis.
2. **Recuperação de Tarefas**: As tarefas são recuperadas da API do ClickUp.
3. **Filtragem de Tarefas**: As tarefas são filtradas para extrair dados relevantes.
4. **Retorno dos Dados**: Os dados filtrados são retornados como resposta ao cliente.

### Tratamento de Erros

- Erros HTTP da API do ClickUp são capturados e transformados em `HTTPException` com status 500.
- Erros inesperados são capturados, registrados e também transformados em `HTTPException` com status 500.

## Exemplo de Resposta

```json
{
  "data": [
    {
      "task_id": "12345",
      "status": "complete",
      "name": "Document API Endpoint",
      "assignees": ["user1", "user2"],
      "priority": "high"
    }
  ]
}
```