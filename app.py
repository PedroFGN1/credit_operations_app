"""
Aplicação Principal - Simulador de Operações de Crédito v2

Este é o arquivo principal da aplicação migrada de Flask para Eel.
Contém a inicialização do Eel, configuração do banco de dados e
exposição das funções Python para o frontend JavaScript.
"""

import eel
import logging
import logging.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_models import Base, db
from rule_engine import analisar_operacao, obter_dados_rreo, obter_dados_rgf
from data_updater import atualizar_operacoes_rreo, atualizar_operacoes_rgf
from config import (
    DATABASE_URL, EEL_WEB_FOLDER, EEL_SIZE, EEL_POSITION, 
    APP_NAME, APP_VERSION, LOGGING_CONFIG, criar_diretorios, BASE_DIR
) 


def configurar_logging():
    """Configura o sistema de logging da aplicação."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info(f"Iniciando {APP_NAME} v{APP_VERSION}")
    return logger


def configurar_banco_dados():
    """Configura e inicializa o banco de dados SQLAlchemy."""
    try:
        # Criar engine do SQLAlchemy
        engine = create_engine(DATABASE_URL, echo=False)
        
        # Configurar sessão global
        Session = sessionmaker(bind=engine)
        db.session = Session()
        
        # Criar tabelas se não existirem
        Base.metadata.create_all(engine)
        
        logger.info("Banco de dados configurado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao configurar banco de dados: {e}")
        return False


# Configurar logging
logger = configurar_logging()

# Criar diretórios necessários
criar_diretorios()

# Configurar banco de dados
if not configurar_banco_dados():
    logger.error("Falha na configuração do banco de dados. Encerrando aplicação.")
    exit(1)


# ========== FUNÇÕES EXPOSTAS PARA O FRONTEND ==========

@eel.expose
def analisar_operacao_py(ano, valor_requisitado=0.0):
    """
    Função exposta para análise de operações de crédito.
    
    Args:
        ano (int): Ano da operação
        valor_requisitado (float): Valor requisitado
        
    Returns:
        dict: Dados da análise
    """
    try:
        logger.info(f"Analisando operação - Ano: {ano}, Valor: {valor_requisitado}")
        resultado = analisar_operacao(ano, valor_requisitado)
        logger.info("Análise concluída com sucesso")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na análise da operação: {e}")
        return {"erro": str(e)}

'''
@eel.expose
def obter_dados_rreo_py(ano=None):
    """
    Função exposta para obter dados RREO.
    
    Args:
        ano (int): Ano para filtrar
        
    Returns:
        dict: Dados RREO
    """
    try:
        logger.info(f"Obtendo dados RREO - Ano: {ano}")
        resultado = obter_dados_rreo(ano)
        logger.info("Dados RREO obtidos com sucesso")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao obter dados RREO: {e}")
        return {"data": [], "erro": str(e)}

'''
'''
@eel.expose
def obter_dados_rgf_py(ano=None):
    """
    Função exposta para obter dados RGF.
    
    Args:
        ano (int): Ano para filtrar
        
    Returns:
        dict: Dados RGF
    """
    try:
        logger.info(f"Obtendo dados RGF - Ano: {ano}")
        resultado = obter_dados_rgf(ano)
        logger.info("Dados RGF obtidos com sucesso")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao obter dados RGF: {e}")
        return {"data": [], "erro": str(e)}

'''
@eel.expose
def atualizar_rreo_py(status='now'):
    """
    Função exposta para atualizar dados RREO via API.
    
    Args:
        status (str): 'now' ou 'all'
        
    Returns:
        dict: Resultado da atualização
    """
    try:
        logger.info(f"Atualizando dados RREO - Status: {status}")
        resultado = atualizar_operacoes_rreo(status)
        logger.info("Atualização RREO concluída")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na atualização RREO: {e}")
        return {"message": f"Erro: {str(e)}", "status": "error"}


@eel.expose
def atualizar_rgf_py(status='now'):
    """
    Função exposta para atualizar dados RGF via API.
    
    Args:
        status (str): 'now' ou 'all'
        
    Returns:
        dict: Resultado da atualização
    """
    try:
        logger.info(f"Atualizando dados RGF - Status: {status}")
        resultado = atualizar_operacoes_rgf(status)
        logger.info("Atualização RGF concluída")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na atualização RGF: {e}")
        return {"message": f"Erro: {str(e)}", "status": "error"}

'''
@eel.expose
def importar_csv_py(arquivo_path):
    """
    Função exposta para importar dados de CSV.
    
    Args:
        arquivo_path (str): Caminho do arquivo
        
    Returns:
        dict: Resultado da importação
    """
    try:
        logger.info(f"Importando CSV: {arquivo_path}")
        resultado = importar_operacoes_csv(arquivo_path)
        logger.info("Importação CSV concluída")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na importação CSV: {e}")
        return {"message": f"Erro: {str(e)}", "status": "error"}

'''
@eel.expose
def obter_info_app():
    """
    Função exposta para obter informações da aplicação.
    
    Returns:
        dict: Informações da aplicação
    """
    return {
        "nome": APP_NAME,
        "versao": APP_VERSION,
        "status": "ativo"
    }


def main():
    """Função principal para inicializar a aplicação Eel."""
    try:
        logger.info("Inicializando interface Eel")
        
        # Inicializar Eel
        eel.init(str(BASE_DIR / EEL_WEB_FOLDER))
        
        # Iniciar aplicação
        logger.info(f"Iniciando aplicação em {EEL_WEB_FOLDER}/main.html")
        eel.start(
            'main.html',
            size=EEL_SIZE,
            position=EEL_POSITION,
            disable_cache=True
        )
        
    except Exception as e:
        logger.error(f"Erro ao inicializar aplicação: {e}")
        raise


if __name__ == '__main__':
    main()
