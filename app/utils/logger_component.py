# Arquivo: logger_component.py (versão Flask)

import logging
import sys
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum
from queue import Queue

class LogLevel(Enum):
    """Níveis de log com cores associadas para o frontend."""
    DEBUG = ("DEBUG", "#6c757d")
    INFO = ("INFO", "#17a2b8")
    SUCCESS = ("SUCCESS", "#28a745")
    WARNING = ("WARNING", "#ffc107")
    ERROR = ("ERROR", "#dc3545")
    CRITICAL = ("CRITICAL", "#6f42c1")

class LoggerComponent:
    """Logger para aplicações web, com fila para streaming de logs."""
    
    def __init__(self, name: str = "AppLogger"):
        self.name = name
        self.log_history: List[Dict[str, Any]] = []
        self.log_queue: Queue = Queue() # Fila para novas mensagens de log
        self._setup_console_logger()
    
    def _setup_console_logger(self):
        """Configura um logger básico para o terminal do servidor."""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level: LogLevel, message: str, details: str = None):
        """Cria uma entrada de log, armazena no histórico e coloca na fila de stream."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = {
            'timestamp': timestamp,
            'level': level.value[0],
            'color': level.value[1],
            'message': message,
            'details': details or ""
        }
        
        # Armazena no histórico para consultas futuras
        self.log_history.append(log_entry)
        
        # Coloca na fila para ser transmitido em tempo real
        self.log_queue.put(log_entry)
        
        self.logger.info(f"{level.value[0]}: {message}")
            
    # --- Funções públicas para sua aplicação usar ---
    def debug(self, message: str, details: str = None): self._log(LogLevel.DEBUG, message, details)
    def info(self, message: str, details: str = None): self._log(LogLevel.INFO, message, details)
    def success(self, message: str, details: str = None): self._log(LogLevel.SUCCESS, message, details)
    def warning(self, message: str, details: str = None): self._log(LogLevel.WARNING, message, details)
    def error(self, message: str, details: str = None): self._log(LogLevel.ERROR, message, details)
    def critical(self, message: str, details: str = None): self._log(LogLevel.CRITICAL, message, details)

    # --- Funções de gerenciamento do histórico ---
    def get_history(self) -> List[Dict[str, Any]]:
        return self.log_history

    def clear_history(self):
        self.log_history.clear()
        self.info("Histórico de logs foi limpo.")

# --- Instância Global ---
# Importe esta instância na sua aplicação Flask
log = LoggerComponent()