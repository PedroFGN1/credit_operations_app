"""
Aplicação Principal - Simulador de Operações de Crédito v2

Este é o arquivo principal da aplicação. Atua como a "ponte" entre o
backend (motor de regras, acesso a dados) e o frontend (JavaScript/Eel).
"""

import eel
from sqlalchemy import func

# Módulos da nossa arquitetura
from src.simulador.rule_engine_new import analisar_operacao
from src.simulador.data_updater import atualizar_operacoes_rreo, atualizar_operacoes_rgf
from src.simulador.database_models import db, RREO

# Módulos de configuração
from src.simulador.config import (
    EEL_WEB_FOLDER, EEL_SIZE, EEL_POSITION, APP_NAME, APP_VERSION, 
    criar_diretorios, configurar_banco_dados, configurar_logging
) 

# --- CONFIGURAÇÃO INICIAL DA APLICAÇÃO ---

logger = configurar_logging()
criar_diretorios()

if not configurar_banco_dados(logger):
    logger.error("Falha na configuração do banco de dados. Encerrando aplicação.")
    exit(1)


# ========== FUNÇÕES EXPOSTAS PARA O FRONTEND (API INTERNA) ==========

@eel.expose
def obter_dados_iniciais():
    """
    Busca informações iniciais para popular o frontend, como a lista de anos
    disponíveis para análise no banco de dados.
    """
    try:
        logger.info("Buscando dados iniciais para o frontend...")
        # Busca todos os anos distintos presentes na tabela RREO
        anos_query = db.session.query(RREO.exercicio).distinct().order_by(RREO.exercicio.desc()).all()
        anos_disponiveis = [ano[0] for ano in anos_query]
        logger.info(f"Anos disponíveis encontrados: {anos_disponiveis}")
        
        return {
            "status": "sucesso",
            "anos_disponiveis": anos_disponiveis
        }
    except Exception as e:
        logger.error(f"Erro ao obter dados iniciais: {e}")
        return {"status": "erro", "mensagem": str(e), "anos_disponiveis": []}

@eel.expose
def analisar_operacao_py(ano: int, valor_requisitado: float):
    """
    Ponto de entrada principal para executar o motor de regras e retornar a análise completa.
    """
    try:
        logger.info(f"Recebido pedido de análise - Ano: {ano}, Valor: {valor_requisitado}")
        # Esta chamada agora invoca nosso orquestrador inteligente
        resultado = analisar_operacao(ano, valor_requisitado)
        logger.info("Análise via orquestrador concluída com sucesso.")
        return resultado
    except Exception as e:
        logger.error(f"Erro ao executar 'analisar_operacao': {e}", exc_info=True)
        return {"status": "erro", "mensagem": f"Ocorreu um erro crítico no backend: {e}"}

@eel.expose
def atualizar_rreo_py(status='now'):
    """
    Dispara a rotina de atualização dos dados do RREO a partir da API do Siconfi.
    """
    try:
        logger.info(f"Disparando atualização RREO - Status: {status}")
        resultado = atualizar_operacoes_rreo(status)
        logger.info("Atualização RREO concluída.")
        return resultado
    except Exception as e:
        logger.error(f"Erro na atualização RREO: {e}", exc_info=True)
        return {"message": f"Erro: {str(e)}", "status": "error"}

@eel.expose
def atualizar_rgf_py(status='now'):
    """
    Dispara a rotina de atualização dos dados do RGF a partir da API do Siconfi.
    """
    try:
        logger.info(f"Disparando atualização RGF - Status: {status}")
        resultado = atualizar_operacoes_rgf(status)
        logger.info("Atualização RGF concluída.")
        return resultado
    except Exception as e:
        logger.error(f"Erro na atualização RGF: {e}", exc_info=True)
        return {"message": f"Erro: {str(e)}", "status": "error"}

@eel.expose
def obter_info_app():
    """
    Retorna informações básicas sobre a aplicação.
    """
    return { "nome": APP_NAME, "versao": APP_VERSION }


# As funções obter_dados_rreo_py e obter_dados_rgf_py foram removidas,
# pois a nova função analisar_operacao_py já orquestra toda a busca de dados
# necessária de forma interna e mais eficiente.

# A função de importação de CSV pode ser adicionada aqui se você
# planeja ter um botão no frontend para upload de arquivos.

def main():
    """Função principal para inicializar a aplicação Eel."""
    try:
        eel.init(str(EEL_WEB_FOLDER))
        logger.info(f"Aplicação '{APP_NAME} v{APP_VERSION}' iniciando...")
        eel.start('main.html', size=EEL_SIZE, position=EEL_POSITION)
    except Exception as e:
        logger.critical(f"Não foi possível iniciar a aplicação Eel: {e}", exc_info=True)

if __name__ == '__main__':
    main()
