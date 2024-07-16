[![clickup_api_to_dw](docs\static\img_exca.svg)](https://excalidraw.com/#json=CNdxxeExm7K-clUexHxMr,DGr7x_W10WefJ8Up9aey7w)

---

Aqui está a versão modificada do guia, incluindo instruções para rodar o seu projeto atual usando `Poetry`, configurando o ambiente virtual e instalando as dependências sem instalar o pacote raiz.

---

## Instalação do pyenv

### Linux

1. **Instale as dependências necessárias**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
   libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
   xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
   ```

2. **Instale o pyenv**:
   ```bash
   curl https://pyenv.run | bash
   ```

3. **Configure o ambiente**:
   Adicione as seguintes linhas ao seu `~/.bashrc`:
   ```bash
   export PATH="$HOME/.pyenv/bin:$PATH"
   eval "$(pyenv init --path)"
   eval "$(pyenv virtualenv-init -)"
   ```

4. **Reinicie o terminal** ou execute `source ~/.bashrc`.

### Windows

Para Windows, recomendamos usar o `pyenv-win`:

1. **Instale o pyenv-win**:
   ```powershell
   pip install pyenv-win --target "$HOME/.pyenv"
   ```

2. **Configure o ambiente**:
   Adicione `$HOME/.pyenv/pyenv-win/bin` e `$HOME/.pyenv/pyenv-win/shims` ao seu PATH através das Configurações do Sistema.

### macOS

1. **Instale o Homebrew** se ainda não estiver instalado:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Instale o pyenv** usando o Homebrew:
   ```bash
   brew install pyenv
   ```

3. **Adicione o pyenv ao seu perfil**:
   ```bash
   echo 'if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi' >> ~/.zprofile
   ```

4. **Instale o Python desejado**:
   ```bash
   pyenv install 3.9.0
   ```

## Instalação do Poetry

### Universal (Linux, Windows, macOS)

1. **Instale o Poetry**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Configure o PATH** (se necessário):
   Certifique-se de que o diretório `~/.local/bin` está no seu PATH para acessar o binário do Poetry.

---

## Configuração do Projeto

1. **Defina a versão do Python usando pyenv**:
   ```bash
   pyenv local 3.x.x
   ```

2. **Navegue até o diretório do seu projeto**:
   ```bash
   cd caminho_para_seu_projeto
   ```

3. **Inicialize o ambiente virtual usando Poetry**:
   ```bash
   poetry shell
   ```

4. **Instale as dependências do projeto sem instalar o pacote raiz**:
   ```bash
   poetry install --no-root
   ```

5. **Execute o projeto**:
   ```bash
   python nome_do_script.py
   ```

Estas instruções ajudarão você a configurar e executar seu projeto Python atual, utilizando as versões específicas do Python definidas pelo `pyenv` e gerenciando dependências com `Poetry`.