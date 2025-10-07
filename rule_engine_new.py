from datetime import datetime
# Importe as novas funções de acesso a dados
from data_access import (
    obter_dados_rreo_para_analise, 
    obter_dados_rgf_para_analise
)
from utils import validation_credit_operation, bar_data, calcula_quadrimestre_atual, calcular_bimestre_atual
from config import carregar_modelo_yaml


# --- CAMADA 2: MOTOR DE REGRAS ---

class RegraDeNegocio:
    """
    Classe base para todas as regras de negócio.
    Define um contrato que todas as regras devem seguir.
    """
    def __init__(self, ano, dados_rreo, dados_rgf, valor_requisitado=0.0):
        self.ano = ano
        self.dados_rreo = dados_rreo
        self.dados_rgf = dados_rgf
        self.valor_requisitado = valor_requisitado

    def avaliar(self):
        """
        Este método deve ser implementado por cada classe de regra filha.
        Ele executa o cálculo da regra e retorna um resultado padronizado.
        """
        raise NotImplementedError("O método 'avaliar' deve ser implementado na classe filha.")

class RegraDeOuroAnoAnterior(RegraDeNegocio):
    """
    Verifica se as operações de crédito do ano anterior foram maiores que as
    despesas de capital, conforme a Regra de Ouro.
    """
    def avaliar(self):
        # Usamos os dados do ano anterior, que já foram buscados
        ano_anterior = self.ano - 1
        dados_ano_anterior = self.dados_rreo.get(ano_anterior, {}).get('registros', [])
        
        if not dados_ano_anterior:
            # Se não há dados, não podemos avaliar. Pode ser uma aprovação padrão ou erro.
            return {'aprovado': True, 'dados_calculados': {'mensagem': 'Sem dados para o ano anterior.'}}

        # Define os filtros com base na lógica original
        colunas_despesa = ['DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)', 'INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)']
        contas_despesa_capital = ['AMORTIZAÇÃO DA DÍVIDA', 'INVERSÕES FINANCEIRAS', 'INVESTIMENTOS']
        
        colunas_operacao = ['Até o Bimestre (c)']
        contas_operacao_credito = ['OPERAÇÕES DE CRÉDITO']

        # Usa a função auxiliar para fazer os cálculos de forma limpa
        despesas_capital = _soma_valores(dados_ano_anterior, contas_despesa_capital, colunas_despesa)
        operacoes_credito = _soma_valores(dados_ano_anterior, contas_operacao_credito, colunas_operacao)

        # A lógica da regra
        limite_disponivel = despesas_capital - operacoes_credito
        aprovado = limite_disponivel >= 0
        
        # Retorna o resultado padronizado
        return {
            'aprovado': aprovado,
            'dados_calculados': {
                'despesas_capital': despesas_capital,
                'operacoes_credito': operacoes_credito,
                'limite_disponivel': limite_disponivel
            }
        }
    
def _soma_valores(registros: list, filtros_conta: list, filtros_coluna: list):
    """
    Função auxiliar para somar valores de uma lista de registros
    com base em filtros de conta e coluna.
    """
    soma = 0.0
    for reg in registros:
        if reg['conta'] in filtros_conta and reg['coluna'] in filtros_coluna:
            soma += reg['valor']
    return soma


def analisar_operacao(ano, valor_requisitado=0.0):
    """
    Orquestra a análise de uma operação de crédito.
    (Versão Refatorada)
    """
    try:
        if not ano:
            ano = datetime.now().year
        
        # --- CAMADA 1: ACESSO A DADOS ---
        # Buscamos todos os dados necessários de uma só vez no início.
        print("Buscando dados RREO...")
        dados_rreo = obter_dados_rreo_para_analise(ano)
        
        print("Buscando dados RGF...")
        dados_rgf = obter_dados_rgf_para_analise(ano)
        
        print("\n--- DADOS COLETADOS ---")
        print(f"Dados RREO para {ano}: {len(dados_rreo[ano]['registros'])} registros")
        print(f"Dados RREO para {ano-1}: {len(dados_rreo[ano-1]['registros'])} registros")
        print(f"Dados RGF para {ano}: {len(dados_rgf[ano]['registros'])} registros")
        print(f"Dados RGF para {ano-1}: {len(dados_rgf[ano-1]['registros'])} registros")
        print("-----------------------\n")

         # 2. CAMADA DE REGRAS: Instancia e avalia as regras
        print("--- AVALIANDO REGRAS ---")
        
        # Instancia a regra, passando os dados necessários
        regra_ouro_anterior = RegraDeOuroAnoAnterior(ano, dados_rreo, dados_rgf, valor_requisitado)
        
        # Avalia a regra
        resultado_regra = regra_ouro_anterior.avaliar()
        
        print("\nResultado da 'Regra de Ouro - Ano Anterior':")
        print(resultado_regra)
        print("--------------------------\n")
        
        # No futuro, faremos isso para todas as regras e usaremos o YAML para formatar o resultado
        
        return {"status": "Análise concluída com sucesso.", "resultado_teste": resultado_regra}

    except Exception as e:
        print(f"Erro na análise da operação: {e}")
        # Retorne uma estrutura de erro consistente
        return {"status": f"Erro: {e}", "dados_coletados": False}

# Configuração para rodar o script diretamente

from config import configurar_banco_dados, configurar_logging

logger = configurar_logging()

if __name__ == "__main__":
    if not configurar_banco_dados(logger):
        print("Falha na configuração do banco de dados.")
        exit(1)

    # Teste rápido
    resultado = analisar_operacao(2025, 50000.0)
    print(resultado)