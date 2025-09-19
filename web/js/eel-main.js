/**
 * JavaScript principal para comunicação com Eel
 * Simulador de Operações de Crédito v2
 */

// Variáveis globais
let dadosSimulacao = {};
let anoAtual = new Date().getFullYear();

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando aplicação Eel...');
    
    // Inicializar componentes
    inicializarFormularios();
    carregarAnosDisponiveis();
    carregarDadosIniciais();
    
    // Event listeners
    configurarEventListeners();
});

/**
 * Inicializa os formulários da aplicação
 */
function inicializarFormularios() {
    // Configurar ano padrão
    const selectAno = document.getElementById('ano');
    if (selectAno) {
        // Preencher anos de 2015 a 2030
        for (let ano = 2015; ano <= 2030; ano++) {
            const option = document.createElement('option');
            option.value = ano;
            option.textContent = ano;
            if (ano === anoAtual) {
                option.selected = true;
            }
            selectAno.appendChild(option);
        }
    }
}

/**
 * Carrega os anos disponíveis no sistema
 */
async function carregarAnosDisponiveis() {
    try {
        // Os anos já são carregados na inicialização
        console.log('Anos disponíveis carregados');
    } catch (error) {
        console.error('Erro ao carregar anos:', error);
        mostrarMensagem('Erro ao carregar anos disponíveis', 'error');
    }
}

/**
 * Carrega dados iniciais da aplicação
 */
async function carregarDadosIniciais() {
    try {
        // Carregar informações da aplicação
        const infoApp = await eel.obter_info_app()();
        console.log('Aplicação:', infoApp);
        
        // Carregar dados RREO e RGF do ano atual
        await carregarDadosRREO(anoAtual);
        await carregarDadosRGF(anoAtual);
        
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
        mostrarMensagem('Erro ao carregar dados iniciais', 'error');
    }
}

/**
 * Configura os event listeners dos elementos
 */
function configurarEventListeners() {
    // Formulário de simulação
    const formSimulacao = document.getElementById('form-simulacao');
    if (formSimulacao) {
        formSimulacao.addEventListener('submit', async function(e) {
            e.preventDefault();
            await executarSimulacao();
        });
    }
    
    // Botão de atualizar dados
    const btnAtualizar = document.getElementById('btn-atualizar');
    if (btnAtualizar) {
        btnAtualizar.addEventListener('click', async function() {
            await atualizarDados();
        });
    }
    
    // Formulário de upload
    const formUpload = document.getElementById('form-upload');
    if (formUpload) {
        formUpload.addEventListener('submit', async function(e) {
            e.preventDefault();
            await importarCSV();
        });
    }
    
    // Mudança de ano
    const selectAno = document.getElementById('ano');
    if (selectAno) {
        selectAno.addEventListener('change', async function() {
            const ano = parseInt(this.value);
            await carregarDadosRREO(ano);
            await carregarDadosRGF(ano);
        });
    }
}

/**
 * Executa a simulação de operação de crédito
 */
async function executarSimulacao() {
    try {
        mostrarCarregamento(true);
        
        const ano = parseInt(document.getElementById('ano').value);
        const valorRequisitado = parseFloat(document.getElementById('valor-requisitado').value) || 0;
        
        console.log(`Executando simulação - Ano: ${ano}, Valor: ${valorRequisitado}`);
        
        // Chamar função Python via Eel
        const resultado = await eel.analisar_operacao_py(ano, valorRequisitado)();
        
        if (resultado.erro) {
            throw new Error(resultado.erro);
        }
        
        // Armazenar dados da simulação
        dadosSimulacao = resultado;
        
        // Atualizar interface
        atualizarTabelaRegras(resultado.tabela);
        atualizarValoresRCL(resultado);
        atualizarBarraProgresso(resultado);
        
        mostrarMensagem('Simulação executada com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro na simulação:', error);
        mostrarMensagem(`Erro na simulação: ${error.message}`, 'error');
    } finally {
        mostrarCarregamento(false);
    }
}

/**
 * Atualiza a tabela de regras com os resultados
 */
function atualizarTabelaRegras(tabela) {
    const tbody = document.getElementById('tbody-regras');
    if (!tbody || !tabela) return;
    
    tbody.innerHTML = '';
    
    tabela.forEach(regra => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${regra.regra}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatarMoeda(regra.amortizacao)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatarMoeda(regra.inversao)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatarMoeda(regra.investimento)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatarMoeda(regra.operacao_credito)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatarMoeda(regra.limiteOp)}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${regra.bg === 'bg-red-500' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
                    ${regra.situacao}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * Atualiza os valores de RCL na interface
 */
function atualizarValoresRCL(dados) {
    const elementoRCL = document.getElementById('valor-rcl');
    const elementoRCLRGF = document.getElementById('valor-rcl-rgf');
    const elementoDCLRGF = document.getElementById('valor-dcl-rgf');
    
    if (elementoRCL) elementoRCL.textContent = formatarMoeda(dados.rcl);
    if (elementoRCLRGF) elementoRCLRGF.textContent = formatarMoeda(dados.rcl_rgf);
    if (elementoDCLRGF) elementoDCLRGF.textContent = formatarMoeda(dados.dcl_rgf);
}

/**
 * Atualiza a barra de progresso
 */
function atualizarBarraProgresso(dados) {
    const barraProgresso = document.getElementById('barra-progresso');
    if (!barraProgresso || !dados.dados_barra) return;
    
    barraProgresso.classList.remove('hidden');
    
    // Atualizar elementos da barra
    const elementoRequisitado = document.getElementById('barra-requisitado');
    const elementoOperacao = document.getElementById('barra-operacao');
    const elementoRCL = document.getElementById('barra-rcl');
    const elementoLimite = document.getElementById('barra-limite');
    
    if (elementoRequisitado) elementoRequisitado.textContent = formatarMoeda(dados.requisitado);
    if (elementoOperacao) elementoOperacao.textContent = formatarMoeda(dados.dados_barra.operacao || 0);
    if (elementoRCL) elementoRCL.textContent = formatarMoeda(dados.rcl);
    if (elementoLimite) elementoLimite.textContent = formatarMoeda(dados.dados_barra.limite || 0);
    
    // Calcular e atualizar porcentagem da barra
    const porcentagem = calcularPorcentagemBarra(dados);
    const barraPreenchimento = document.getElementById('barra-preenchimento');
    if (barraPreenchimento) {
        barraPreenchimento.style.width = `${porcentagem}%`;
    }
}

/**
 * Calcula a porcentagem para a barra de progresso
 */
function calcularPorcentagemBarra(dados) {
    if (!dados.dados_barra || !dados.rcl) return 0;
    
    const total = dados.requisitado + (dados.dados_barra.operacao || 0);
    const limite = dados.rcl * 0.16; // 16% da RCL como exemplo
    
    return Math.min((total / limite) * 100, 100);
}

/**
 * Carrega dados RREO para um ano específico
 */
async function carregarDadosRREO(ano) {
    try {
        const dados = await eel.obter_dados_rreo_py(ano)();
        
        if (dados.erro) {
            throw new Error(dados.erro);
        }
        
        atualizarTabelaRREO(dados.data);
        
    } catch (error) {
        console.error('Erro ao carregar dados RREO:', error);
        mostrarMensagem(`Erro ao carregar dados RREO: ${error.message}`, 'error');
    }
}

/**
 * Carrega dados RGF para um ano específico
 */
async function carregarDadosRGF(ano) {
    try {
        const dados = await eel.obter_dados_rgf_py(ano)();
        
        if (dados.erro) {
            throw new Error(dados.erro);
        }
        
        atualizarTabelaRGF(dados.data);
        
    } catch (error) {
        console.error('Erro ao carregar dados RGF:', error);
        mostrarMensagem(`Erro ao carregar dados RGF: ${error.message}`, 'error');
    }
}

/**
 * Atualiza a tabela RREO
 */
function atualizarTabelaRREO(dados) {
    const tbody = document.getElementById('tbody-rreo');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    // Limitar a 10 registros para não sobrecarregar a interface
    const dadosLimitados = dados.slice(0, 10);
    
    dadosLimitados.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-4 py-2 text-sm text-gray-900">${item.exercicio}</td>
            <td class="px-4 py-2 text-sm text-gray-500">${item.periodo}</td>
            <td class="px-4 py-2 text-sm text-gray-500" title="${item.conta}">${item.conta.substring(0, 30)}...</td>
            <td class="px-4 py-2 text-sm text-gray-500">${item.valor}</td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * Atualiza a tabela RGF
 */
function atualizarTabelaRGF(dados) {
    const tbody = document.getElementById('tbody-rgf');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    // Limitar a 10 registros para não sobrecarregar a interface
    const dadosLimitados = dados.slice(0, 10);
    
    dadosLimitados.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-4 py-2 text-sm text-gray-900">${item.exercicio}</td>
            <td class="px-4 py-2 text-sm text-gray-500">${item.periodo}</td>
            <td class="px-4 py-2 text-sm text-gray-500" title="${item.conta}">${item.conta.substring(0, 30)}...</td>
            <td class="px-4 py-2 text-sm text-gray-500">${item.valor}</td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * Atualiza os dados via API
 */
async function atualizarDados() {
    try {
        mostrarCarregamento(true);
        mostrarMensagem('Atualizando dados via API...', 'info');
        
        // Atualizar RREO
        const resultadoRREO = await eel.atualizar_rreo_py('now')();
        console.log('Resultado RREO:', resultadoRREO);
        
        // Atualizar RGF
        const resultadoRGF = await eel.atualizar_rgf_py('now')();
        console.log('Resultado RGF:', resultadoRGF);
        
        // Recarregar dados na interface
        const ano = parseInt(document.getElementById('ano').value);
        await carregarDadosRREO(ano);
        await carregarDadosRGF(ano);
        
        mostrarMensagem('Dados atualizados com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao atualizar dados:', error);
        mostrarMensagem(`Erro ao atualizar dados: ${error.message}`, 'error');
    } finally {
        mostrarCarregamento(false);
    }
}

/**
 * Importa dados de arquivo CSV
 */
async function importarCSV() {
    try {
        const arquivoInput = document.getElementById('arquivo-csv');
        const arquivo = arquivoInput.files[0];
        
        if (!arquivo) {
            mostrarMensagem('Selecione um arquivo CSV', 'warning');
            return;
        }
        
        mostrarCarregamento(true);
        mostrarMensagem('Importando arquivo CSV...', 'info');
        
        // Nota: Para upload de arquivos com Eel, seria necessário implementar
        // uma lógica mais complexa. Por enquanto, mostrar mensagem informativa.
        mostrarMensagem('Funcionalidade de upload em desenvolvimento', 'info');
        
    } catch (error) {
        console.error('Erro ao importar CSV:', error);
        mostrarMensagem(`Erro ao importar CSV: ${error.message}`, 'error');
    } finally {
        mostrarCarregamento(false);
    }
}

/**
 * Formata um valor como moeda brasileira
 */
function formatarMoeda(valor) {
    if (valor === null || valor === undefined || isNaN(valor)) {
        return 'R$ 0,00';
    }
    
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

/**
 * Mostra/oculta indicador de carregamento
 */
function mostrarCarregamento(mostrar) {
    // Implementar indicador de carregamento visual
    const botoes = document.querySelectorAll('button[type="submit"]');
    botoes.forEach(botao => {
        if (mostrar) {
            botao.disabled = true;
            botao.textContent = 'Carregando...';
        } else {
            botao.disabled = false;
            // Restaurar texto original baseado no contexto
            if (botao.closest('#form-simulacao')) {
                botao.textContent = 'Simular Operação';
            } else if (botao.closest('#form-upload')) {
                botao.textContent = 'Importar CSV';
            }
        }
    });
}

/**
 * Mostra mensagem para o usuário
 */
function mostrarMensagem(mensagem, tipo = 'info') {
    // Criar elemento de notificação
    const notificacao = document.createElement('div');
    notificacao.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${obterClasseTipo(tipo)}`;
    notificacao.textContent = mensagem;
    
    document.body.appendChild(notificacao);
    
    // Remover após 5 segundos
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.parentNode.removeChild(notificacao);
        }
    }, 5000);
}

/**
 * Obtém a classe CSS baseada no tipo de mensagem
 */
function obterClasseTipo(tipo) {
    const classes = {
        'success': 'bg-green-500 text-white',
        'error': 'bg-red-500 text-white',
        'warning': 'bg-yellow-500 text-white',
        'info': 'bg-blue-500 text-white'
    };
    
    return classes[tipo] || classes['info'];
}
