"""
Módulo de Atualização de Dados

Este módulo contém as funções responsáveis por atualizar os dados da aplicação
através de APIs externas (Siconfi), extraídas das rotas Flask originais.
"""

import requests
from datetime import datetime
from werkzeug.utils import secure_filename
from config import LOGGING_CONFIG
from database_models import RREO, RGF, db
from utils import calcular_bimestre_atual, calcula_quadrimestre_atual
import logging
import logging.config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

def configurar_logging():
    """Configura o sistema de logging da aplicação."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    return logger

logger = configurar_logging()


def _criar_chave_identificadora(item, chaves):
    """Cria uma tupla única para um item com base em um conjunto de chaves."""
    return tuple(item.get(chave) for chave in chaves)

def _atualizar_dados_siconfi(modelo_db, endpoint, params_base, periodo_params):
    """
    Função genérica para buscar, processar e salvar dados do Siconfi.

    Args:
        modelo_db: A classe do modelo SQLAlchemy (ex: RREO, RGF).
        endpoint (str): O endpoint da API (ex: 'rreo', 'rgf').
        params_base (dict): Parâmetros base da API que não mudam (esfera, ente, etc).
        periodo_params (list): Uma lista de dicionários, cada um contendo os parâmetros
                                de período para uma chamada de API (ano, anexo, etc).

    Returns:
        dict: Resultado da operação com sucessos e falhas.
    """
    TOTAL_INSERIDOS = 0
    sucessos, falhas = [], []
    # Define o conteúdo dos registros indesejados para filtragem
    if endpoint == 'rreo':
        conteudo_indesejado = ['%', 'SALDO']
    elif endpoint == 'rgf':
        conteudo_indesejado = []
    
    # Define as colunas que formam uma chave única para cada modelo
    chaves_unicas = {
        'RREO': ['exercicio', 'periodo', 'instituicao', 'anexo', 'rotulo', 'coluna', 'conta'],
        'RGF': ['exercicio', 'periodo', 'instituicao', 'co_poder', 'anexo', 'rotulo', 'coluna', 'cod_conta']
    }

    param_order = {
        'rreo': [
            'an_exercicio', 'nr_periodo', 'co_tipo_demonstrativo', 
            'no_anexo', 'co_esfera', 'id_ente'
        ],
        'rgf': [
            'an_exercicio', 'in_periodicidade', 'nr_periodo', 
            'co_tipo_demonstrativo', 'no_anexo', 'co_esfera', 
            'co_poder', 'id_ente'
        ]
    }

    chaves_identificadoras = chaves_unicas.get(modelo_db.__name__, [])

    for params_periodo in periodo_params:
        # Monta a URL completa com os parâmetros
        params_completos = {**params_base, **params_periodo}
        base_url = f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/{endpoint}"
        
        # Pega a lista ordenada de chaves para o endpoint atual
        ordem_correta = param_order.get(endpoint, [])
        
        # Constrói a query string (ex: "chave1=valor1&chave2=valor2")
        query_params = []
        for key in ordem_correta:
            if key in params_completos:
                query_params.append(f"{key}={params_completos[key]}")
        
        query_string = "&".join(query_params)
        
        # Monta a URL final
        url_completa = f"{base_url}?{query_string}"
        
        info_log = ", ".join([f"{k}={v}" for k, v in params_periodo.items()])
        logger.info(f"Consultando API para {url_completa} - {info_log}")
        
        try:
            print(f"Requisição para {url_completa} com params {params_base}")  # Linha de debug
            response = requests.get(url_completa, timeout=30)
            response.raise_for_status()
            data = response.json()
            items = data.get("items")
            if not items:
                falhas.append({**params_periodo, "motivo": "Nenhum dado encontrado."})
                continue
        
            # Filtra itens indesejados antes de qualquer processamento
            itens_filtrados = [
                item for item in items 
                if not any(item['coluna'].startswith(p) for p in conteudo_indesejado)
            ]

            if not itens_filtrados:
                sucessos.append(params_periodo) # Sucesso, mas sem dados novos
                continue
            logger.info(f"{len(itens_filtrados)} registros resgatados após filtragem inicial.")

            tamanho_lote = 50
            registros_inseridos_total = 0
            for i in range(0, len(itens_filtrados), tamanho_lote):
                lote_itens = itens_filtrados[i:i + tamanho_lote]
                
                logger.info(f"Processando lote {i//tamanho_lote + 1} com {len(lote_itens)} itens...")

                # 1. Cria um conjunto de chaves de identificação para cada lote 
                chaves_api_lote = {_criar_chave_identificadora(item, chaves_identificadoras) for item in lote_itens}

                # --- DEBUG ETAPA 3 ---
                print("\n--- DEBUG: ETAPA 3 (Chaves da API) ---")
                if chaves_api_lote:
                    primeira_chave_api = next(iter(chaves_api_lote))
                    print(f"Exemplo de chave da API: {primeira_chave_api}")
                    print("Tipos de dados na chave da API:")
                    for i, parte in enumerate(primeira_chave_api):
                        print(f"  - Parte {i} ({chaves_identificadoras[i]}): '{parte}' (Tipo: {type(parte)})")
                else:
                    print("Nenhuma chave gerada para o lote da API.")
                # --- FIM DEBUG ---

                filtros_db = []  # 2. Constrói uma consulta para buscar no banco os registros em lotes que correspondem a essas chaves.
                for chave_tupla in chaves_api_lote:
                    condicoes_and = [
                        (getattr(modelo_db, nome_chave).is_(None) if valor is None else getattr(modelo_db, nome_chave) == valor)
                        for nome_chave, valor in zip(chaves_identificadoras, chave_tupla)
                    ]
                    filtros_db.append(and_(*condicoes_and))

                if filtros_db: registros_existentes = db.session.query(modelo_db).filter(or_(*filtros_db)).all()
                else: registros_existentes = []

                chaves_existentes = {_criar_chave_identificadora(vars(reg), chaves_identificadoras) for reg in registros_existentes}

                # --- DEBUG ETAPA 4 ---
                print("\n--- DEBUG: ETAPA 4 (Chaves do Banco de Dados) ---")
                if chaves_existentes:
                    primeira_chave_db = next(iter(chaves_existentes))
                    print(f"Exemplo de chave do Banco: {primeira_chave_db}")
                    print("Tipos de dados na chave do Banco:")
                    for i, parte in enumerate(primeira_chave_db):
                        print(f"  - Parte {i} ({chaves_identificadoras[i]}): '{parte}' (Tipo: {type(parte)})")
                else:
                    print("Nenhuma chave correspondente encontrada no banco de dados.")
                # --- FIM DEBUG ---

                '''registros_novos_para_inserir = [
                    item for item in lote_itens
                    if _criar_chave_identificadora(item, chaves_identificadoras) not in chaves_existentes
                ]'''

                # --- DEBUG ETAPA 5 ---
                print("\n--- DEBUG: ETAPA 5 (Comparação) ---")
                registros_novos_para_inserir = []
                for item in lote_itens:
                    chave_api_item = _criar_chave_identificadora(item, chaves_identificadoras)
                    encontrado_no_db = chave_api_item in chaves_existentes
                    print(f"Verificando chave: {chave_api_item}")
                    print(f" -> Encontrada no DB? {encontrado_no_db}")
                    if not encontrado_no_db:
                        registros_novos_para_inserir.append(item)
                print(f"Resultado: {len(registros_novos_para_inserir)} registros marcados como novos para inserção.")
                # --- FIM DEBUG ---

                # Insere os novos registros em lote.
                if registros_novos_para_inserir:
                    # Transação atômica para a inserção
                    try:
                        db.session.bulk_insert_mappings(modelo_db, registros_novos_para_inserir)
                        db.session.commit() # Confirma a transação para este lote
                        logger.info(f"Lote salvo! {len(registros_novos_para_inserir)} novos registros inseridos.")
                        registros_inseridos_total += len(registros_novos_para_inserir)
                    except Exception as e_transacao:
                        logger.error(f"Erro ao salvar lote no banco de dados: {e_transacao}")
                        db.session.rollback() # Reverte a transação em caso de erro
                        raise e_transacao # Propaga o erro para o bloco principal
                
            logger.info(f"Importação para {info_log} concluída. Total de {registros_inseridos_total} registros inseridos.")
            sucessos.append(params_periodo)
            TOTAL_INSERIDOS += registros_inseridos_total
            
        except requests.exceptions.RequestException as e:
            falhas.append({**params_periodo, "motivo": f"Erro de requisição: {e}"})
        except SQLAlchemyError as e:
            db.session.rollback()
            falhas.append({**params_periodo, "motivo": f"Erro no banco: {str(e)}"})
        except Exception as e:
            db.session.rollback()
            falhas.append({**params_periodo, "motivo": f"Erro inesperado: {str(e)}"})

    logger.info(f"Processo de atualização para endpoint '{endpoint}' concluído. Total geral de registros inseridos: {TOTAL_INSERIDOS}")
    return sucessos, falhas


def atualizar_operacoes_rreo(status='now'):
    """
    Atualiza os dados da tabela RREO através da API do Siconfi.
    """
    try:
        # Definição dos períodos
        if status == 'now':
            anos = [datetime.now().year]
            bimestre = calcular_bimestre_atual() - 1 if calcular_bimestre_atual() > 1 else 1
        else:
            anos = list(range(2021, datetime.now().year)) # Corrigido para incluir o ano atual
            bimestre = 6

        # Parâmetros que não mudam
        params_base = {
            "co_tipo_demonstrativo": "RREO",
            "co_esfera": "E",
            "id_ente": 52
        }
        
        # Parâmetros que mudam a cada iteração (ano e anexo)
        periodo_params = []
        for ano in anos:
            for anexo in ["RREO-Anexo 01", "RREO-Anexo 02"]:
                periodo_params.append({
                    "an_exercicio": ano,
                    "nr_periodo": bimestre,
                    "no_anexo": anexo
                })
        
        # Chama a função genérica
        sucessos, falhas = _atualizar_dados_siconfi(RREO, 'rreo', params_base, periodo_params)

        if falhas:
            return {"message": "Importação RREO concluída com erros.", "sucessos": sucessos, "falhas": falhas, "status": "error"}

        return {"message": "Dados RREO importados com sucesso!", "sucessos": sucessos, "status": "success"}

    except Exception as e:
        logger.exception("Erro geral na atualização RREO")
        return {"message": f"Erro geral: {str(e)}", "sucessos": [], "falhas": [], "status": "error"}

def atualizar_operacoes_rgf(status='now'):
    """
    Atualiza os dados da tabela RGF através da API do Siconfi.
    """
    try:
        # Período
        if status == 'now':
            anos = [datetime.now().year]
            quadrimestre = calcula_quadrimestre_atual() -1 if calcula_quadrimestre_atual() > 1 else 1
        else:
            anos = list(range(2021, datetime.now().year)) # Corrigido para incluir o ano atual
            quadrimestre = 3
        
        # Parâmetros que não mudam
        params_base = {
            "in_periodicidade": "Q",
            "co_tipo_demonstrativo": "RGF",
            "co_esfera": "E",
            "id_ente": 52
        }

        # Parâmetros que mudam a cada iteração
        periodo_params = []
        for ano in anos:
            for anexo in ["RGF-Anexo 01", "RGF-Anexo 02"]:
                for poder in ["E"]:
                    periodo_params.append({
                        "an_exercicio": ano,
                        "nr_periodo": quadrimestre,
                        "no_anexo": anexo,
                        "co_poder": poder
                    })
        
        # Chama a função genérica
        sucessos, falhas = _atualizar_dados_siconfi(RGF, 'rgf', params_base, periodo_params)

        if falhas:
            return {"message": "Importação RGF concluída com erros.", "sucessos": sucessos, "falhas": falhas, "status": "error"}

        return {"message": "Dados RGF importados com sucesso!", "sucessos": sucessos, "status": "success"}

    except Exception as e:
        logger.exception("Erro geral na atualização RGF")
        return {"message": f"Erro geral: {str(e)}", "sucessos": [], "falhas": [], "status": "error"}


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

def configurar_banco_dados():
    """Configura e inicializa o banco de dados SQLAlchemy."""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Session = sessionmaker(bind=engine)
        db.session = Session()
        # Cria tabelas se não existirem
        from database_models import Base
        Base.metadata.create_all(engine)
        logger.info("Banco de dados configurado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar banco de dados: {e}")
        return False

if __name__ == "__main__":
    # Configura banco de dados
    if not configurar_banco_dados():
        print("Falha na configuração do banco de dados.")
        exit(1)

    print("Escolha a operação:")
    print("1 - Atualizar RREO")
    print("2 - Atualizar RGF")
    escolha = input("Digite o número da operação: ")

    if escolha == "1":
        resultado = atualizar_operacoes_rreo(status='past')
        print(resultado)
    elif escolha == "2":
        resultado = atualizar_operacoes_rgf(status='past')
        #print(resultado)
    else:
        print("Opção inválida.")