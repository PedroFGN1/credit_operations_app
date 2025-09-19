"""
Módulo de Atualização de Dados

Este módulo contém as funções responsáveis por atualizar os dados da aplicação
através de APIs externas (Siconfi), extraídas das rotas Flask originais.
"""

import os
import pandas as pd
import requests
from datetime import datetime
from werkzeug.utils import secure_filename
from database_models import RREO, RGF, Operacoes, db
from utils import allowed_file, tratar_float, calcular_bimestre_atual, calcula_quadrimestre_atual


def atualizar_operacoes_rreo(status='now'):
    """
    Atualiza os dados da tabela RREO através da API do Siconfi.
    
    Args:
        status (str): 'now' para dados atuais ou 'all' para dados históricos
        
    Returns:
        dict: Resultado da operação com sucessos e falhas
    """
    try:
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
                        print(f"Processando: {item}")
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
                    db.session.rollback()
                    falhas.append({"ano": ano, "anexo": anexo, "motivo": f"Erro inesperado: {str(e)}"})

        if falhas:
            return {"message": "Importação concluída com erros.", "sucessos": sucessos, "falhas": falhas, "status": "error"}
        return {"message": "Dados importados com sucesso!", "sucessos": sucessos, "status": "success"}
        
    except Exception as e:
        print(f"Erro geral na atualização RREO: {e}")
        return {"message": f"Erro geral: {str(e)}", "sucessos": [], "falhas": [], "status": "error"}


def atualizar_operacoes_rgf(status='now'):
    """
    Atualiza os dados da tabela RGF através da API do Siconfi.
    
    Args:
        status (str): 'now' para dados atuais ou 'all' para dados históricos
        
    Returns:
        dict: Resultado da operação com sucessos e falhas
    """
    try:
        if status == 'now':
            anos = [datetime.now().year]
            quadrimestre = calcula_quadrimestre_atual()
        else:
            anos = list(range(2021, datetime.now().year))
            quadrimestre = 3
        
        anexos = ["RGF-Anexo 01", "RGF-Anexo 02"]
        poderes = ["E"]  # Executivo
        esfera = "E"
        ente = 52

        sucessos = []
        falhas = []

        colunas_indesejadas = ['%', 'SALDO']

        for ano in anos:
            for anexo in anexos:
                for poder in poderes:
                    url = (f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"
                           f"?an_exercicio={ano}&nr_periodo={quadrimestre}&co_tipo_demonstrativo=RGF"
                           f"&no_anexo={anexo}&co_esfera={esfera}&co_poder={poder}&id_ente={ente}")

                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        data = response.json()

                        if not data.get("items"):
                            falhas.append({"ano": ano, "anexo": anexo, "poder": poder, "motivo": "Nenhum dado encontrado."})
                            continue

                        for item in data["items"]:
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
                        db.session.rollback()
                        falhas.append({"ano": ano, "anexo": anexo, "poder": poder, "motivo": f"Erro inesperado: {str(e)}"})

        if falhas:
            return {"message": "Importação concluída com erros.", "sucessos": sucessos, "falhas": falhas, "status": "error"}
        return {"message": "Dados importados com sucesso!", "sucessos": sucessos, "status": "success"}
        
    except Exception as e:
        print(f"Erro geral na atualização RGF: {e}")
        return {"message": f"Erro geral: {str(e)}", "sucessos": [], "falhas": [], "status": "error"}


def importar_operacoes_csv(arquivo_path):
    """
    Importa operações de um arquivo CSV.
    
    Args:
        arquivo_path (str): Caminho para o arquivo CSV
        
    Returns:
        dict: Resultado da operação
    """
    try:
        if not allowed_file(arquivo_path):
            return {"message": "Tipo de arquivo não permitido.", "status": "error"}

        # Ler o arquivo CSV
        df = pd.read_csv(arquivo_path, sep=';', decimal=',', encoding='UTF-8')

        # Converte colunas numéricas de vírgula para ponto
        colunas_numericas = ['valor']
        for coluna in colunas_numericas:
            df[coluna] = df[coluna].apply(lambda x: tratar_float(x) if pd.notna(x) else None)

        # Insere os dados no banco de dados
        registros_inseridos = 0
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
            registros_inseridos += 1

        db.session.commit()
        
        # Remove o arquivo após importação
        if os.path.exists(arquivo_path):
            os.remove(arquivo_path)
            
        return {
            "message": f"Os dados foram importados com sucesso! {registros_inseridos} registros inseridos.",
            "registros": registros_inseridos,
            "status": "success"
        }

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao importar dados: {e}")
        return {"message": f"Erro ao importar dados: {str(e)}", "status": "error"}


def salvar_arquivo_upload(arquivo, upload_folder):
    """
    Salva um arquivo enviado pelo usuário.
    
    Args:
        arquivo: Arquivo enviado
        upload_folder (str): Pasta de destino
        
    Returns:
        str: Caminho do arquivo salvo ou None se houver erro
    """
    try:
        if arquivo and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            filepath = os.path.join(upload_folder, filename)
            arquivo.save(filepath)
            return filepath
        return None
        
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return None
