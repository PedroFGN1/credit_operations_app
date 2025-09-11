# Simulador de Operações de Crédito - Aplicativo Desktop

Este é um aplicativo desktop desenvolvido com Flask e PyWebView para gerenciar operações de crédito. Ele oferece uma interface de usuário amigável para interagir com um banco de dados local e configurações personalizáveis.

## Funcionalidades

- **Interface Desktop:** Utiliza PyWebView para fornecer uma experiência de aplicativo desktop.
- **Configuração Flexível:** Permite a configuração de banco de dados, servidor e cache através de um arquivo `config.json`.
- **Servidor Flask Integrado:** Roda um servidor Flask em uma thread separada para servir a interface web.
- **Gerenciamento de Dados:** Interage com um banco de dados SQLite local para armazenar e gerenciar dados de operações de crédito.

## Tecnologias Utilizadas

- **Python:** Linguagem de programação principal.
- **Flask:** Microframework web para a lógica de backend e roteamento.
- **PyWebView:** Biblioteca para exibir conteúdo web em janelas desktop nativas.
- **SQLite:** Banco de dados leve e embutido para armazenamento de dados.

## Instalação

Para configurar e rodar o projeto localmente, siga os passos abaixo:

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/PedroFGN1/credit_operations_app.git
   cd credit_operations_app
   ```

2. **Instale as dependências:**

   Embora o arquivo `requirements.txt` não tenha sido lido, as dependências esperadas incluem `Flask` e `PyWebView`. Você pode instalá-las manualmente:

   ```bash
   pip install Flask PyWebView
   ```

   *Nota: Pode haver outras dependências não listadas aqui devido à falha na leitura do arquivo `requirements.txt`.*

3. **Configuração (Opcional):**

   O aplicativo pode ser configurado através de um arquivo `config.json` localizado no diretório `instance/`. Um exemplo de configuração padrão é:

   ```json
   {
       "database": {
           "uri": "sqlite:///instance/database.db"
       },
       "server": {
           "host": "127.0.0.1",
           "port": 5000,
           "debug": false
       },
       "cache": {
           "enabled": true,
           "timeout": 300
       }
   }
   ```

## Uso

Para iniciar o aplicativo, execute o arquivo `run.py`:

```bash
python run.py
```

Isso iniciará o servidor Flask e abrirá a interface do aplicativo em uma janela desktop.

## Estrutura do Projeto

```
credit_operations_app/
├── app/                  # Contém a lógica principal do aplicativo Flask
├── config.py             # Configurações do aplicativo
├── instance/             # Arquivos de instância, como o banco de dados e config.json
├── docs/                 # Documentação adicional (se houver)
├── OperationCredit.exe   # Executável do aplicativo (se compilado com PyInstaller)
├── requirements.txt      # Dependências do projeto (não lido)
└── run.py                # Ponto de entrada para iniciar o aplicativo
```


