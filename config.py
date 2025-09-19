"""
Módulo de Configuração da Aplicação

Este módulo contém as configurações necessárias para a aplicação Eel,
incluindo configurações de banco de dados e outras configurações gerais.
"""

import os
from pathlib import Path

# Diretório base da aplicação
BASE_DIR = Path(__file__).parent.absolute()

# Configurações do banco de dados
DATABASE_URL = f"sqlite:///{BASE_DIR}/instance/database.db"

# Configurações de upload
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx', 'xls'}

# Configurações do Eel
EEL_WEB_FOLDER = "web"
EEL_SIZE = (1200, 800)
EEL_POSITION = "center"

# Configurações da aplicação
APP_NAME = "Simulador de Operações de Crédito v2"
APP_VERSION = "2.0.0"
DEBUG = True

# Criar diretórios necessários
def criar_diretorios():
    """Cria os diretórios necessários para a aplicação."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(BASE_DIR / "instance", exist_ok=True)

# Configurações de logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': BASE_DIR / 'app.log',
            'mode': 'a',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
}
