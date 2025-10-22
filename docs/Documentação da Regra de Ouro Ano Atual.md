# Documentação da Regra de Ouro Ano Atual

Este documento detalha a regra de cálculo "Regra de Ouro Ano Atual" no sistema de `Simulador de Operações de Crédito`.

## 1. Visão Geral da Regra

### 1.1. Nome da Regra

Regra de Ouro Ano Atual (conforme `modelo.yaml` e classe `RegraDeOuroAnoAtual` em `src/simulador/rule_engine.py`).

### 1.2. Objetivo da Regra

A regra de ouro busca evitar o uso de recursos provenientes de operações de crédito para o pagamento de despesas correntes. Para isto, ela diz que as receitas de operação de crédito não podem ultrapassar as despesas de capital.

### 1.3. Base Normativa

Regra de ouro 167, Inciso III, da CF 88 + RSF 43/2001, Pag 78 do MIP.

## 2. Detalhamento da Lógica de Cálculo

### 2.1. Descrição da Lógica

A `RegraDeOuroAnoAtual` verifica a projeção da Regra de Ouro para o ano corrente. Ela compara o limite disponível (Despesas de Capital - Operações de Crédito) com o `valor_requisitado`. A regra é considerada aprovada se o `limite_disponivel` for maior ou igual ao `valor_requisitado`.

Os dados utilizados são do ano corrente (`self.ano`). As "Despesas de Capital" são calculadas somando os valores das colunas `'DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)'` e `'INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)'` para as contas `'AMORTIZAÇÃO DA DÍVIDA'`, `'INVERSÕES FINANCEIRAS'` e `'INVESTIMENTOS'`. As "Operações de Crédito" são calculadas somando os valores da coluna `'PREVISÃO ATUALIZADA (a)'` para a conta `'OPERAÇÕES DE CRÉDITO'`.

### 2.2. Parâmetros de Entrada

| Parâmetro           | Tipo    | Descrição                                                                 |
| :------------------ | :------ | :------------------------------------------------------------------------ |
| `ano`               | `int`   | Ano de referência para a análise (ano corrente).                          |
| `valor_requisitado` | `float` | Valor da operação de crédito que está sendo requisitada.                  |
| `dados_rreo`        | `dict`  | Dados do Relatório Resumido da Execução Orçamentária para o ano corrente. |
| `dados_rgf`         | `dict`  | Dados do Relatório de Gestão Fiscal (não utilizado diretamente nesta regra, mas passado para a classe base). |

### 2.3. Métodos Auxiliares de Cálculo (Classe da Regra)

A classe `RegraDeOuroAnoAtual` utiliza o método auxiliar `_calcular_e_detalhar_soma` para agregar os valores das despesas de capital e operações de crédito.

```python
def _calcular_e_detalhar_soma(registros: list, filtros_conta: list, filtros_coluna: list) -> tuple:
    """
    Função auxiliar que calcula a soma E detalha os componentes dessa soma.
    Itera sobre uma lista de registros de dados, filtrando-os por 'conta' e 'coluna',
    e soma os valores correspondentes. Retorna a soma total e um dicionário
    com os detalhes da soma por conta.
    Retorna uma tupla contendo: (soma_total, dicionario_com_detalhes)
    """
    # Implementação em src/simulador/rule_engine.py
```

### 2.4. Fluxo da Regra (Diagrama Simples)

[![](https://mermaid.ink/img/pako:eNp1kk1u2zAQha9CzKoBFEeWZVnWooUj2UmANgncIouUWbDi2CYgkQIlBW0NHybooquuegRdrKOfqJuWK3Lmfe_x7wipkQgR7K0oDuxTwjWjsfrM4UY3v1JlmBRs9SwyJZqfzY9uuUVSc3hi5-dv2eWRw92XCi1LhDQlu8UUy7J5scqU7zicesNL0jIOH1XOocNiSri3ptWKV_TNdru-c9j2anNG7j0Yd-qEQlZFplLSvm9-72nCJLK4ecnSOjNjTNLHxEZL1W93VVjzLKQYYtcU222fxXVeWNU2nv7HPiiT_UU3IzrWB3Ld9a-ov2nPN1Q3_6wOF3FL_oPvNSnW1hp2MVzDjS7rnUoV6grLEbzu7bgGhx5LSYh2IivRgRxtLto1HFslh-qAOXKIaCpxJ-qs4sD1ibhC6EdjcogqWxNpTb0_jD51IUWFiRJ0xHysWtQSbWxqXUE0D7zOBKIjfIXIm7kT1w-9YLn0Z4G_CEMHvkE08yZuQAU39OZzN1wEJwe-d7HuZDlbTsNwsQh91_W96dQBlKoy9kP_C7vPePoDq-PL8w?type=png)](https://mermaid.live/edit#pako:eNp1kk1u2zAQha9CzKoBFEeWZVnWooUj2UmANgncIouUWbDi2CYgkQIlBW0NHybooquuegRdrKOfqJuWK3Lmfe_x7wipkQgR7K0oDuxTwjWjsfrM4UY3v1JlmBRs9SwyJZqfzY9uuUVSc3hi5-dv2eWRw92XCi1LhDQlu8UUy7J5scqU7zicesNL0jIOH1XOocNiSri3ptWKV_TNdru-c9j2anNG7j0Yd-qEQlZFplLSvm9-72nCJLK4ecnSOjNjTNLHxEZL1W93VVjzLKQYYtcU222fxXVeWNU2nv7HPiiT_UU3IzrWB3Ld9a-ov2nPN1Q3_6wOF3FL_oPvNSnW1hp2MVzDjS7rnUoV6grLEbzu7bgGhx5LSYh2IivRgRxtLto1HFslh-qAOXKIaCpxJ-qs4sD1ibhC6EdjcogqWxNpTb0_jD51IUWFiRJ0xHysWtQSbWxqXUE0D7zOBKIjfIXIm7kT1w-9YLn0Z4G_CEMHvkE08yZuQAU39OZzN1wEJwe-d7HuZDlbTsNwsQh91_W96dQBlKoy9kP_C7vPePoDq-PL8w)

## 3. Impacto nas Camadas do Sistema

Esta seção detalha como a implementação ou modificação da regra afeta as diferentes camadas da arquitetura do sistema.

### 3.1. Camada de Apresentação (Frontend - `src/web/`)

- **Exibição de Resultados:** Os resultados formatados (`regras_cumpridas`, `regras_violadas`) da `Regra de Ouro Ano Atual` são apresentados ao usuário na interface, indicando se a regra foi cumprida ou violada, juntamente com os `dados_calculados` (limite disponível, valor requisitado na análise, despesas de capital e operações de crédito detalhadas).
- **Entrada de Dados:** A regra utiliza o `ano` e o `valor_requisitado` que são fornecidos pelo usuário através da interface principal (`main.html`) e passados via `eel.expose`.
- **Interações:** A avaliação desta regra é disparada quando o usuário solicita a análise de uma operação de crédito, chamando a função `analisar_operacao_py` no backend.

### 3.2. Camada de Aplicação (Backend - `app.py`)

- **Funções `eel.expose`:** A função `analisar_operacao_py(ano: int, valor_requisitado: float)` é o ponto de entrada exposto ao frontend que orquestra a avaliação da `Regra de Ouro Ano Atual`.
- **Orquestração:** Dentro de `analisar_operacao_py`, a função `analisar_operacao` (em `src/simulador/rule_engine.py`) é invocada. Esta, por sua vez, carrega o `modelo.yaml`, obtém os dados necessários e instancia a classe `RegraDeOuroAnoAtual` para avaliação.

### 3.3. Camada de Lógica de Negócio (Motor de Regras - `src/simulador/rule_engine.py`)

- **Nova Classe de Regra:** A regra é implementada na classe `RegraDeOuroAnoAtual(RegraDeNegocio)`, que herda da classe base `RegraDeNegocio`.
    - **Implementação de `avaliar()`:** O método `avaliar()` dentro desta classe contém a lógica específica para calcular as despesas de capital e as operações de crédito do ano corrente, e determinar se o `valor_requisitado` está dentro do `limite_disponivel`.
- **Registro da Regra:** A classe `RegraDeOuroAnoAtual` é adicionada ao dicionário `REGISTRY` (`"Regra_de_Ouro_Ano_Atual": RegraDeOuroAnoAtual`), permitindo que o orquestrador a encontre e instancie dinamicamente.
- **Funções Auxiliares:** Utiliza a função auxiliar `_calcular_e_detalhar_soma` para somar e detalhar os componentes das despesas de capital e operações de crédito.

### 3.4. Camada de Acesso a Dados (`src/simulador/data_access.py`, `src/simulador/database_models.py`)

- **Novas Consultas:** A regra depende da função `obter_dados_rreo_para_analise(ano_corrente: int)` em `src/simulador/data_access.py` para buscar os dados do RREO para o ano corrente. Não requer novas consultas específicas, mas utiliza a estrutura existente.
- **Modelos de Banco de Dados:** A regra interage com os dados armazenados na tabela `RREO`, conforme definido em `src/simulador/database_models.py`.

### 3.5. Camada de Configuração (`src/simulador/config.py`, `modelo.yaml`)

- **`modelo.yaml`:** A `Regra_de_Ouro_Ano_Atual` está definida neste arquivo, incluindo suas mensagens de `validacao` (true/false), `banco_de_dados` (`[SICONFI]`), `base_normativa` e `objetivo`.
- **`config.py`:** Não há alterações diretas necessárias neste arquivo para a `Regra de Ouro Ano Atual`, pois as configurações de banco de dados e caminhos de ativos já são gerenciadas.

## 4. Testes e Validação

- **Casos de Teste:**
    - Cenário 1: **Limite Suficiente**
        - Entrada: `ano = 2025`, `valor_requisitado = 50000.0`.
        - `dados_rreo` (ano 2025): Despesas de Capital (h+k) = 150.000,00; Operações de Crédito (a) = 80.000,00.
        - Lógica: `limite_disponivel` = 150.000 - 80.000 = 70.000. `70.000 >= 50.000` é `True`.
        - Saída Esperada: `aprovado = True`, `dados_calculados = {'limite_disponivel': 70000.0, 'valor_requisitado_na_analise': 50000.0, ...}`.
    - Cenário 2: **Limite Insuficiente**
        - Entrada: `ano = 2025`, `valor_requisitado = 100000.0`.
        - `dados_rreo` (ano 2025): Despesas de Capital (h+k) = 150.000,00; Operações de Crédito (a) = 80.000,00.
        - Lógica: `limite_disponivel` = 150.000 - 80.000 = 70.000. `70.000 >= 100.000` é `False`.
        - Saída Esperada: `aprovado = False`, `dados_calculados = {'limite_disponivel': 70000.0, 'valor_requisitado_na_analise': 100000.0, ...}`.
    - Cenário 3: **Dados Ausentes**
        - Entrada: `ano = 2026` (assumindo que não há dados para 2026).
        - Lógica: `dados_ano_corrente` vazio.
        - Saída Esperada: `aprovado = True`, `dados_calculados = {'mensagem': 'Sem dados para o ano corrente.'}` (comportamento atual da regra).

## 5. Considerações Adicionais

- A regra assume que os dados do RREO para o ano corrente estão disponíveis e são consistentes. A ausência de dados leva a uma aprovação padrão, o que pode ser um ponto a ser revisado para um tratamento de erro mais explícito.
- As colunas e contas utilizadas para o cálculo são fixas dentro da implementação da classe. Qualquer mudança na estrutura dos dados do SICONFI pode exigir atualização direta no código da regra.
- A regra `RegraDeOuroAnoAtual` é a segunda a ser avaliada na `Primeira_Etapa` do `modelo.yaml`, dependendo da aprovação da `Regra_de_Ouro_Ano_Anterior`.
