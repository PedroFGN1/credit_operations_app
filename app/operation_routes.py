from datetime import datetime
import os
from flask import Blueprint, current_app, jsonify, render_template, request, flash, redirect
import pandas as pd
from sqlalchemy import func
from app.models import DCRCL, RGF, RREO, Operacoes, db
from app.utils import allowed_file, bar_data, calcula_quadrimestre_atual, calcular_bimestre_atual, tratar_float, validation_credit_operation
from werkzeug.utils import secure_filename
from datetime import datetime
import requests

operation_bp = Blueprint('operation_bp', __name__, template_folder='templates')

@operation_bp.route('/dados_rreo', methods=['GET'])
def dados_rreo():
    # Obtendo o ano do request
    ano = request.args.get('ano', type=int)
    if not ano:
        ano = datetime.now().year # Valor padrão caso o ano não seja fornecido

    # Consultando a tabela RREO com filtro por ano
    rreo_data = RREO.query.filter_by(exercicio=ano).all()
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

    return jsonify({"data": data})

@operation_bp.route('/dados_rgf', methods=['GET'])
def dados_rgf():
    # Obtendo o ano do request
    ano = request.args.get('ano', type=int)
    if not ano:
        ano = datetime.now().year # Valor padrão caso o ano não seja fornecido

    # Consultando a tabela RREO com filtro por ano
    rgf_data = RGF.query.filter_by(exercicio=ano).all()
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

    return jsonify({"data": data})


# Rota para gerar o relatório filtrado por mês
@operation_bp.route('/painel_operacoes_credito', methods=['GET'], endpoint='operacoes_de_credito')
def painel_operacoes_credito():

    # Obtendo o ano do request
    ano = request.args.get('ano', type=int)
    if not ano:
        ano = datetime.now().year # Valor padrão caso o ano não seja fornecido

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

        if linha == 'regra_1':
        # Valores do ano anterior
            for natureza in [amortizacoes,inversoes,investimentos]:
                valor = (
                    db.session.query(func.sum(RREO.valor))
                    .filter(
                        RREO.exercicio == ano - 1,
                        RREO.coluna.in_(tipo_movimentacao),
                        RREO.conta.in_(natureza)
                    )
                    .scalar()
                ) or 0
            
                if natureza == amortizacoes:amortizacao = valor
                elif natureza == inversoes:inversao = valor
                elif natureza == investimentos:investimento = valor

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
                bg='bg-red-500'
            else :
                situacao = 'operação de crédito liberada!'
                bg='bg-[#009e3c]'

        elif linha == 'regra_2':
        # Valores do ano atual
            max_bimestre = db.session.query(func.max(RREO.periodo)).filter(RREO.exercicio==ano).scalar()
            for natureza in [amortizacoes,inversoes,investimentos]:
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

                if natureza == amortizacoes:amortizacao = valor
                elif natureza == inversoes:inversao = valor
                elif natureza == investimentos:investimento = valor

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
            situacao = ''
            
            try:
                requisitado = request.args.get('requisitado', type=float) or 0.0
                rcl = (db.session.query(func.sum(DCRCL.receita_corrente_liquida)).filter(DCRCL.ano == ano).scalar()) or 0
                apuracao = validation_credit_operation(float(requisitado), float(rcl), float(operacao), float(limiteOp))
                dados_barra = bar_data(requisitado, operacao, rcl, limiteOp)
            except Exception as e:
                f"Ocorreu um erro no tratamento dos dados! /n {e}", 400       


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

    # Regra de Fluxo
    # Valores do ano anterior para Dívida Consolidada Líquida e Receita Corrente Líquida
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
                RGF.conta.in_(['= RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)','RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)']
            ))
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
                RGF.conta.in_(['= RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)','RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (VI) = (IV - V)']
            ))
            .scalar()
        ) or 0

    # Regra de Contra-garantia
    # Valores do ano anterior para Dívida Consolidada Líquida e Receita Corrente Líquida
    max_ano = datetime.now().year
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
                RREO.periodo == calcular_bimestre_atual,
                RREO.coluna == 'Até o Bimestre (c)',
                RREO.conta == 'Impostos'
            )
            .scalar()
        ) or 0

        dsd = (
            (db.session.query(func.sum(RREO.valor))
            .filter(
                RREO.exercicio == ano,
                RREO.periodo == calcular_bimestre_atual,
                RREO.coluna == 'DOTAÇÃO ATUALIZADA (a)',
                RREO.conta == 'Serviço da Dívida Interna'
            )
            .scalar() or 0) 
            + 
            (db.session.query(func.sum(RREO.valor))
            .filter(
                RREO.exercicio == ano,
                RREO.periodo == calcular_bimestre_atual,
                RREO.coluna == 'DOTAÇÃO ATUALIZADA (a)',
                RREO.conta == 'Serviço da Dívida Externa'
            )
            .scalar() or 0)
        )

    return render_template('/operacoes_credito_refatorado.html', tabela=tabela, anos=anos, ano=ano, rcl=float(rcl), rcl_rgf=float(rcl_rgf), dcl_rgf=float(dcl_rgf), requisitado=float(requisitado), apuracao=apuracao, dados_barra=dados_barra, receitas_proprias=float(receitas_proprias), dsd=float(dsd))

@operation_bp.route('/importar_operacoes', methods=['GET', 'POST'])
def importar_operacoes():
    if request.method == 'POST':
        file = request.files['arquivo']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Ler o arquivo CSV
                df = pd.read_csv(filepath, sep=';', decimal=',', encoding='UTF-8')

                # Converte colunas numéricas de vírgula para ponto
                colunas_numericas = ['valor']
                for coluna in colunas_numericas:
                    df[coluna] = df[coluna].apply(lambda x: tratar_float(x) if pd.notna(x) else None)

                # Insere os dados no banco de dados
                for _, linha in df.iterrows():
                    operacao = Operacoes(
                        ano=linha['ano'],
                        bimestre=linha['bimestre'],
                        instituicao=linha['instituicao'],
                        movimentacao_contabil=linha['movimentacao_contabil'],
                        natureza_despesa_receita=linha['natureza_despesa_receita'],
                        valor=linha['valor']
                    )
                    db.session.add(operacao)

                db.session.commit()
                os.remove(filepath)
                flash("Os dados foram importados com sucesso para a tabela Operacoes!")
                return redirect('/')

            except Exception as e:
                db.session.rollback()
                flash("error", f"Erro ao importar dados: {e}")
                return redirect('/')

    return redirect('/')

@operation_bp.route('/atualizar_operacoes_rreo', methods=['GET','POST'])
def atualizar_operacoes_rreo():
    status = request.args.get('status', type=str)
    if not status:
        status = 'now'

    if status == 'now':
        anos = [datetime.now().year]
        bimestre = calcular_bimestre_atual()
    else:
        anos = list(range(2021, datetime.now().year))
        bimestre = 6
    
    anexos = ["RREO-Anexo 01", "RREO-Anexo 02"]
    esfera = "E"
    ente = 52

    sucessos = []
    falhas = []

    colunas_indesejadas = ['%', 'SALDO']

    with current_app.app_context():
        for ano in anos:
            for anexo in anexos:
                url = (f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
                       f"?an_exercicio={ano}&nr_periodo={bimestre}&co_tipo_demonstrativo=RREO"
                       f"&no_anexo={anexo}&co_esfera={esfera}&id_ente={ente}")

                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()

                    if not data.get("items"):
                        falhas.append({"ano": ano, "anexo": anexo, "motivo": "Nenhum dado encontrado."})
                        continue

                    for item in data["items"]:
                        print(f"Processando: {item}")  # Log para ver se os dados estão vindo
                        if any(item['coluna'].startswith(padrao) for padrao in colunas_indesejadas):
                            continue

                        existe = RREO.query.filter_by(
                            exercicio=item['exercicio'],
                            demonstrativo=item['demonstrativo'],
                            periodo=item['periodo'],
                            instituicao=item['instituicao'],
                            uf=item['uf'],
                            anexo=item['anexo'],
                            esfera=item['esfera'],
                            rotulo=item['rotulo'],
                            coluna=item['coluna'],
                            cod_conta=item['cod_conta'],
                            conta=item['conta']
                        ).first()

                        if not existe:
                            novo_registro = RREO(
                                exercicio=item['exercicio'],
                                demonstrativo=item['demonstrativo'],
                                periodo=item['periodo'],
                                instituicao=item['instituicao'],
                                uf=item['uf'],
                                anexo=item['anexo'],
                                esfera=item['esfera'],
                                rotulo=item['rotulo'],
                                coluna=item['coluna'],
                                cod_conta=item['cod_conta'],
                                conta=item['conta'],
                                valor=item['valor']
                            )
                            db.session.add(novo_registro)
                            print(f"Adicionado: {item['cod_conta']} para {ano}")
                            db.session.commit()
                    sucessos.append({"ano": ano, "anexo": anexo})

                except requests.exceptions.RequestException as e:
                    falhas.append({"ano": ano, "anexo": anexo, "motivo": str(e)})
                except Exception as e:
                    db.session.rollback()  # Rollback dentro do loop
                    falhas.append({"ano": ano, "anexo": anexo, "motivo": f"Erro inesperado: {str(e)}"})

    if falhas:
        return jsonify({"message": "Importação concluída com erros.", "sucessos": sucessos, "falhas": falhas}), 500
    return jsonify({"message": "Dados importados com sucesso!", "sucessos": sucessos})
  
@operation_bp.route('/atualizar_operacoes_rgf', methods=['GET','POST'])
def atualizar_operacoes_rgf():
    status = request.args.get('status', type=str)
    if not status:
        status = 'now'

    if status == 'now':
        anos = [datetime.now().year]
        periodo = 3
    else:
        anos = list(range(2014, datetime.now().year))
        periodo = 3
    
    anexos = ["RGF-Anexo 02"]
    poderes = ['E','L','J','M','D']
    esfera = "E"
    ente = 52
    periodicidade = 'Q'

    sucessos = []
    falhas = []

    colunas_indesejadas = ['*****']

    with current_app.app_context():
        for ano in anos:
            for anexo in anexos:
                for poder in poderes:
                    url = (f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt//rgf"
                        f"?an_exercicio={ano}&in_periodicidade={periodicidade}&nr_periodo={periodo}&co_tipo_demonstrativo=RGF"
                        f"&no_anexo={anexo}&co_esfera={esfera}&co_poder={poder}&id_ente={ente}")

                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        data = response.json()

                        if not data.get("items"):
                            falhas.append({"ano": ano, "anexo": anexo, "poder": poder, "motivo": "Nenhum dado encontrado."})
                            continue

                        for item in data["items"]:
                            print(f"Processando: {item}")  # Log para ver se os dados estão vindo
                            if any(item['coluna'].startswith(padrao) for padrao in colunas_indesejadas):
                                continue

                            existe = RGF.query.filter_by(
                                exercicio=item['exercicio'],
                                periodo=item['periodo'],
                                periodicidade=item['periodicidade'],
                                instituicao=item['instituicao'],
                                uf=item['uf'],
                                co_poder=item['co_poder'],
                                anexo=item['anexo'],
                                esfera=item['esfera'],
                                rotulo=item['rotulo'],
                                coluna=item['coluna'],
                                cod_conta=item['cod_conta'],
                                conta=item['conta']
                            ).first()

                            if not existe:
                                novo_registro = RGF(
                                    exercicio=item['exercicio'],
                                    periodo=item['periodo'],
                                    periodicidade=item['periodicidade'],
                                    instituicao=item['instituicao'],
                                    uf=item['uf'],
                                    co_poder=item['co_poder'],
                                    anexo=item['anexo'],
                                    esfera=item['esfera'],
                                    rotulo=item['rotulo'],
                                    coluna=item['coluna'],
                                    cod_conta=item['cod_conta'],
                                    conta=item['conta'],
                                    valor=item['valor']
                                )
                                
                                db.session.add(novo_registro)
                                print(f"Adicionado: {item['cod_conta']} para {ano}")
                                db.session.commit()
                        sucessos.append({"ano": ano, "anexo": anexo, "poder": poder})

                    except requests.exceptions.RequestException as e:
                        falhas.append({"ano": ano, "anexo": anexo, "poder": poder, "motivo": str(e)})
                    except Exception as e:
                        db.session.rollback()  # Rollback dentro do loop
                        falhas.append({"ano": ano, "anexo": anexo, "poder": poder, "motivo": f"Erro inesperado: {str(e)}"})

    if falhas:
        return jsonify({"message": "Importação concluída com erros.", "sucessos": sucessos, "falhas": falhas}), 500
    return jsonify({"message": "Dados importados com sucesso!", "sucessos": sucessos})