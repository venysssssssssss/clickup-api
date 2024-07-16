Aqui está a documentação do workflow em formato Markdown:

---

# GitHub Actions Workflow: Schedule API Requests

Este workflow é configurado para fazer requisições a duas APIs diferentes a cada 3 horas, utilizando o `cron` agendador.

## Descrição

O workflow `Schedule API Requests` é executado em um ambiente `ubuntu-latest` e possui um único job `call_apis` que realiza duas requisições HTTP usando `curl`. Se qualquer uma das requisições falhar, o job será interrompido e um erro será reportado.

## Definição do Workflow

```yaml
name: Schedule API Requests

on:
  schedule:
    - cron: '0 */3 * * *'  # Executa a cada 3 horas

jobs:
  call_apis:
    runs-on: ubuntu-latest

    steps:
    - name: Make API request to get_data_organized/192959544
      run: |
        echo "Fetching: ${{ secrets.API_URL_1_INO }}"
        curl -s -o /dev/null -w "%{http_code}" "${{ secrets.API_URL_1_INO }}"
        if [ $? -ne 0 ]; then
          echo "Failed to fetch ${{ secrets.API_URL_1_INO }}"
          exit 1
        fi
    - name: Make API request to get_data_organized/174940580
      run: |
        echo "Fetching: ${{ secrets.API_URL_2_NEG }}"
        curl -s -o /dev/null -w "%{http_code}" "${{ secrets.API_URL_2_NEG }}"
        if [ $? -ne 0 ]; then
          echo "Failed to fetch ${{ secrets.API_URL_2_NEG }}"
          exit 1
        fi
```

## Explicação das Configurações

### Triggers

- `schedule`: O workflow é agendado para executar a cada 3 horas usando uma expressão cron (`0 */3 * * *`).

### Jobs

#### `call_apis`

- `runs-on`: Define o ambiente de execução como `ubuntu-latest`.

#### Steps

1. **Make API request to get_data_organized/192959544**
   - Faz uma requisição HTTP à URL armazenada no secret `API_URL_1_INO`.
   - Utiliza `curl` para fazer a requisição de forma silenciosa (`-s`), ignorando a saída padrão e registrando apenas o código de status HTTP (`-o /dev/null -w "%{http_code}"`).
   - Verifica se o comando `curl` foi bem-sucedido (`if [ $? -ne 0 ]; then`).
   - Em caso de falha, imprime uma mensagem de erro e interrompe a execução (`exit 1`).

2. **Make API request to get_data_organized/174940580**
   - Faz uma requisição HTTP à URL armazenada no secret `API_URL_2_NEG` seguindo os mesmos passos descritos acima.

## Configuração de Secrets

- `API_URL_1_INO`: URL da primeira API a ser chamada.
- `API_URL_2_NEG`: URL da segunda API a ser chamada.

---
