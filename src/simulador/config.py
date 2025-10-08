"""
Módulo de Configuração da Aplicação

Este módulo contém as configurações necessárias para a aplicação Eel,
incluindo configurações de banco de dados e outras configurações gerais.
"""

import os
import sys
import yaml
from pathlib import Path

def get_asset_path(relative_path):
    """
    Obtém o caminho absoluto para um recurso (asset), funcionando tanto em
    modo de desenvolvimento quanto no executável do PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Estamos rodando em um bundle do PyInstaller
        base_path = Path(sys._MEIPASS)
    else:
        # Estamos rodando em modo normal
        # Assumimos que config.py está em src/simulador, então subimos 2 níveis
        base_path = Path(__file__).resolve().parents[2]
    
    return base_path / relative_path
    
# Diretório base da aplicação
BASE_DIR = get_asset_path('')

# Configurações do banco de dados
DATABASE_URL = f"sqlite:///{BASE_DIR}/instance/database.db"

# Configurações de upload
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx', 'xls'}

# Configurações do Eel
EEL_WEB_FOLDER = get_asset_path('src/web')
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

def carregar_modelo_yaml():
    """
    Carrega o arquivo modelo.yaml e retorna seu conteúdo como dicionário.
    
    Returns:
        dict: Conteúdo do modelo.yaml
    """
    try:
        modelo_path = BASE_DIR / "modelo.yaml"
        with open(modelo_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Erro ao carregar modelo.yaml: {e}")
        return {}

import logging
import logging.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database_models import db, Base

def configurar_logging():
    """Configura o sistema de logging da aplicação."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    return logger

def configurar_banco_dados(logger):
    """Configura e inicializa o banco de dados SQLAlchemy."""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Session = sessionmaker(bind=engine)
        db.session = Session()
        # Cria tabelas se não existirem
        Base.metadata.create_all(engine)
        logger.info("Banco de dados configurado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar banco de dados: {e}")
        return False

