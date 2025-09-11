from datetime import datetime
import math
import re
import pandas as pd

def tratar_data(valor):
    """
    Converte datas do formato '1/1/2024' para o padrão ISO ('2024-01-01').
    """
    try:
        return datetime.strptime(valor, '%d/%m/%Y').date()
    except (ValueError, TypeError):
        return None  # Retorna None se a data for inválida

def tratar_float(valor):
    """
    Converte números do formato '123.456.789,12' para float padrão.
    """
    try:
        if isinstance(valor, str):
            valor = valor.replace('.', '').replace(',', '.')
        return float(valor)
    except (ValueError, TypeError):
        return None  # Retorna None se o valor for inválido    

def separador_milhar(value, locale="national", decimals=0):
    """
    Formata um número com separador de milhar no formato nacional ou internacional
    e permite especificar o número de casas decimais.

    Args:
        value (float): O número a ser formatado.
        locale (str): O formato desejado: "national" (BR) ou "international" (US).
        decimals (int): O número de casas decimais a serem exibidas.

    Returns:
        str: O número formatado.
    """
    try:
        # Confirma que o valor é numérico
        number = float(value)

        # Define o formato com casas decimais ajustáveis
        format_str = f"{number:,.{decimals}f}"

        if locale == "national":  # Formato Brasileiro (11.454,12)
            return format_str.replace(",", "X").replace(".", ",").replace("X", ".")
        elif locale == "international":  # Formato Internacional (11,454.12)
            return format_str
        else:
            raise ValueError("O argumento 'locale' deve ser 'national' ou 'international'.")
    except (ValueError, TypeError):
        return "Valor inválido"
    
# Função para verificar extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']

def detectar_formato_numerico(amostra):
    """
    Detecta o formato decimal e de milhar com base em uma amostra.
    """
    padrao_nacional = re.compile(r'\d{1,3}\.\d{3},\d{1,2}')  # Ex: 1.234,56
    padrao_internacional = re.compile(r'\d{1,3},\d{3}\.\d{1,2}')  # Ex: 1,234.56
    
    for valor in amostra:
        if pd.isnull(valor):
            continue
        if padrao_nacional.match(str(valor)):
            return {'decimal': ',', 'thousands': '.'}
        if padrao_internacional.match(str(valor)):
            return {'decimal': '.', 'thousands': ','}
    
    return {'decimal': ',', 'thousands': '.'}  # Padrão seguro

def generate_alert(type, message):
    '''
    Configura e retorna os parâmetros do componente alert por Tipo(Sucess, Error, Info e Warning)
    '''
    if type=='sucess':
        color = 'bg-emerald-500'
    elif type=='error':
        color = 'bg-red-500'
    elif type=='info':
        color = 'bg-blue-500'
    elif type=='warning':
        color = 'bg-yellow-400'
    
    return {
        "type": type,
        "color": color,
        "message": message
        }

def validation_credit_operation(requisitado, rcl, realizado, limiteRegra2):
    '''
    Valida o valor requisitado de operação de crédito para a regra de ouro.
    Retorna feedback de erro caso o valor exceda e quais regras não foram cumpridas.
    '''
    try:
        operacoes_total = requisitado + realizado
        disponivel = rcl * 0.16

        violacoes = []

        if operacoes_total > limiteRegra2:
            violacoes.append('Regra 2: Operação excede o limite estabelecido pela Regra 2.')

        if operacoes_total > disponivel:
            violacoes.append('Regra 3: Operação excede 16% da Receita Corrente Líquida.')

        if not violacoes:
            resultado = 'Operação de crédito liberada!'
        else:
            resultado = 'Operação de crédito negada!'

        return {
            "resultado": resultado,
            "violacoes": violacoes
        }
    except Exception as e:
        return {
            "erro": f"Ocorreu um erro no tratamento dos dados! {e}"
        }, 400

def bar_data(requisitado, operacao, rcl, limiteOp):
    '''
    Função para calcular o limite final de operações e as porcentagens da largura que cada valor na barra gráfica representa.
    Formato de retorno:
        {
        "limite": 1000000,
        "largura_entrada": 45.67,
        "largura_calculado": 32.89
        }
    '''
    # Garantir que rcl e limiteOp são números válidos
    try:
        rcl = float(rcl)
        limiteOp = float(limiteOp)
        requisitado = float(requisitado)
        operacao = float(operacao)  
    except (ValueError, TypeError):
        return {"erro": "Valores inválidos para rcl ou limiteOp"}

    # Comparação de limites
    limite_rcl = 0.16 * rcl
    limite = max(min(limiteOp, limite_rcl), 1)  # Evita limite zero, coloca 1 como fallback mínimo

    # Variáveis de entrada do usuário e valor calculado no banco
    entrada_usuario = requisitado  # Supondo que vem da requisição
    valor_calculado = operacao     # Supondo que já foi calculado

    # Evita divisão por zero e calcula largura da barra (em %)
    largura_entrada = (entrada_usuario / limite * 100) if limite != 0 else 0
    largura_calculado = (valor_calculado / limite * 100) if limite != 0 else 1

    if largura_calculado < 1: largura_calculado = 1

    # Formata pra mandar pro front
    dados_barra = {
        "limite": limite,
        "largura_contratar": round(largura_entrada, 2),
        "largura_liberar": round(largura_calculado, 2)
    }
    
    return dados_barra

def calcular_bimestre_atual():
    """Calcula o bimestre atual (1 a 6) baseado no mês."""
    mes_atual = datetime.now().month
    return (mes_atual - 1) // 2 + 1

def calcula_quadrimestre_atual():
    mes_atual = datetime.now().month
    quadrimestre = math.ceil(mes_atual / 4)
    return quadrimestre