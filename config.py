# Configura o diretório principal do projeto
import os
import sys
import json
from pathlib import Path

def get_base_dir():
    if getattr(sys, 'frozen', False):  
    # Se estiver rodando no .exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
    # Se estiver rodando no Python normal
        return os.path.abspath(os.path.dirname(__file__))
    
class Config:
    def __init__(self):
        self.base_path = self._get_base_path()
        self.data_path = self._get_data_path()
        self.config_file = self._load_user_config()
    
    def _get_base_path(self):
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        return Path(__file__).parent.parent
    
    def _get_data_path(self):
        if getattr(sys, 'frozen', False):
            return Path.home() / 'OperationCredit'
        return self.base_path.cwd() / 'instance'
    
    def _load_user_config(self):
        config_path = self.data_path / 'config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return self._get_default_config()
    
    def _get_default_config(self):
        return {
            'database': {
                'uri': f'sqlite:///{(self.data_path/'database.db').as_posix()}'
            },
            'server': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': False
            },
            'cache': {
                'enabled': True,
                'timeout': 300
            }
        }