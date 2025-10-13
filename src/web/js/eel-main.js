/**
 * JavaScript principal para comunicação com Eel e renderização da interface.
 * Simulador de Operações de Crédito v2 - Refatorado
 */

// --- INICIALIZAÇÃO ---

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado. Inicializando aplicação...');
    configurarEventListeners();
    carregarDadosIniciais();
    initializeLogComponent();
    // Garante que a seção de simulação seja exibida por padrão ao carregar
    mostrarSecao('secao-simulacao'); 
});

// --- LÓGICA DE NAVEGAÇÃO ENTRE SEÇÕES ---
function mostrarSecao(nomeSecao) {
    // Esconde todas as seções principais
    document.getElementById('secao-simulacao').classList.add('hidden');
    document.getElementById('secao-logs').classList.add('hidden');
    // Adicione outras seções aqui no futuro (ex: 'secao-configuracoes')

    // Remove a classe de 'ativo' de todos os links de navegação
    document.getElementById('nav-simulacao').classList.remove();
    document.getElementById('nav-logs').classList.remove();

    // Mostra a seção desejada
    const secaoParaMostrar = document.getElementById(nomeSecao);
    if (secaoParaMostrar) {
        secaoParaMostrar.classList.remove('hidden');
    }
    
    // Adiciona a classe de 'ativo' ao link de navegação clicado
    const navLinkAtivo = document.getElementById(`nav-${nomeSecao.split('-')[1]}`);
    if (navLinkAtivo) {
        navLinkAtivo.classList.add();
    }
}

// --- CONFIGURAÇÃO DE EVENTOS ---

function configurarEventListeners() {
    // Formulário principal de simulação
    document.getElementById('form-simulacao').addEventListener('submit', (e) => {
        e.preventDefault();
        executarSimulacao();
    });

    // Botão para atualizar dados da API Siconfi
    document.getElementById('btn-atualizar').addEventListener('click', atualizarDadosSiconfi);
    
    // Botões e eventos do modal de detalhes
    document.getElementById('btn-fechar-modal').addEventListener('click', esconderModal);
    document.getElementById('btn-fechar-modal-2').addEventListener('click', esconderModal);
    document.getElementById('modal-feedback').addEventListener('click', (e) => {
        if (e.target.id === 'modal-feedback') esconderModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') esconderModal();
    });

    // Adiciona os novos listeners para a navegação
    document.getElementById('nav-simulacao').addEventListener('click', (e) => {
        e.preventDefault();
        mostrarSecao('secao-simulacao');
    });

    document.getElementById('nav-logs').addEventListener('click', (e) => {
        e.preventDefault();
        mostrarSecao('secao-logs');
    });
}


// --- COMUNICAÇÃO COM O BACKEND (PYTHON/EEL) ---

async function carregarDadosIniciais() {
    console.log("Buscando dados iniciais do backend...");
    try {
        const resultado = await eel.obter_dados_iniciais()();
        if (resultado.status === 'sucesso') {
            popularSeletorDeAnos(resultado.anos_disponiveis);
            console.log("Anos disponíveis carregados:", resultado.anos_disponiveis);
        } else {
            throw new Error(resultado.mensagem);
        }
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
        mostrarMensagem('Falha ao carregar dados iniciais do servidor.', 'error');
    }
}

async function executarSimulacao() {
    const ano = parseInt(document.getElementById('ano').value);
    const valorRequisitado = parseFloat(document.getElementById('valor-requisitado').value) || 0;

    console.log(`Iniciando simulação para o ano ${ano} com valor ${valorRequisitado}`);
    mostrarCarregamento(true, 'form-simulacao');

    try {
        const resultado = await eel.analisar_operacao_py(ano, valorRequisitado)();
        console.log("Resultado da análise recebido:", resultado);

        if (resultado.status !== 'Análise completa.') {
            throw new Error(resultado.mensagem || 'Ocorreu um erro desconhecido na análise.');
        }
        
        // A nova função central de renderização
        renderizarResultados(resultado);
        mostrarMensagem('Análise concluída com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao executar simulação:', error);
        mostrarMensagem(`Erro na simulação: ${error.message}`, 'error');
    } finally {
        mostrarCarregamento(false, 'form-simulacao');
    }
}

async function atualizarDadosSiconfi() {
    console.log("Iniciando atualização de dados Siconfi...");
    mostrarCarregamento(true, 'btn-atualizar');
    mostrarMensagem('Atualizando dados RREO e RGF... Isso pode levar um momento.', 'info');
    
    try {
        // Executa as duas atualizações em paralelo para agilizar
        const [resRREO, resRGF] = await Promise.all([
            eel.atualizar_rreo_py('now')(),
            eel.atualizar_rgf_py('now')()
        ]);

        const [resRREO2, resRGF2] = await Promise.all([
            eel.atualizar_rreo_py('all')(),
            eel.atualizar_rgf_py('all')()
        ]);

        console.log("Resultado da atualização RREO atual:", resRREO);
        console.log("Resultado da atualização RGF atual:", resRGF);
        console.log("Resultado da atualização RREO anterior:", resRREO2);
        console.log("Resultado da atualização RGF anterior:", resRGF2);

        if (resRREO.status === 'error' || resRGF.status === 'error') {
            throw new Error('Uma ou mais atualizações falharam. Verifique o console.');
        }

        mostrarMensagem('Dados atualizados com sucesso! A lista de anos será recarregada.', 'success');
        // Recarrega os anos disponíveis, pois novos dados podem ter sido adicionados
        await carregarDadosIniciais();

    } catch (error) {
        console.error('Erro ao atualizar dados Siconfi:', error);
        mostrarMensagem(`Erro na atualização: ${error.message}`, 'error');
    } finally {
        mostrarCarregamento(false, 'btn-atualizar');
    }
}


// --- RENDERIZAÇÃO DA INTERFACE (UI) ---

function popularSeletorDeAnos(anos) {
    const selectAno = document.getElementById('ano');
    selectAno.innerHTML = ''; // Limpa opções antigas
    const anoCorrente = new Date().getFullYear();

    anos.forEach(ano => {
        const option = document.createElement('option');
        option.value = ano;
        option.textContent = ano;
        if (ano === anoCorrente) {
            option.selected = true;
        }
        selectAno.appendChild(option);
    });
}

function renderizarResultados(resultado) {
    const container = document.getElementById('tabela-resultados-container'); // Você precisará criar este container no HTML
    const tbody = document.getElementById('tbody-resultados'); // E este tbody
    
    tbody.innerHTML = ''; // Limpa resultados anteriores
    
    const todasAsRegras = [
        ...(resultado.regras_violadas || []),
        ...(resultado.regras_cumpridas || [])
    ];

    if (todasAsRegras.length === 0) {
        container.style.display = 'none';
        return;
    }

    todasAsRegras.forEach(regra => {
        const tr = document.createElement('tr');
        
        const statusClasse = regra.status === 'Cumprida' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800';

        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${regra.nome}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClasse}">
                    ${regra.status}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-normal text-sm text-gray-500">${regra.descricao}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button class="text-blue-600 hover:text-blue-900 ver-detalhes-btn">Ver Detalhes</button>
            </td>
        `;

        // Adiciona o listener no botão para mostrar o modal com os dados da regra específica
        tr.querySelector('.ver-detalhes-btn').addEventListener('click', () => mostrarDetalhesRegra(regra));
        
        tbody.appendChild(tr);
    });

    container.style.display = 'block'; // Mostra a tabela de resultados
}


function mostrarDetalhesRegra(regra) {
    // Popula o modal com os dados detalhados da regra
    document.getElementById('modal-title').textContent = regra.nome;
    document.getElementById('modal-status').textContent = regra.status;
    document.getElementById('modal-status').className = `font-semibold ${regra.status === 'Cumprida' ? 'text-green-600' : 'text-red-600'}`;
    
    document.getElementById('modal-descricao').textContent = regra.descricao;
    document.getElementById('modal-proximo-passo').textContent = regra.proximo_passo;
    document.getElementById('modal-base-normativa').textContent = regra.base_normativa;
    document.getElementById('modal-objetivo').textContent = regra.objetivo;
    
    // Constrói a visualização dos dados calculados
    const calculadosContainer = document.getElementById('modal-dados-calculados');
    calculadosContainer.innerHTML = ''; // Limpa
    
    if (regra.dados_calculados) {
        for (const [key, value] of Object.entries(regra.dados_calculados)) {
            const div = document.createElement('div');
            div.className = 'py-2';
            
            let content = `<dt class="font-medium text-gray-900">${key.replace(/_/g, ' ')}</dt>`;
            
            if (typeof value === 'object' && value !== null && value.total !== undefined) {
                content += `<dd class="text-gray-700"><strong>Total: ${formatarMoeda(value.total)}</strong></dd>`;
                if(value.detalhe){
                    const detalhesList = Object.entries(value.detalhe)
                        .map(([detalheKey, detalheValue]) => `<li class="ml-4 text-sm">${detalheKey}: ${formatarMoeda(detalheValue)}</li>`)
                        .join('');
                    content += `<ul class="list-disc list-inside">${detalhesList}</ul>`;
                }
            } else {
                content += `<dd class="text-gray-700">${formatarMoeda(value)}</dd>`;
            }
            div.innerHTML = content;
            calculadosContainer.appendChild(div);
        }
    }

    // Mostra o modal
    document.getElementById('modal-feedback').classList.remove('hidden');
}


function esconderModal() {
    document.getElementById('modal-feedback').classList.add('hidden');
}


// --- FUNÇÕES UTILITÁRIAS ---

function formatarMoeda(valor) {
    if (valor === null || valor === undefined || isNaN(valor)) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}

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

function obterClasseTipo(tipo) {
    const classes = {
        'success': 'bg-green-500 text-white',
        'error': 'bg-red-500 text-white',
        'warning': 'bg-yellow-500 text-white',
        'info': 'bg-blue-500 text-white'
    };
    
    return classes[tipo] || classes['info'];
}

function mostrarCarregamento(mostrar, elementoId) {
    const elemento = document.getElementById(elementoId);
    let botao;

    if (elemento.tagName === 'BUTTON') {
        botao = elemento;
    } else {
        botao = elemento.querySelector('button[type="submit"]');
    }

    if (!botao) return;

    if (mostrar) {
        botao.disabled = true;
        botao.dataset.originalText = botao.innerHTML; // Salva o texto original
        botao.innerHTML = `<span class="relative px-5 py-2.5 transition-all ease-in duration-75 bg-white hover:text-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">
                               <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Carregando... </span>`;
    } else {
        botao.disabled = false;
        botao.innerHTML = botao.dataset.originalText; // Restaura o texto original
    }
}



// ----------------------- LÓGICA DO COMPONENTE DE LOGS ------------------------

let logHistory = [];
let currentLogLevelFilter = 'all';

function initializeLogComponent() {
    console.log("Inicializando componente de logs...");
    // Adiciona os listeners aos botões e filtro
    document.getElementById('logFilter').addEventListener('change', (e) => {
        currentLogLevelFilter = e.target.value;
        filterLogs();
    });
    document.getElementById('clearLogsBtn').addEventListener('click', () => eel.clear_logs());

    // Pede ao backend os logs antigos caso a página seja recarregada
    eel.get_all_logs()((logs) => {
        logHistory = logs;
        filterLogs();
    });
}

// Exposto ao Python: recebe uma nova mensagem de log
eel.expose(add_log_message);
function add_log_message(logEntry) {
    logHistory.push(logEntry);
    if (currentLogLevelFilter === 'all' || currentLogLevelFilter === logEntry.level) {
        displayLogEntry(logEntry);
    }
}

// Exposto ao Python: limpa o terminal no frontend
eel.expose(clear_logs_frontend);
function clear_logs_frontend() {
    logHistory = [];
    document.getElementById('logTerminal').innerHTML = `
        <div class="log-welcome flex items-center justify-center h-full">
            <p class="text-gray-400">Terminal limpo. Aguardando novas mensagens.</p>
        </div>
    `;
}

// Função interna para renderizar um log na tela
function displayLogEntry(logEntry) {
    const logTerminal = document.getElementById('logTerminal');
    const welcome = logTerminal.querySelector('.log-welcome');
    if (welcome) welcome.remove();

    const logElement = document.createElement('div');
    logElement.className = 'log-entry mb-2 flex';
    // Usando cores do Tailwind para consistência
    const levelColorClass = {
        'DEBUG': 'text-gray-500', 'INFO': 'text-blue-400', 'SUCCESS': 'text-green-400',
        'WARNING': 'text-yellow-400', 'ERROR': 'text-red-400', 'CRITICAL': 'text-purple-400'
    };

    logElement.innerHTML = `
        <span class="timestamp text-gray-600 mr-4">${logEntry.timestamp}</span>
        <span class="level font-bold w-20 ${levelColorClass[logEntry.level] || 'text-gray-400'}">${logEntry.level}</span>
        <div class="message flex-1">
            <p>${logEntry.message}</p>
            ${logEntry.details ? `<p class="text-gray-500 text-xs mt-1">${logEntry.details}</p>` : ''}
        </div>
    `;
    logTerminal.appendChild(logElement);
    logTerminal.scrollTop = logTerminal.scrollHeight; // Auto-scroll
}

// Função interna para (re)aplicar o filtro de logs
function filterLogs() {
    const logTerminal = document.getElementById('logTerminal');
    logTerminal.innerHTML = ''; 
    
    const filtered = currentLogLevelFilter === 'all'
        ? logHistory
        : logHistory.filter(log => log.level === currentLogLevelFilter);

    if (filtered.length === 0) {
        logTerminal.innerHTML = `<div class="log-welcome flex items-center justify-center h-full"><p class="text-gray-400">Nenhum log para o filtro '${currentLogLevelFilter}'.</p></div>`;
    } else {
        filtered.forEach(displayLogEntry);
    }
}