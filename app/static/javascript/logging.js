// Arquivo: log_component.js (versão Flask)

let logHistory = [];
let currentLogLevelFilter = 'all';

// Função para inicializar o componente
function initializeLogComponent() {
    // Conecta-se ao stream de logs do servidor
    const source = new EventSource('/log-stream');

    // Listener para novas mensagens do servidor
    source.onmessage = function(event) {
        const logEntry = JSON.parse(event.data);
        addLogMessage(logEntry);
    };

    source.onerror = function(event) {
        console.error("EventSource failed:", event);
        // Opcional: tentar reconectar ou mostrar um aviso na UI
    };

    // Listeners para os botões de controle
    document.getElementById('logFilter').addEventListener('change', (e) => {
        currentLogLevelFilter = e.target.value;
        filterLogs();
    });
    
    document.getElementById('clearLogsBtn').addEventListener('click', () => {
        fetch('/logs/clear', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                // O log de limpeza virá pelo stream SSE, então não precisamos fazer mais nada
            });
    });

    // Puxa o histórico de logs ao carregar a página
    fetch('/logs/history')
        .then(response => response.json())
        .then(logs => {
            logHistory = logs;
            filterLogs();
        });
}

function addLogMessage(logEntry) {
    logHistory.push(logEntry);
    if (currentLogLevelFilter === 'all' || currentLogLevelFilter === logEntry.level) {
        displayLogEntry(logEntry);
    }
}

function displayLogEntry(logEntry) {
    // (Esta função permanece idêntica à versão Eel)
    const logTerminal = document.getElementById('logTerminal');
    const welcome = logTerminal.querySelector('.log-welcome');
    if (welcome) welcome.remove();

    const logElement = document.createElement('div');
    logElement.className = 'log-entry';
    logElement.innerHTML = `
        <span class="log-timestamp">${logEntry.timestamp}</span>
        <div class="log-content">
            <span class="log-level ${logEntry.level}" style="color: ${logEntry.color};">${logEntry.level}</span>
            <span class="log-message ${logEntry.level}" style="color: ${logEntry.color};">${logEntry.message}</span>
            ${logEntry.details ? `<div class="log-details">${logEntry.details}</div>` : ''}
        </div>
    `;
    logTerminal.appendChild(logElement);
    logTerminal.scrollTop = logTerminal.scrollHeight;
}

function filterLogs() {
    // (Esta função permanece idêntica à versão Eel)
    const logTerminal = document.getElementById('logTerminal');
    logTerminal.innerHTML = '';
    
    const filtered = currentLogLevelFilter === 'all'
        ? logHistory
        : logHistory.filter(log => log.level === currentLogLevelFilter);

    if (filtered.length === 0) {
        logTerminal.innerHTML = `<div class="log-welcome"><p>Nenhum log para o filtro '${currentLogLevelFilter}'.</p></div>`;
    } else {
        filtered.forEach(displayLogEntry);
    }
}

// Inicializa o componente quando a página estiver pronta
document.addEventListener('DOMContentLoaded', initializeLogComponent);