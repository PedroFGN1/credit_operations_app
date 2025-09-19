"""
Módulo de Motor de Regras para Simulação de Operações de Crédito

Este módulo contém toda a lógica de negócio para análise e validação de operações de crédito,
extraída das rotas Flask originais e refatorada para uso com Eel.
"""

from datetime import datetime
from sqlalchemy import func
from database_models import DCRCL, RGF, RREO, db
from utils import validation_credit_operation, bar_data, calcula_quadrimestre_atual, calcular_bimestre_atual


def analisar_operacao(ano, valor_requisitado=0.0):
    """
    Analisa uma operação de crédito com base no ano e valor requisitado.
    
    Args:
        ano (int): Ano da operação
        valor_requisitado (float): Valor requisitado para a operação
        
    Returns:
        dict: Dicionário com todos os dados necessários para o frontend
    """
    try:
        if not ano:
            ano = datetime.now().year
            
        anos = [ano for ano in range(2015, 2030)]
        
        # Definindo os tipos de pagamento para cada linha
        filtros = {
            "regra_1": {
                'movimentacao_contabil': ['DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)', 'INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)'],
                'amortizacao': ['AMORTIZAÇÃO DA DÍVIDA'],
                'inversao': ['INVERSÕES FINANCEIRAS'],
                'investimento': ['INVESTIMENTOS'],
                'operacoes': ['OPERAÇÕES DE CRÉDITO'],
            },
            "regra_2": {
                'movimentacao_contabil': ['DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)', 'INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)'],
                'amortizacao': ['AMORTIZAÇÃO DA DÍVIDA'],
                'inversao': ['INVERSÕES FINANCEIRAS'],
                'investimento': ['INVESTIMENTOS'],
                'operacoes': ['OPERAÇÕES DE CRÉDITO'],
            },
        }

        tabela = []
        rcl = 0
        apuracao = {}
        dados_barra = {}

        # Gerando os dados para cada linha
        for linha, config in filtros.items():
            tipo_movimentacao = config["movimentacao_contabil"]
            amortizacoes = config["amortizacao"]
            inversoes = config["inversao"]
            investimentos = config["investimento"]
            operacoes = config["operacoes"]
            
            # Inicializa as variáveis
            amortizacao = 0
            inversao = 0
            investimento = 0
            operacao = 0
            limiteOp = 0
            despesas_capital = 0
            situacao = ''
            bg = ''

            if linha == 'regra_1':
                # Valores do ano anterior
                for natureza in [amortizacoes, inversoes, investimentos]:
                    valor = (
                        db.session.query(func.sum(RREO.valor))
                        .filter(
                            RREO.exercicio == ano - 1,
                            RREO.coluna.in_(tipo_movimentacao),
                            RREO.conta.in_(natureza)
                        )
                        .scalar()
                    ) or 0
                
                    if natureza == amortizacoes:
                        amortizacao = valor
                    elif natureza == inversoes:
                        inversao = valor
                    elif natureza == investimentos:
                        investimento = valor

                operacao = (
                    db.session.query(func.sum(RREO.valor))
                    .filter(
                        RREO.exercicio == ano-1,
                        RREO.coluna.in_(['Até o Bimestre (c)']),
                        RREO.conta.in_(operacoes)
                    )
                    .scalar()
                ) or 0
                
                despesas_capital = sum([amortizacao, inversao, investimento])
                limiteOp = despesas_capital - operacao
                
                if limiteOp < 0:
                    situacao = 'operação de crédito negada!'
                    bg = 'bg-red-500'
                else:
                    situacao = 'operação de crédito liberada!'
                    bg = 'bg-[#009e3c]'

            elif linha == 'regra_2':
                # Valores do ano atual
                max_bimestre = db.session.query(func.max(RREO.periodo)).filter(RREO.exercicio==ano).scalar()
                
                for natureza in [amortizacoes, inversoes, investimentos]:
                    valor = (
                        db.session.query(func.sum(RREO.valor))
                        .filter(
                            RREO.exercicio == ano,
                            RREO.coluna.in_(tipo_movimentacao),
                            RREO.conta.in_(natureza),
                            RREO.periodo == max_bimestre
                        )
                        .scalar()
                    ) or 0

                    if natureza == amortizacoes:
                        amortizacao = valor
                    elif natureza == inversoes:
                        inversao = valor
                    elif natureza == investimentos:
                        investimento = valor

                operacao = (
                    db.session.query(func.sum(RREO.valor))
                    .filter(
                        RREO.exercicio == ano,
                        RREO.coluna.in_(['PREVISÃO ATUALIZADA (a)']),
                        RREO.conta.in_(operacoes)
                    )
                    .scalar()
                ) or 0

                despesas_capital = sum([amortizacao, inversao, investimento])
                limiteOp = despesas_capital - operacao
                
                try:
                    rcl = (db.session.query(func.sum(DCRCL.receita_corrente_liquida)).filter(DCRCL.ano == ano).scalar()) or 0
                    apuracao = validation_credit_operation(float(valor_requisitado), float(rcl), float(operacao), float(limiteOp))
                    dados_barra = bar_data(valor_requisitado, operacao, rcl, limiteOp)
                except Exception as e:
                    print(f"Erro no tratamento dos dados: {e}")

            # Adicionando dados da linha à tabela
            tabela.append({
                'regra': linha,
                'amortizacao': amortizacao,
                'inversao': inversao,
                'investimento': investimento,
                'operacao_credito': float(operacao),
                'limiteOp': limiteOp,
                'despesas_capital': despesas_capital,
                'situacao': situacao,
                'bg': bg,
            })

        # Regra de Fluxo - Valores RGF
        max_ano = datetime.now().year
        max_ano_quadrimestre = (db.session.query(func.max(RGF.exercicio)).filter(RGF.periodo==calcula_quadrimestre_atual(),RGF.exercicio==max_ano).scalar()) or 0
        
        if max_ano_quadrimestre == 0:
            dcl_rgf = (
                db.session.query(func.sum(RGF.valor))
                .filter(
                    RGF.exercicio == ano,
                    RGF.coluna == 'Até o 3º Quadrimestre',
                    RGF.conta == 'DÍVIDA CONSOLIDADA LÍQUIDA (DCL) (III) = (I - II)'
                )
                .scalar()
            ) or 0

            rcl_rgf = (
                db.session.query(func.sum(RGF.valor))
                .filter(
                    RGF.exercicio == ano,
                    RGF.coluna == 'Até o 3º Quadrimestre',
                    RGF.conta.in_(['= RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)','RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)'])
                )
                .scalar()
            ) or 0
        else:
            dcl_rgf = (
                db.session.query(func.sum(RGF.valor))
                .filter(
                    RGF.exercicio == ano,
                    RGF.coluna == 'Até o ' + str(calcula_quadrimestre_atual()) + 'º Quadrimestre',
                    RGF.conta == 'DÍVIDA CONSOLIDADA LÍQUIDA (DCL) (III) = (I - II)'
                )
                .scalar()
            ) or 0

            rcl_rgf = (
                db.session.query(func.sum(RGF.valor))
                .filter(
                    RGF.exercicio == ano,
                    RGF.coluna == 'Até o ' + str(calcula_quadrimestre_atual()) + 'º Quadrimestre',
                    RGF.conta.in_(['= RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)','RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)'])
                )
                .scalar()
            ) or 0

        # Regra de Contra-garantia - Valores RREO
        max_ano_bimestre = (db.session.query(func.max(RREO.exercicio)).filter(RREO.periodo==calcular_bimestre_atual(),RREO.exercicio==max_ano).scalar()) or 0
        
        if max_ano_bimestre == 0:
            receitas_proprias = (
                db.session.query(func.sum(RREO.valor))
                .filter(
                    RREO.exercicio == ano,
                    RREO.periodo == 6,
                    RREO.coluna == 'Até o Bimestre (c)',
                    RREO.conta == 'Impostos'
                )
                .scalar()
            ) or 0

            dsd = (
                (db.session.query(func.sum(RREO.valor))
                .filter(
                    RREO.exercicio == ano,
                    RREO.periodo == 6,
                    RREO.coluna == 'DOTAÇÃO ATUALIZADA (a)',
                    RREO.conta == 'Serviço da Dívida Interna'
                )
                .scalar() or 0)
                +
                (db.session.query(func.sum(RREO.valor))
                .filter(
                    RREO.exercicio == ano,
                    RREO.periodo == 6,
                    RREO.coluna == 'DOTAÇÃO ATUALIZADA (a)',
                    RREO.conta == 'Serviço da Dívida Externa'
                )
                .scalar() or 0)
            )
        else:
            receitas_proprias = (
                db.session.query(func.sum(RREO.valor))
                .filter(
                    RREO.exercicio == ano,
                    RREO.periodo == calcular_bimestre_atual(),
                    RREO.coluna == 'Até o Bimestre (c)',
                    RREO.conta == 'Impostos'
                )
                .scalar()
            ) or 0

            dsd = (
                (db.session.query(func.sum(RREO.valor))
                .filter(
                    RREO.exercicio == ano,
                    RREO.periodo == calcular_bimestre_atual(),
                    RREO.coluna == 'DOTAÇÃO ATUALIZADA (a)',
                    RREO.conta == 'Serviço da Dívida Interna'
                )
                .scalar() or 0) 
                + 
                (db.session.query(func.sum(RREO.valor))
                .filter(
                    RREO.exercicio == ano,
                    RREO.periodo == calcular_bimestre_atual(),
                    RREO.coluna == 'DOTAÇÃO ATUALIZADA (a)',
                    RREO.conta == 'Serviço da Dívida Externa'
                )
                .scalar() or 0)
            )

        # Retorna todos os dados necessários para o frontend
        return {
            'tabela': tabela,
            'anos': anos,
            'ano': ano,
            'rcl': float(rcl),
            'rcl_rgf': float(rcl_rgf),
            'dcl_rgf': float(dcl_rgf),
            'requisitado': float(valor_requisitado),
            'apuracao': apuracao,
            'dados_barra': dados_barra,
            'receitas_proprias': float(receitas_proprias),
            'dsd': float(dsd)
        }
        
    except Exception as e:
        print(f"Erro na análise da operação: {e}")
        return {
            'erro': f"Erro na análise da operação: {str(e)}",
            'tabela': [],
            'anos': [],
            'ano': ano,
            'rcl': 0,
            'rcl_rgf': 0,
            'dcl_rgf': 0,
            'requisitado': 0,
            'apuracao': {},
            'dados_barra': {},
            'receitas_proprias': 0,
            'dsd': 0
        }


def obter_dados_rreo(ano=None):
    """
    Obtém dados da tabela RREO filtrados por ano.
    
    Args:
        ano (int): Ano para filtrar os dados
        
    Returns:
        dict: Dados formatados para exibição
    """
    try:
        if not ano:
            ano = datetime.now().year

        rreo_data = db.session.query(RREO).filter_by(exercicio=ano).all()
        data = [
            {
                "id": item.id,
                "exercicio": item.exercicio,
                "periodo": item.periodo,
                "anexo": item.anexo,
                "coluna": item.coluna,
                "conta": item.conta,
                "valor": f"R$ {item.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            }
            for item in rreo_data
        ]

        return {"data": data}
        
    except Exception as e:
        print(f"Erro ao obter dados RREO: {e}")
        return {"data": [], "erro": str(e)}


def obter_dados_rgf(ano=None):
    """
    Obtém dados da tabela RGF filtrados por ano.
    
    Args:
        ano (int): Ano para filtrar os dados
        
    Returns:
        dict: Dados formatados para exibição
    """
    try:
        if not ano:
            ano = datetime.now().year

        rgf_data = db.session.query(RGF).filter_by(exercicio=ano).all()
        data = [
            {
                "id": item.id,
                "exercicio": item.exercicio,
                "periodo": item.periodo,
                "anexo": item.anexo,
                "coluna": item.coluna,
                "conta": item.conta,
                "valor": f"R$ {item.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            }
            for item in rgf_data
        ]

        return {"data": data}
        
    except Exception as e:
        print(f"Erro ao obter dados RGF: {e}")
        return {"data": [], "erro": str(e)}
