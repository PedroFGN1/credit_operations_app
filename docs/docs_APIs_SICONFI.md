# Objetivo do Processo

Resgatar dados financeiros (RREO e RGF) da API do Siconfi, processá-los de forma eficiente e inserir apenas os registros novos em um banco de dados local, evitando duplicidade e garantindo a integridade dos dados.

---

## Etapa 1: Resgate dos Dados Brutos

*   **Ação:** O script constrói uma URL de requisição para a API Siconfi, com os parâmetros (`an_exercicio`, `id_ente`, etc.) em uma ordem específica para garantir a compatibilidade com a API.
*   **Processo:** Uma chamada `GET` é feita, e a resposta esperada é um JSON. O script extrai a lista de registros contida na chave `"items"`.
*   **Resultado:** Uma lista de dicionários, onde cada dicionário representa um registro completo, com todas as colunas e dados brutos fornecidos pela API.

---

## Etapa 2: Filtragem Inicial

*   **Ação:** Uma limpeza inicial é realizada para remover registros que não representam dados primários, como linhas de totais ou saldos calculados.
*   **Processo:** O script verifica o valor da coluna `"coluna"` de cada registro. Se o valor começar com um termo pré-definido (ex: `'%'`, `'SALDO'`), o registro inteiro é descartado.
*   **Resultado:** A mesma lista de dicionários da etapa anterior, porém contendo apenas os registros de dados relevantes.

---

## Etapa 3: Criação das Chaves Únicas (A "Impressão Digital")

*   **Ação:** Transformar cada registro de dados em uma "impressão digital" única e compacta para permitir uma verificação de existência rápida e precisa.
*   **Processo:**
    1.  O script divide a lista de registros filtrados em lotes (ex: de 50 em 50) para processamento.
    2.  Para cada registro (dicionário) em um lote, ele extrai os valores de um conjunto pré-definido de colunas que, juntas, garantem a unicidade do registro.
        *   **Colunas da Chave (Exemplo RREO):** `exercicio`, `periodo`, `instituicao`, `anexo`, `rotulo`, `coluna`, `conta`.
    3.  Esses valores são agrupados em uma tupla (ex: `(2025, 5, ..., 'Receita Tributária')`).
*   **Resultado:** Para cada lote, o script gera um conjunto (`set`) de tuplas. Cada tupla é a chave única de um registro da API.

---

## Etapa 4: Consulta de Existência no Banco de Dados

*   **Ação:** Perguntar ao banco de dados, de forma otimizada, quais das chaves geradas na etapa anterior já existem na tabela.
*   **Processo:**
    1.  O script constrói uma única consulta SQL por lote, combinando as chaves com `OR`.
    2.  A consulta é cuidadosamente montada para lidar com valores `NULL` (`IS NULL`) e valores normais (`=`), garantindo precisão.
    3.  A consulta é executada, retornando todos os registros do banco que correspondem a qualquer uma das chaves do lote.
*   **Resultado:** Uma lista de objetos SQLAlchemy, representando as linhas completas do banco de dados que já existem.

---

## Etapa 5: Reconciliação e Identificação de Novos Registros

*   **Ação:** Comparar as chaves da API com as chaves encontradas no banco para determinar quais registros são genuinamente novos.
*   **Processo:**
    1.  As chaves dos registros retornados pelo banco são extraídas e colocadas em um `set` para comparação ultra-rápida.
    2.  O script percorre os registros originais do lote da API e verifica se a sua chave existe no conjunto de chaves do banco.
    3.  Se a chave de um registro da API não for encontrada, o registro completo (dicionário) é adicionado a uma lista de "novos registros para inserir".
*   **Resultado:** Uma lista contendo apenas os dicionários dos registros que precisam ser salvos no banco de dados.

---

## Etapa 6: Inserção em Massa no Banco de Dados

*   **Ação:** Salvar os novos registros identificados de forma segura e eficiente.
*   **Processo:**
    1.  Se houver registros na lista de "novos registros", o script utiliza o método `bulk_insert_mappings` do SQLAlchemy.
    2.  Este método agrupa todos os novos registros em uma única transação `INSERT`, o que é muito mais performático do que inserir um por um.
    3.  Se a operação for bem-sucedida, a transação é confirmada com `commit()`.
    4.  Se qualquer erro ocorrer, a transação é revertida com `rollback()`, garantindo a integridade e consistência do banco de dados.
*   **Resultado:** Os novos dados são salvos de forma permanente na tabela, e o processo continua para o próximo lote até que todos os dados tenham sido processados.

---
