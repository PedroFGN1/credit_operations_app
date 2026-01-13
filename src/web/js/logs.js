// ======================================================================
// LÓGICA DO COMPONENTE DE LOGS
// ======================================================================

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