"""
Aplicação Principal - Simulador de Operações de Crédito v2

Este é o arquivo principal da aplicação. Atua como a "ponte" entre o
backend (motor de regras, acesso a dados) e o frontend (JavaScript/Eel).
"""

import eel
from sqlalchemy import func

# Módulos da nossa arquitetura
from src.simulador.rule_engine import analisar_operacao
from src.simulador.data_updater import atualizar_operacoes_rreo, atualizar_operacoes_rgf
from src.simulador.database_models import db, RREO
from src.simulador.logger import log

# Módulos de configuração
from src.simulador.config import (
    EEL_WEB_FOLDER, EEL_SIZE, EEL_POSITION, APP_NAME, APP_VERSION, 
    criar_diretorios, configurar_banco_dados
) 

# --- CONFIGURAÇÃO INICIAL DA APLICAÇÃO ---

criar_diretorios()

if not configurar_banco_dados(log):
    log.error("Falha na configuração do banco de dados. Encerrando aplicação.")
    exit(1)

# ========== FUNÇÕES DE LOGGING EXPOSTAS ==========

@eel.expose
def get_all_logs():
    return log.get_all_logs()

@eel.expose
def clear_logs():
    log.clear_logs()

# ========== FUNÇÕES EXPOSTAS PARA O FRONTEND (API INTERNA) ==========

@eel.expose
def obter_dados_iniciais():
    """
    Busca informações iniciais para popular o frontend, como a lista de anos
    disponíveis para análise no banco de dados.
    """
    try:
        log.info("Buscando dados iniciais para o frontend.", modulo="app.py", funcao="obter_dados_iniciais")
        # Busca todos os anos distintos presentes na tabela RREO
        anos_query = db.session.query(RREO.exercicio).distinct().order_by(RREO.exercicio.desc()).all()
        anos_disponiveis = [ano[0] for ano in anos_query]
        log.success(f"Anos disponíveis encontrados: {len(anos_disponiveis)}, Primeiro ano: {(anos_disponiveis[-1:])}, Último ano: {(anos_disponiveis[:1])}", modulo="app.py", funcao="obter_dados_iniciais", anos=anos_disponiveis)
        
        return {
            "status": "sucesso",
            "anos_disponiveis": anos_disponiveis
        }
    except Exception as e:
        log.error(f"Erro ao obter dados iniciais: {e}")
        return {"status": "erro", "mensagem": str(e), "anos_disponiveis": []}

@eel.expose
def analisar_operacao_py(ano: int, valor_requisitado: float):
    """
    Ponto de entrada principal para executar o motor de regras e retornar a análise completa.
    """
    try:
        log.info("Recebido pedido de análise do frontend.", modulo="app.py", funcao="analisar_operacao_py", ano=ano, valor_requisitado=valor_requisitado)
        # Esta chamada agora invoca nosso orquestrador inteligente
        resultado = analisar_operacao(ano, valor_requisitado)
        log.success("Análise via orquestrador concluída com sucesso.")
        return resultado
    except Exception as e:
        log.error("Erro ao executar 'analisar_operacao'", details=str(e), modulo="app.py", funcao="analisar_operacao_py", traceback=True)
        return {"status": "erro", "mensagem": f"Ocorreu um erro crítico no backend: {e}"}

@eel.expose
def atualizar_rreo_py(status='now'):
    """
    Dispara a rotina de atualização dos dados do RREO a partir da API do Siconfi.
    """
    try:
        log.info(f"Disparando atualização RREO.", modulo="app.py", funcao="atualizar_rreo_py", status=status)
        resultado = atualizar_operacoes_rreo(status)
        log.success("Atualização RREO concluída.", modulo="app.py", funcao="atualizar_rreo_py", status=status)
        return resultado
    except Exception as e:
        log.error(f"Erro na atualização RREO:", details=str(e), modulo="app.py", funcao="atualizar_rreo_py", traceback=True)
        return {"message": f"Erro: {str(e)}", "status": "error"}

@eel.expose
def atualizar_rgf_py(status='now'):
    """
    Dispara a rotina de atualização dos dados do RGF a partir da API do Siconfi.
    """
    try:
        log.info(f"Disparando atualização RGF.", modulo="app.py", funcao="atualizar_rgf_py", status=status)
        resultado = atualizar_operacoes_rgf(status)
        log.success("Atualização RGF concluída.", modulo="app.py", funcao="atualizar_rgf_py", status=status)
        return resultado
    except Exception as e:
        log.error(f"Erro na atualização RGF:", details=str(e), modulo="app.py", funcao="atualizar_rgf_py", traceback=True)
        return {"message": f"Erro: {str(e)}", "status": "error"}

@eel.expose
def obter_info_app():
    """
    Retorna informações básicas sobre a aplicação.
    """
    return { "nome": APP_NAME, "versao": APP_VERSION }


def main():
    """Função principal para inicializar a aplicação Eel."""
    try:
        eel.init(str(EEL_WEB_FOLDER))
        log.info(f"Aplicação '{APP_NAME} v{APP_VERSION}' iniciando...")
        eel.start('main.html', size=EEL_SIZE, position=EEL_POSITION)
    except Exception as e:
        log.critical(f"Não foi possível iniciar a aplicação Eel:", details=str(e), modulo="app.py", funcao="main", traceback=True)

if __name__ == '__main__':
    main()
