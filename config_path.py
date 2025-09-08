# Configura o diretório principal do projeto
import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):  
    # Se estiver rodando no .exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
    # Se estiver rodando no Python normal
        return os.path.abspath(os.path.dirname(__file__))